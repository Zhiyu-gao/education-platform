import os
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from datetime import datetime

import dashscope
import pandas as pd
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from sklearn.feature_extraction.text import HashingVectorizer

from database import Base, SessionLocal, engine
from models import RagDataset

# 创建数据库表（如果不存在）
Base.metadata.create_all(bind=engine)

QDRANT_PATH = "./qdrant_db"
QDRANT_COLLECTION = "excel_data"
VECTOR_SIZE = 384

qdrant_client = QdrantClient(path=QDRANT_PATH)
vectorizer = HashingVectorizer(
    n_features=VECTOR_SIZE,
    alternate_sign=False,
    norm="l2",
    analyzer="char",
    ngram_range=(2, 4),
)


def _ensure_qdrant_collection():
    try:
        qdrant_client.get_collection(QDRANT_COLLECTION)
    except Exception:
        qdrant_client.create_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=qmodels.VectorParams(size=VECTOR_SIZE, distance=qmodels.Distance.COSINE),
        )


def _embed_texts(texts):
    if not texts:
        return []
    matrix = vectorizer.transform(texts)
    return matrix.toarray().tolist()


_ensure_qdrant_collection()

# 从环境变量读取通义千问API密钥（未配置时自动降级为本地模式）
dashscope.api_key = os.getenv("DASHSCOPE_API_KEY", "").strip()


class RAGService:
    SCORE_THRESHOLD = 0.58
    @staticmethod
    def _build_point_id(dataset_id, row_index):
        return int(dataset_id) * 1_000_000 + int(row_index)

    @staticmethod
    def _split_text_content(raw_text, chunk_size=500):
        content = (raw_text or "").strip()
        if not content:
            return []
        chunks = []
        buffer = []
        current_len = 0
        for line in content.splitlines():
            line = line.strip()
            if not line:
                continue
            if current_len + len(line) + 1 > chunk_size and buffer:
                chunks.append("\n".join(buffer))
                buffer = [line]
                current_len = len(line)
            else:
                buffer.append(line)
                current_len += len(line) + 1
        if buffer:
            chunks.append("\n".join(buffer))
        return chunks

    @staticmethod
    def _extract_texts_from_file(file_path):
        ext = os.path.splitext(file_path)[1].lower()
        if ext in [".xlsx", ".xls"]:
            df = pd.read_excel(file_path)
            texts = []
            for _, row in df.iterrows():
                text = ", ".join([f"{col}：{row[col]}" for col in df.columns])
                texts.append(text)
            return texts, "excel"
        if ext == ".txt":
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                raw_text = f.read()
            return RAGService._split_text_content(raw_text), "txt"
        raise ValueError("仅支持 .xlsx / .xls / .txt 文件")

    @staticmethod
    def process_file(file_path):
        """解析文件并存入Qdrant和MySQL数据库（支持Excel/TXT）"""
        texts, file_type = RAGService._extract_texts_from_file(file_path)
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path) / 1024  # KB

        db = SessionLocal()
        try:
            dataset = RagDataset(
                file_name=file_name,
                file_path=file_path,
                upload_time=datetime.now(),
                file_size=file_size,
                is_deleted="0",
            )
            db.add(dataset)
            db.commit()
            db.refresh(dataset)
            dataset_id = dataset.id
        except Exception as e:
            db.rollback()
            return f"数据库记录失败：{str(e)}"
        finally:
            db.close()

        try:
            vectors = _embed_texts(texts)
            points = []
            for idx, (text, vector) in enumerate(zip(texts, vectors)):
                points.append(
                    qmodels.PointStruct(
                        id=RAGService._build_point_id(dataset_id, idx),
                        vector=vector,
                        payload={
                            "dataset_id": dataset_id,
                            "row_index": idx,
                            "file_name": file_name,
                            "text": text,
                        },
                    )
                )
            if points:
                qdrant_client.upsert(collection_name=QDRANT_COLLECTION, points=points, wait=True)
            return f"成功导入 {len(texts)} 条{file_type}数据，数据集ID：{dataset_id}"
        except Exception as e:
            db2 = SessionLocal()
            try:
                rollback_dataset = db2.query(RagDataset).filter(RagDataset.id == dataset_id).first()
                if rollback_dataset:
                    rollback_dataset.is_deleted = "1"
                    db2.commit()
            finally:
                db2.close()
            return f"向量写入失败（数据集ID：{dataset_id}）：{str(e)}"

    @staticmethod
    def process_excel(file_path):
        """兼容旧接口，内部统一走 process_file"""
        return RAGService.process_file(file_path)

    @staticmethod
    def _local_fallback_answer(context):
        preview = context[:1200] if context else "未检索到相关知识。"
        return f"当前未启用在线大模型，以下是本地知识库检索结果：\n{preview}"

    @staticmethod
    def _local_general_answer(question):
        q = (question or "").strip()
        if any(x in q for x in ["你好", "您好", "hi", "hello"]):
            return "你好，我是教育平台 AI 助手。你可以问我学习规划、作业建议、考试复盘和成绩提升。"
        if "作业" in q:
            return "作业建议：先做基础题，再做提升题；每道错题记录“错因+改法”，第二天复做一次。"
        if "考试" in q or "复习" in q:
            return "考试复习建议：先梳理考点清单，再按薄弱点分配时间，最后做1-2套限时模拟并复盘错题。"
        if "成绩" in q or "提高" in q:
            return "提分建议：固定每天学习时段，先补薄弱科目；每周做一次错题复盘并跟踪正确率变化。"
        return "当前未连接在线大模型。你可以继续提问，我会按教育场景给你结构化建议。"

    @staticmethod
    def _call_qwen(messages, timeout=15):
        def call_qwen():
            return dashscope.Generation.call(model="qwen-turbo", messages=messages)

        with ThreadPoolExecutor(max_workers=1) as executor:
            response = executor.submit(call_qwen).result(timeout=timeout)
        if getattr(response, "status_code", None) == 200:
            return (response.output.get("text", "") or "").strip()
        return ""

    @staticmethod
    def _chat_without_knowledge(question):
        if not dashscope.api_key:
            return RAGService._local_general_answer(question)
        try:
            answer = RAGService._call_qwen(
                [
                    {"role": "system", "content": "你是教育场景的AI助手，请直接、清晰回答用户问题。"},
                    {"role": "user", "content": question},
                ]
            )
            return answer or RAGService._local_general_answer(question)
        except TimeoutError:
            return RAGService._local_general_answer(question)
        except Exception as e:
            return f"{RAGService._local_general_answer(question)}\n（在线模型调用异常：{str(e)}）"

    @staticmethod
    def query_answer(question):
        db = SessionLocal()
        try:
            active_ids = [item.id for item in db.query(RagDataset.id).filter(RagDataset.is_deleted == "0").all()]
        finally:
            db.close()

        if not active_ids:
            return RAGService._chat_without_knowledge(question)

        try:
            query_vec = _embed_texts([question])[0]
            result = qdrant_client.query_points(
                collection_name=QDRANT_COLLECTION,
                query=query_vec,
                limit=120,
                with_payload=True,
            )
            results = getattr(result, "points", []) or []
        except Exception as e:
            return f"知识库检索失败：{str(e)}"

        active_set = set(active_ids)
        chunks = []
        for item in results:
            payload = item.payload or {}
            score = float(getattr(item, "score", 0.0) or 0.0)
            if payload.get("dataset_id") in active_set and score >= RAGService.SCORE_THRESHOLD:
                text = payload.get("text", "")
                if text:
                    chunks.append(text)
            if len(chunks) >= 20:
                break

        context = "\n".join(chunks)
        if not context:
            return RAGService._chat_without_knowledge(question)

        if not dashscope.api_key:
            return RAGService._local_fallback_answer(context)

        try:
            answer = RAGService._call_qwen(
                [
                    {"role": "system", "content": "请根据提供的已知信息回答问题，不要编造内容。"},
                    {"role": "user", "content": f"已知信息：{context}\n问题：{question}"},
                ]
            )
        except TimeoutError:
            return RAGService._local_fallback_answer(context)
        except Exception as e:
            return f"{RAGService._local_fallback_answer(context)}\n（在线模型调用异常：{str(e)}）"

        return answer or RAGService._local_fallback_answer(context)

    @staticmethod
    def get_datasets():
        """获取所有未删除的数据集"""
        try:
            db = SessionLocal()
            datasets = db.query(RagDataset).filter(RagDataset.is_deleted == "0").all()
            return [
                {
                    "id": dataset.id,
                    "file_name": dataset.file_name,
                    "file_path": dataset.file_path,
                    "upload_time": dataset.upload_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "file_size": dataset.file_size,
                }
                for dataset in datasets
            ]
        except Exception as e:
            return {"error": str(e)}
        finally:
            db.close()

    @staticmethod
    def delete_dataset(dataset_id):
        """删除数据集（软删除）"""
        try:
            db = SessionLocal()
            dataset = db.query(RagDataset).filter(RagDataset.id == dataset_id).first()
            if not dataset:
                return {"error": "数据集不存在"}

            dataset.is_deleted = "1"
            db.commit()
            return {"message": "数据集删除成功"}
        except Exception as e:
            db.rollback()
            return {"error": str(e)}
        finally:
            db.close()

    @staticmethod
    def get_dataset_detail(dataset_id):
        """获取数据集详情"""
        try:
            db = SessionLocal()
            dataset = db.query(RagDataset).filter(
                RagDataset.id == dataset_id,
                RagDataset.is_deleted == "0",
            ).first()

            if not dataset:
                return {"error": "数据集不存在或已删除"}

            ext = os.path.splitext(dataset.file_path)[1].lower()
            if ext in [".xlsx", ".xls"]:
                df = pd.read_excel(dataset.file_path)
                data = df.to_dict("records")
            elif ext == ".txt":
                with open(dataset.file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read().strip()
                chunks = RAGService._split_text_content(content, chunk_size=300)
                data = [{"content": item} for item in chunks[:50]]
            else:
                data = [{"content": "暂不支持该文件类型的详情预览"}]

            return {
                "id": dataset.id,
                "file_name": dataset.file_name,
                "file_path": dataset.file_path,
                "upload_time": dataset.upload_time.strftime("%Y-%m-%d %H:%M:%S"),
                "file_size": dataset.file_size,
                "data": data,
            }
        except Exception as e:
            return {"error": str(e)}
        finally:
            db.close()
