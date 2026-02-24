import os
import re
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from datetime import datetime
from typing import Any

import dashscope
import pandas as pd
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from sklearn.feature_extraction.text import HashingVectorizer

from database import Base, SessionLocal, engine
from models import RagDataset

# 创建数据库表（如果不存在）
Base.metadata.create_all(bind=engine)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
QDRANT_PATH = os.path.join(BASE_DIR, "qdrant_db")
QDRANT_COLLECTION = "excel_data"
VECTOR_SIZE = 384
ACTIVE_FLAG = "0"
DELETED_FLAG = "1"
SUPPORTED_EXCEL_EXT = {".xlsx", ".xls"}
SUPPORTED_TXT_EXT = ".txt"
QWEN_MODEL = "qwen-turbo"

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


def _load_api_key():
    # 1) 优先读系统环境变量
    for key_name in ("DASHSCOPE_API_KEY", "QWEN_API_KEY"):
        value = os.getenv(key_name, "").strip()
        if value:
            return value

    # 2) 再尝试读取 ai_service/.env（支持 uv 启动时未自动注入环境变量）
    env_path = os.path.join(BASE_DIR, ".env")
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    if key in ("DASHSCOPE_API_KEY", "QWEN_API_KEY") and val:
                        return val
        except Exception:
            return ""
    return ""


# 通义千问 API 密钥（未配置时自动降级为本地模式）
dashscope.api_key = _load_api_key()


class RAGService:
    SCORE_THRESHOLD = 0.58
    MIN_FALLBACK_SCORE = 0.12
    FALLBACK_TOP_K = 5
    MAX_STRONG_CHUNKS = 20
    MAX_CONTEXT_CHARS = 4200
    FIELD_PATTERNS = {
        "Exam_Score": [r"Exam_Score", r"Exam Score", r"考试成绩", r"成绩"],
        "Hours_Studied": [r"Hours_Studied", r"Hours Studied", r"学习时长", r"学习时间"],
        "Sleep_Hours": [r"Sleep_Hours", r"Sleep Hours", r"睡眠时长", r"睡眠时间"],
        "Previous_Scores": [r"Previous_Scores", r"Previous Scores", r"之前成绩", r"历史成绩"],
        "Motivation_Level": [r"Motivation_Level", r"Motivation Level", r"学习动力", r"动力水平"],
    }

    @staticmethod
    def _serialize_dataset(dataset: RagDataset) -> dict[str, Any]:
        return {
            "id": dataset.id,
            "file_name": dataset.file_name,
            "file_path": dataset.file_path,
            "upload_time": dataset.upload_time.strftime("%Y-%m-%d %H:%M:%S"),
            "file_size": dataset.file_size,
        }

    @staticmethod
    def _build_point_id(dataset_id, row_index):
        return int(dataset_id) * 1_000_000 + int(row_index)

    @staticmethod
    def _split_text_content(raw_text, chunk_size=500, overlap=80):
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
                chunk = "\n".join(buffer).strip()
                if chunk:
                    chunks.append(chunk)
                # 保留尾部重叠内容，增强跨段检索稳定性
                tail = chunk[-overlap:] if overlap > 0 else ""
                buffer = [tail, line] if tail else [line]
                current_len = len("\n".join(buffer))
            else:
                buffer.append(line)
                current_len += len(line) + 1
        if buffer:
            chunk = "\n".join(buffer).strip()
            if chunk:
                chunks.append(chunk)
        return chunks

    @staticmethod
    def _extract_texts_from_file(file_path):
        ext = os.path.splitext(file_path)[1].lower()
        if ext in SUPPORTED_EXCEL_EXT:
            df = pd.read_excel(file_path)
            texts = []
            for _, row in df.iterrows():
                fields = []
                for col in df.columns:
                    value = row[col]
                    if pd.isna(value):
                        continue
                    text_value = str(value).strip()
                    if text_value:
                        fields.append(f"{col}：{text_value}")
                if fields:
                    texts.append(", ".join(fields))
            return texts, "excel"
        if ext == SUPPORTED_TXT_EXT:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                raw_text = f.read()
            return RAGService._split_text_content(raw_text), "txt"
        raise ValueError("仅支持 .xlsx / .xls / .txt 文件")

    @staticmethod
    def process_file(file_path):
        """解析文件并存入Qdrant和MySQL数据库（支持Excel/TXT）"""
        texts, file_type = RAGService._extract_texts_from_file(file_path)
        if not texts:
            return "文件解析后没有可用文本，请检查内容是否为空"
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path) / 1024  # KB

        db = SessionLocal()
        try:
            dataset = RagDataset(
                file_name=file_name,
                file_path=file_path,
                upload_time=datetime.now(),
                file_size=file_size,
                is_deleted=ACTIVE_FLAG,
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
                    rollback_dataset.is_deleted = DELETED_FLAG
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
        context_text = (context or "").strip()
        if not context_text:
            return "未检索到相关知识。"

        lines = [line.strip() for line in context_text.splitlines() if line.strip()]
        advice = []
        for line in lines:
            for tag in ("优化方案：", "调整方案：", "提升方案：", "维持方案：", "建议："):
                if tag in line:
                    part = line.split(tag, 1)[1].strip("；;，, ")
                    if part:
                        advice.append(part)
                    break
            if len(advice) >= 3:
                break

        if not advice:
            preview = context_text[:300]
            return f"已命中相关资料。结论：当前信息可用于分析，建议优先围绕薄弱项做针对训练。\n依据摘要：{preview}"

        unique_advice = []
        for item in advice:
            if item not in unique_advice:
                unique_advice.append(item)
        bullets = [f"{idx + 1}. {text}" for idx, text in enumerate(unique_advice[:3])]
        return "结论：已命中可执行的提分建议。\n建议：\n" + "\n".join(bullets)

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
            return dashscope.Generation.call(model=QWEN_MODEL, messages=messages)

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
        result = RAGService.query_answer_with_meta(question)
        return result.get("answer", "")

    @staticmethod
    def _build_source_item(payload: dict[str, Any], score: float):
        text = str(payload.get("text", "")).strip()
        return {
            "datasetId": payload.get("dataset_id"),
            "fileName": payload.get("file_name", ""),
            "rowIndex": payload.get("row_index"),
            "score": round(score, 4),
            "snippet": text[:180],
            "text": text,
        }

    @staticmethod
    def _pick_diverse_sources(sources: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
        if not sources or limit <= 0:
            return []
        grouped: dict[Any, list[dict[str, Any]]] = {}
        for src in sorted(sources, key=lambda x: x.get("score", 0), reverse=True):
            key = src.get("datasetId")
            grouped.setdefault(key, []).append(src)

        selected: list[dict[str, Any]] = []
        dataset_order = [k for k in grouped.keys()]
        idx = 0
        while len(selected) < limit and dataset_order:
            dataset_key = dataset_order[idx % len(dataset_order)]
            bucket = grouped.get(dataset_key, [])
            if bucket:
                selected.append(bucket.pop(0))
            if not bucket:
                dataset_order.remove(dataset_key)
                if not dataset_order:
                    break
                idx = idx % len(dataset_order)
            else:
                idx += 1
        return selected

    @staticmethod
    def _retrieve_context(question: str, active_ids: list[int]) -> dict[str, Any]:
        query_vec = _embed_texts([question])[0]
        result = qdrant_client.query_points(
            collection_name=QDRANT_COLLECTION,
            query=query_vec,
            limit=120,
            with_payload=True,
        )
        results = getattr(result, "points", []) or []

        active_set = set(active_ids)
        strong_sources = []
        fallback_sources = []
        for item in results:
            payload = item.payload or {}
            dataset_id = payload.get("dataset_id")
            if dataset_id not in active_set:
                continue
            score = float(getattr(item, "score", 0.0) or 0.0)
            source = RAGService._build_source_item(payload, score)
            if not source["text"]:
                continue
            if score >= RAGService.SCORE_THRESHOLD:
                strong_sources.append(source)
            if score >= RAGService.MIN_FALLBACK_SCORE:
                fallback_sources.append(source)

        if strong_sources:
            selected = RAGService._pick_diverse_sources(strong_sources, RAGService.MAX_STRONG_CHUNKS)
            mode = "strong"
        else:
            selected = RAGService._pick_diverse_sources(fallback_sources, RAGService.FALLBACK_TOP_K)
            mode = "fallback" if selected else "none"

        texts = []
        total_chars = 0
        for src in selected:
            seg = src["text"]
            if total_chars + len(seg) > RAGService.MAX_CONTEXT_CHARS:
                break
            texts.append(seg)
            total_chars += len(seg)

        context = "\n".join(texts)
        return {
            "mode": mode,
            "context": context,
            "sources": selected,
        }

    @staticmethod
    def _build_rag_prompt(question: str, context: str):
        return [
            {
                "role": "system",
                "content": (
                    "你是教育平台RAG助手。仅依据给定资料回答，不要编造。"
                    "当资料中已经出现可用于分析的学生字段（如 Exam_Score、Hours_Studied、Sleep_Hours、Previous_Scores 等）时，"
                    "必须先给出可执行建议，不要直接回答“无法给建议”。"
                    "输出必须是总结性表达，先给结论，再给 3-5 条编号建议，避免复述检索片段原文。"
                    "只有在完全没有相关字段时，才说明信息不足，并明确需要补充哪些字段。"
                ),
            },
            {"role": "user", "content": f"【资料】\n{context}\n\n【问题】\n{question}"},
        ]

    @staticmethod
    def _contains_insufficient_signal(answer: str) -> bool:
        text = (answer or "").strip()
        if not text:
            return True
        patterns = [
            "无法直接得出",
            "无法给出",
            "无法提供",
            "信息不足",
            "没有提供",
            "缺少",
        ]
        return any(p in text for p in patterns)

    @staticmethod
    def _extract_numeric_field(all_text: str, aliases: list[str]) -> int | None:
        for alias in aliases:
            escaped = re.escape(alias)
            regex_list = [
                rf"{escaped}\s*[：:=]\s*[\"']?(-?\d+(?:\.\d+)?)",
                rf"[\"']{escaped}[\"']\s*:\s*[\"']?(-?\d+(?:\.\d+)?)",
            ]
            for reg in regex_list:
                match = re.search(reg, all_text, flags=re.IGNORECASE)
                if match:
                    try:
                        return int(float(match.group(1)))
                    except (TypeError, ValueError):
                        continue
        return None

    @staticmethod
    def _extract_student_fields_from_text(all_text: str) -> dict[str, int]:
        fields: dict[str, int] = {}
        for key, aliases in RAGService.FIELD_PATTERNS.items():
            value = RAGService._extract_numeric_field(all_text, aliases)
            if value is not None:
                fields[key] = value
        return fields

    @staticmethod
    def _rule_summary_from_sources(question: str, sources: list[dict[str, Any]]) -> str:
        all_text = "\n".join([str((src or {}).get("text", "")).strip() for src in sources if src])
        if not all_text:
            return ""

        fields = RAGService._extract_student_fields_from_text(all_text)
        score = fields.get("Exam_Score")
        hours = fields.get("Hours_Studied")
        sleep = fields.get("Sleep_Hours")
        prev = fields.get("Previous_Scores")
        motivation = fields.get("Motivation_Level")

        advice = []
        if hours is not None and hours > 10:
            advice.append("把长时低效学习压缩到 6-8 小时，采用“2小时学习+10分钟复盘”的节奏，优先做错题与薄弱点。")
        if sleep is not None:
            if sleep > 9:
                advice.append("将睡眠逐步调整到 7-8 小时，把新增时间用于薄弱学科专项练习。")
            elif 6 <= sleep <= 8:
                advice.append("保持 6-8 小时规律睡眠，固定作息，保障注意力稳定。")
            else:
                advice.append("先把睡眠补到 6-8 小时，避免疲劳导致学习效率下滑。")
        if prev is not None and score is not None and score <= prev + 10:
            advice.append("按周跟踪同科目分项得分，定位掉分题型后做针对训练，避免只刷总量。")
        if motivation is not None and motivation <= 4:
            advice.append("把学习任务切成 25-30 分钟小目标并设置即时反馈，先恢复学习启动意愿。")
        if score is not None and score < 75:
            advice.append("优先保证基础题满分率，先清理高频错题再做综合题，避免一上来刷难题。")

        if not advice:
            lines = [line.strip() for line in all_text.splitlines() if line.strip()]
            for line in lines:
                for tag in ("优化方案：", "调整方案：", "提升方案：", "维持方案：", "建议："):
                    if tag in line:
                        part = line.split(tag, 1)[1].strip("；;，, ")
                        if part and part not in advice:
                            advice.append(part)
                        break
                if len(advice) >= 3:
                    break

        if not advice:
            return ""

        conclusion = "结论：有可落地的提分路径，核心是提升学习效率与策略匹配。"
        if score is not None:
            conclusion = f"结论：当前成绩约为 {score} 分，具备明确提升空间。"
        items = "\n".join([f"{idx + 1}. {item}" for idx, item in enumerate(advice[:4])])
        return f"{conclusion}\n建议：\n{items}"

    @staticmethod
    def query_answer_with_meta(question):
        db = None
        try:
            db = SessionLocal()
            active_ids = [item.id for item in db.query(RagDataset.id).filter(RagDataset.is_deleted == ACTIVE_FLAG).all()]
        finally:
            if db is not None:
                db.close()

        if not active_ids:
            return {
                "answer": RAGService._chat_without_knowledge(question),
                "mode": "chat",
                "sources": [],
                "matchedCount": 0,
            }

        try:
            retrieved = RAGService._retrieve_context(question, active_ids)
        except Exception as e:
            return {
                "answer": f"知识库检索失败：{str(e)}",
                "mode": "error",
                "sources": [],
                "matchedCount": 0,
            }

        context = retrieved.get("context", "")
        sources = retrieved.get("sources", [])
        mode = retrieved.get("mode", "none")
        if not context:
            return {
                "answer": RAGService._chat_without_knowledge(question),
                "mode": "chat",
                "sources": [],
                "matchedCount": 0,
            }

        if not dashscope.api_key:
            return {
                "answer": RAGService._local_fallback_answer(context),
                "mode": mode,
                "sources": [{k: v for k, v in src.items() if k != "text"} for src in sources],
                "matchedCount": len(sources),
            }

        try:
            answer = RAGService._call_qwen(RAGService._build_rag_prompt(question, context))
        except TimeoutError:
            answer = RAGService._local_fallback_answer(context)
        except Exception as e:
            answer = f"{RAGService._local_fallback_answer(context)}\n（在线模型调用异常：{str(e)}）"

        if RAGService._contains_insufficient_signal(answer):
            fallback_summary = RAGService._rule_summary_from_sources(question, sources)
            if fallback_summary:
                answer = fallback_summary

        return {
            "answer": answer or RAGService._local_fallback_answer(context),
            "mode": mode,
            "sources": [{k: v for k, v in src.items() if k != "text"} for src in sources],
            "matchedCount": len(sources),
        }

    @staticmethod
    def get_datasets():
        """获取所有未删除的数据集"""
        db = None
        try:
            db = SessionLocal()
            datasets = db.query(RagDataset).filter(RagDataset.is_deleted == ACTIVE_FLAG).all()
            return [RAGService._serialize_dataset(dataset) for dataset in datasets]
        except Exception as e:
            return {"error": str(e)}
        finally:
            if db is not None:
                db.close()

    @staticmethod
    def delete_dataset(dataset_id):
        """删除数据集（软删除）"""
        db = None
        try:
            db = SessionLocal()
            dataset = db.query(RagDataset).filter(RagDataset.id == dataset_id).first()
            if not dataset:
                return {"error": "数据集不存在"}

            dataset.is_deleted = DELETED_FLAG
            db.commit()
            return {"message": "数据集删除成功"}
        except Exception as e:
            if db is not None:
                db.rollback()
            return {"error": str(e)}
        finally:
            if db is not None:
                db.close()

    @staticmethod
    def get_dataset_detail(dataset_id):
        """获取数据集详情"""
        db = None
        try:
            db = SessionLocal()
            dataset = db.query(RagDataset).filter(
                RagDataset.id == dataset_id,
                RagDataset.is_deleted == ACTIVE_FLAG,
            ).first()

            if not dataset:
                return {"error": "数据集不存在或已删除"}

            ext = os.path.splitext(dataset.file_path)[1].lower()
            if ext in SUPPORTED_EXCEL_EXT:
                df = pd.read_excel(dataset.file_path)
                data = df.to_dict("records")
            elif ext == SUPPORTED_TXT_EXT:
                with open(dataset.file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read().strip()
                chunks = RAGService._split_text_content(content, chunk_size=300)
                data = [{"content": item} for item in chunks[:50]]
            else:
                data = [{"content": "暂不支持该文件类型的详情预览"}]

            result = RAGService._serialize_dataset(dataset)
            result["data"] = data
            return result
        except Exception as e:
            return {"error": str(e)}
        finally:
            if db is not None:
                db.close()
