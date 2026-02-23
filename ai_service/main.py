import os
import time
import uuid
import json
import base64
import io
from typing import List, Dict, Any

from fastapi import FastAPI, UploadFile, File, HTTPException, Path, Body, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from PIL import Image, ImageDraw, ImageStat, ImageOps, UnidentifiedImageError
import dashscope

from rag_service import RAGService
from prediction_service import PredictionService

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)
AI_GRADE_DIR = os.path.join(DATA_DIR, "ai_grade")
AI_GRADE_REF_DIR = os.path.join(AI_GRADE_DIR, "references")
AI_GRADE_RESULT_DIR = os.path.join(AI_GRADE_DIR, "results")
os.makedirs(AI_GRADE_REF_DIR, exist_ok=True)
os.makedirs(AI_GRADE_RESULT_DIR, exist_ok=True)

# 初始化FastAPI应用
app = FastAPI(title="本地RAG问答系统")

# 允许跨域请求（方便前端调用）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 暴露上传文件，供前端展示AI批改标注图
app.mount("/files", StaticFiles(directory=DATA_DIR), name="files")

AI_REF_STORE: Dict[str, Dict[str, Any]] = {}
RAG_ALLOW_EXT = (".xlsx", ".xls", ".txt")
IMAGE_ALLOW_EXT = (".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif")
CSV_EXT = ".csv"
MIN_AI_SCORE = 1
MAX_AI_SCORE = 200
DEFAULT_AI_SCORE = 100
QWEN_VL_MODEL = "qwen-vl-max-latest"
DEFAULT_AI_QUESTION_COUNT = 12
MIN_AI_QUESTION_COUNT = 4
MAX_AI_QUESTION_COUNT = 40

dashscope.api_key = os.getenv("DASHSCOPE_API_KEY", "").strip() or os.getenv("QWEN_API_KEY", "").strip()


def _load_dashscope_api_key() -> str:
    # 1) 优先读取系统环境变量
    for key_name in ("DASHSCOPE_API_KEY", "QWEN_API_KEY"):
        value = os.getenv(key_name, "").strip()
        if value:
            return value
    # 2) 回退读取 ai_service/.env
    env_path = os.path.join(BASE_DIR, ".env")
    if not os.path.exists(env_path):
        return ""
    try:
        with open(env_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key in ("DASHSCOPE_API_KEY", "QWEN_API_KEY") and value:
                    return value
    except Exception:
        return ""
    return ""


def _ensure_dashscope_api_key() -> bool:
    loaded = _load_dashscope_api_key()
    if loaded:
        dashscope.api_key = loaded
        os.environ["DASHSCOPE_API_KEY"] = loaded
        return True
    return bool(getattr(dashscope, "api_key", ""))


_ensure_dashscope_api_key()


def _validate_upload_ext(upload_file: UploadFile, allow_ext: tuple[str, ...]) -> str:
    ext = os.path.splitext(upload_file.filename or "")[1].lower()
    if ext not in allow_ext:
        raise HTTPException(status_code=400, detail=f"仅支持 {', '.join(allow_ext)} 文件")
    return ext


async def _save_upload(upload_file: UploadFile, save_dir: str, allow_ext: tuple[str, ...]) -> str:
    ext = _validate_upload_ext(upload_file, allow_ext)
    filename = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(save_dir, filename)
    content = await upload_file.read()
    if not content:
        raise HTTPException(status_code=400, detail="上传文件为空")
    # 对图片上传做二进制校验，避免把HTML/错误页等非图片内容写入后续流程
    if allow_ext == IMAGE_ALLOW_EXT:
        try:
            with Image.open(io.BytesIO(content)) as img:
                img.verify()
        except Exception:
            raise HTTPException(status_code=400, detail="上传内容不是有效图片文件")
    with open(file_path, "wb") as f:
        f.write(content)
    return file_path


def _estimate_score_from_image(student_path: str, reference_path: str = None, max_score: int = 100):
    try:
        with Image.open(student_path) as raw:
            student_img = ImageOps.exif_transpose(raw).convert("L")
            s_stat = ImageStat.Stat(student_img)
            s_mean = s_stat.mean[0]
            s_std = s_stat.stddev[0]
    except (UnidentifiedImageError, OSError):
        raise HTTPException(status_code=400, detail="学生答题图片无效，无法识别")

    if reference_path and os.path.exists(reference_path):
        try:
            with Image.open(reference_path) as raw_ref:
                ref_img = ImageOps.exif_transpose(raw_ref).convert("L")
                r_stat = ImageStat.Stat(ref_img)
                r_mean = r_stat.mean[0]
                r_std = r_stat.stddev[0]
        except (UnidentifiedImageError, OSError):
            raise HTTPException(status_code=400, detail="参考样卷图片无效，无法识别")
        mean_gap = abs(s_mean - r_mean)
        std_gap = abs(s_std - r_std)
        similarity = max(0.0, 1.0 - (0.7 * mean_gap / 255.0 + 0.3 * std_gap / 128.0))
    else:
        # 无样卷时：使用图像纹理复杂度作为简化估计
        similarity = min(1.0, max(0.2, s_std / 64.0))

    score = int(round(max_score * (0.55 + 0.45 * similarity)))
    score = max(0, min(max_score, score))
    return score, similarity


def _safe_question_count(value: int) -> int:
    try:
        val = int(value or DEFAULT_AI_QUESTION_COUNT)
    except Exception:
        val = DEFAULT_AI_QUESTION_COUNT
    return max(MIN_AI_QUESTION_COUNT, min(MAX_AI_QUESTION_COUNT, val))


def _question_grid(question_count: int, width: int, height: int) -> tuple[int, int]:
    aspect = max(0.4, min(2.8, width / max(1, height)))
    cols = max(2, int(round((question_count * aspect) ** 0.5)))
    rows = max(2, int((question_count + cols - 1) // cols))
    while rows * cols < question_count:
        cols += 1
        rows = (question_count + cols - 1) // cols
    return rows, cols


def _build_mark_points(student_path: str, question_count: int = DEFAULT_AI_QUESTION_COUNT):
    target_count = _safe_question_count(question_count)
    with Image.open(student_path) as raw:
        img = ImageOps.exif_transpose(raw).convert("L")
        width, height = img.size
        points = []
        rows, cols = _question_grid(target_count, width, height)
        cell_w = max(1, width // (cols + 1))
        cell_h = max(1, height // (rows + 1))
        stats = []
        for idx in range(target_count):
            r = idx // cols + 1
            c = idx % cols + 1
            x = c * cell_w
            y = r * cell_h
            box = (
                max(0, x - cell_w // 4),
                max(0, y - cell_h // 6),
                min(width, x + cell_w // 4),
                min(height, y + cell_h // 6),
            )
            patch = img.crop(box)
            stat = ImageStat.Stat(patch)
            stats.append(
                {
                    "x": x,
                    "y": y,
                    "std": float(stat.stddev[0] or 0.0),
                    "darkness": max(0.0, 255.0 - float(stat.mean[0] or 255.0)),
                }
            )
        if not stats:
            return points
        std_values = sorted(item["std"] for item in stats)
        dark_values = sorted(item["darkness"] for item in stats)
        std_threshold = max(8.0, std_values[len(std_values) // 2] * 1.08)
        dark_threshold = max(10.0, dark_values[len(dark_values) // 2] * 1.12)
        for idx, item in enumerate(stats, start=1):
            std_hit = item["std"] >= std_threshold
            dark_hit = item["darkness"] >= dark_threshold
            mark = "tick" if (std_hit or dark_hit) else "cross"
            confidence = min(1.0, max(item["std"] / max(1.0, std_threshold), item["darkness"] / max(1.0, dark_threshold)))
            points.append(
                {
                    "x": item["x"],
                    "y": item["y"],
                    "mark": mark,
                    "confidence": round(confidence, 3),
                    "questionNo": idx,
                }
            )
        return points


def _draw_marked_image(student_path: str, marks: List[Dict[str, Any]]):
    with Image.open(student_path) as raw:
        img = ImageOps.exif_transpose(raw).convert("RGB")
        draw = ImageDraw.Draw(img)
        stroke = max(2, min(img.size) // 260)
        for item in marks:
            x = int(item.get("x", 0))
            y = int(item.get("y", 0))
            mark = item.get("mark")
            if mark == "tick":
                color = (24, 160, 88)
                draw.line((x - 16, y + 2, x - 3, y + 16), fill=color, width=stroke)
                draw.line((x - 3, y + 16, x + 18, y - 12), fill=color, width=stroke)
            else:
                color = (220, 53, 69)
                draw.line((x - 14, y - 14, x + 14, y + 14), fill=color, width=stroke)
                draw.line((x - 14, y + 14, x + 14, y - 14), fill=color, width=stroke)
            q_no = item.get("questionNo")
            if q_no:
                draw.text((x + 20, y - 18), f"Q{q_no}", fill=(33, 37, 41))

        out_name = f"annotated_{uuid.uuid4().hex}.png"
        out_path = os.path.join(AI_GRADE_RESULT_DIR, out_name)
        img.save(out_path, format="PNG")
    return out_path


def _build_teacher_reason_text(question_results: List[Dict[str, Any]]) -> str:
    wrong_items = [item for item in question_results if not item.get("isCorrect")]
    if not wrong_items:
        return "错因：本次识别结果全部判定为正确。"
    lines = ["错因："]
    for item in wrong_items:
        lines.append(f"Q{item.get('questionNo')}：{item.get('reason') or '答案不完整或关键要点缺失'}")
    return "\n".join(lines)


def _build_student_result_text(question_results: List[Dict[str, Any]]) -> str:
    parts = []
    for item in question_results:
        symbol = "√" if item.get("isCorrect") else "×"
        parts.append(f"Q{item.get('questionNo')} {symbol}")
    return "；".join(parts)


def _normalize_question_results(question_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    normalized: List[Dict[str, Any]] = []
    for idx, item in enumerate(question_results, start=1):
        normalized.append(
            {
                "questionNo": int(item.get("questionNo") or idx),
                "isCorrect": bool(item.get("isCorrect")),
                "reason": str(item.get("reason") or "").strip(),
                "mark": "tick" if bool(item.get("isCorrect")) else "cross",
                "x": int(item.get("x") or 0),
                "y": int(item.get("y") or 0),
                "confidence": float(item.get("confidence") or 0.0),
            }
        )
    return normalized


def _analyze_questions_with_heuristic(student_path: str, question_count: int = DEFAULT_AI_QUESTION_COUNT) -> List[Dict[str, Any]]:
    marks = _build_mark_points(student_path, question_count=question_count)
    question_results: List[Dict[str, Any]] = []
    for idx, mark in enumerate(marks, start=1):
        is_correct = mark.get("mark") == "tick"
        confidence = float(mark.get("confidence") or 0.0)
        reason = "" if is_correct else ("识别到该区域作答特征较弱，疑似缺步骤或结果错误" if confidence < 0.95 else "识别到关键作答特征不足")
        question_results.append(
            {
                "questionNo": idx,
                "isCorrect": is_correct,
                "reason": reason,
                "x": mark.get("x"),
                "y": mark.get("y"),
                "confidence": confidence,
            }
        )
    return question_results


def _extract_json_text(raw_text: str) -> Dict[str, Any]:
    text = (raw_text or "").strip()
    if not text:
        return {}
    try:
        return json.loads(text)
    except Exception:
        pass
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        try:
            return json.loads(text[start : end + 1])
        except Exception:
            return {}
    return {}


def _analyze_questions_with_qwen_vl(
    student_path: str,
    reference_path: str = "",
    rubric: str = "",
    question_count: int = DEFAULT_AI_QUESTION_COUNT,
) -> List[Dict[str, Any]]:
    if not _ensure_dashscope_api_key():
        return []
    try:
        with open(student_path, "rb") as f:
            student_b64 = base64.b64encode(f.read()).decode("utf-8")
        ref_part = ""
        if reference_path and os.path.exists(reference_path):
            with open(reference_path, "rb") as rf:
                ref_b64 = base64.b64encode(rf.read()).decode("utf-8")
            ref_part = f"\n参考样卷(base64)：{ref_b64[:2500]}..."
        prompt = (
            "你是阅卷老师。根据学生答题图片识别并按题判断正误，输出严格JSON，"
            "格式为：{\"questions\":[{\"questionNo\":1,\"isCorrect\":true,\"reason\":\"...\"},...]}。"
            f"需要输出 {question_count} 题。reason要简短，错题必须给出错因。不要输出任何额外文本。"
            f"\n批改标准：{rubric or '步骤完整、关键点正确、结论正确'}"
            f"{ref_part}\n学生答题(base64)：{student_b64[:12000]}..."
        )
        resp = dashscope.Generation.call(
            model=QWEN_VL_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        if getattr(resp, "status_code", None) != 200:
            return []
        output_text = (resp.output.get("text", "") or "").strip()
        parsed = _extract_json_text(output_text)
        questions = parsed.get("questions")
        if not isinstance(questions, list):
            return []
        normalized: List[Dict[str, Any]] = []
        for idx, item in enumerate(questions, start=1):
            if not isinstance(item, dict):
                continue
            normalized.append(
                {
                    "questionNo": int(item.get("questionNo") or idx),
                    "isCorrect": bool(item.get("isCorrect")),
                    "reason": str(item.get("reason") or "").strip(),
                }
            )
        return normalized
    except Exception:
        return []


def _merge_question_layout(
    student_path: str,
    question_results: List[Dict[str, Any]],
    question_count: int = DEFAULT_AI_QUESTION_COUNT,
) -> List[Dict[str, Any]]:
    layout_marks = _build_mark_points(student_path, question_count=question_count)
    merged: List[Dict[str, Any]] = []
    if not question_results:
        return _normalize_question_results(layout_marks)
    for idx, layout in enumerate(layout_marks, start=1):
        result = question_results[idx - 1] if idx - 1 < len(question_results) else {}
        merged.append(
            {
                "questionNo": idx,
                "isCorrect": bool(result.get("isCorrect", layout.get("mark") == "tick")),
                "reason": str(result.get("reason") or ("" if result.get("isCorrect", False) else "答案不完整或关键要点缺失")).strip(),
                "x": layout.get("x"),
                "y": layout.get("y"),
                "confidence": float(layout.get("confidence") or 0.0),
            }
        )
    return _normalize_question_results(merged)


def _grade_single_image(
    student_path: str,
    reference_path: str = None,
    rubric: str = "",
    max_score: int = 100,
    question_count: int = DEFAULT_AI_QUESTION_COUNT,
):
    score, similarity = _estimate_score_from_image(student_path, reference_path, max_score=max_score)
    target_count = _safe_question_count(question_count)
    vl_results = _analyze_questions_with_qwen_vl(
        student_path,
        reference_path=reference_path or "",
        rubric=rubric,
        question_count=target_count,
    )
    if vl_results:
        question_results = _merge_question_layout(student_path, vl_results, question_count=target_count)
    else:
        question_results = _analyze_questions_with_heuristic(student_path, question_count=target_count)
        question_results = _normalize_question_results(question_results)
    marks = [
        {"x": q.get("x"), "y": q.get("y"), "mark": q.get("mark"), "questionNo": q.get("questionNo")}
        for q in question_results
    ]
    annotated_path = _draw_marked_image(student_path, marks)
    tick_count = len([m for m in question_results if m.get("isCorrect")])
    cross_count = len(question_results) - tick_count
    level = "优秀" if score >= max_score * 0.9 else "良好" if score >= max_score * 0.75 else "合格" if score >= max_score * 0.6 else "需改进"
    rubric_text = f"；参考标准：{rubric}" if rubric else ""
    feedback = (
        f"AI批改结果：{level}。共标注{len(question_results)}处，√ {tick_count} 处，× {cross_count} 处；"
        f"图像相似度 {round(similarity * 100, 1)}%。建议结合知识点与书写规范进行复核{rubric_text}。"
    )
    teacher_feedback = _build_teacher_reason_text(question_results)
    student_feedback = _build_student_result_text(question_results)
    return {
        "score": score,
        "feedback": feedback,
        "marks": marks,
        "questionResults": question_results,
        "teacherFeedback": teacher_feedback,
        "studentFeedback": student_feedback,
        "annotated_path": annotated_path,
    }


def _collect_upload_items(file: UploadFile | None, files: List[UploadFile] | None) -> List[UploadFile]:
    upload_items: List[UploadFile] = []
    if file is not None:
        upload_items.append(file)
    if files:
        upload_items.extend(files)
    if not upload_items:
        raise HTTPException(status_code=400, detail="请提供要上传的文件")

    dedup_items: List[UploadFile] = []
    seen_keys: set[str] = set()
    for item in upload_items:
        unique_key = f"{item.filename}:{id(item)}"
        if unique_key in seen_keys:
            continue
        seen_keys.add(unique_key)
        dedup_items.append(item)
    return dedup_items


def _score_range(value: int) -> int:
    return max(MIN_AI_SCORE, min(MAX_AI_SCORE, int(value or DEFAULT_AI_SCORE)))


# 上传知识库文件接口（同时支持单文件和多文件上传）
@app.post("/upload-excel")
async def upload_excel(
    file: UploadFile = File(None),
    files: List[UploadFile] = File(None)
):
    """支持单文件和多文件上传（.xlsx/.xls/.txt）"""
    upload_items = _collect_upload_items(file, files)
    results = []

    for upload_item in upload_items:
        filename = upload_item.filename or "unknown"
        try:
            ext = _validate_upload_ext(upload_item, RAG_ALLOW_EXT)
            timestamp = int(time.time())
            name, _ = os.path.splitext(filename)
            unique_filename = f"{name}_{timestamp}{ext}"
            file_path = os.path.join(DATA_DIR, unique_filename)

            with open(file_path, "wb") as f:
                f.write(await upload_item.read())

            result = RAGService.process_file(file_path)
            is_success = isinstance(result, str) and ("成功导入" in result)
            results.append({
                "filename": filename,
                "status": "success" if is_success else "error",
                "message": result,
            })
        except HTTPException:
            results.append({"filename": filename, "status": "error", "message": "请上传 .xlsx / .xls / .txt 文件"})
        except Exception as e:
            results.append({"filename": filename, "status": "error", "message": f"处理文件时出错: {str(e)}"})

    return {"results": results}

# 问答接口
@app.get("/query")
async def query(question: str):
    _ensure_dashscope_api_key()
    q = (question or "").strip()
    if not q:
        raise HTTPException(status_code=400, detail="问题不能为空")
    result = RAGService.query_answer_with_meta(q)
    return {
        "question": q,
        "answer": result.get("answer", ""),
        "mode": result.get("mode", "chat"),
        "matchedCount": result.get("matchedCount", 0),
        "sources": result.get("sources", []),
    }


@app.get("/llm-status")
async def llm_status():
    available = _ensure_dashscope_api_key()
    return {"onlineModelEnabled": bool(available), "provider": "dashscope"}


@app.post("/ai-grade/reference")
async def upload_ai_grade_reference(file: UploadFile = File(...)):
    """上传老师批改好的样卷图片"""
    ref_path = await _save_upload(file, AI_GRADE_REF_DIR, IMAGE_ALLOW_EXT)
    ref_id = uuid.uuid4().hex
    rel_path = os.path.relpath(ref_path, DATA_DIR).replace(os.sep, "/")
    AI_REF_STORE[ref_id] = {
        "file_name": file.filename,
        "path": ref_path,
        "url": f"/files/{rel_path}",
    }
    return {"referenceId": ref_id, "fileName": file.filename, "referenceUrl": f"/files/{rel_path}"}


@app.post("/ai-grade/single")
async def ai_grade_single(
    studentFile: UploadFile = File(...),
    referenceId: str = Form(""),
    rubric: str = Form(""),
    maxScore: int = Form(100),
    questionCount: int = Form(DEFAULT_AI_QUESTION_COUNT),
):
    """AI批改单张学生试卷，返回标注图和建议分数"""
    student_path = await _save_upload(studentFile, AI_GRADE_RESULT_DIR, IMAGE_ALLOW_EXT)
    reference = AI_REF_STORE.get(referenceId, {}) if referenceId else {}
    grade_result = _grade_single_image(
        student_path=student_path,
        reference_path=reference.get("path"),
        rubric=rubric,
        max_score=_score_range(maxScore),
        question_count=_safe_question_count(questionCount),
    )
    rel_path = os.path.relpath(grade_result["annotated_path"], DATA_DIR).replace(os.sep, "/")
    return {
        "score": grade_result["score"],
        "feedback": grade_result["feedback"],
        "marks": grade_result["marks"],
        "gradingJson": {
            "totalQuestions": len(grade_result["questionResults"]),
            "correctCount": len([q for q in grade_result["questionResults"] if q.get("isCorrect")]),
            "wrongCount": len([q for q in grade_result["questionResults"] if not q.get("isCorrect")]),
            "questions": grade_result["questionResults"],
        },
        "teacherFeedback": grade_result["teacherFeedback"],
        "studentFeedback": grade_result["studentFeedback"],
        "annotatedImageUrl": f"/files/{rel_path}",
    }


@app.post("/ai-grade/batch")
async def ai_grade_batch(
    files: List[UploadFile] = File(...),
    referenceId: str = Form(""),
    rubric: str = Form(""),
    maxScore: int = Form(100),
    questionCount: int = Form(DEFAULT_AI_QUESTION_COUNT),
):
    """AI一键批改（批量图片）"""
    reference = AI_REF_STORE.get(referenceId, {}) if referenceId else {}
    results = []
    for file in files:
        try:
            student_path = await _save_upload(file, AI_GRADE_RESULT_DIR, IMAGE_ALLOW_EXT)
            grade_result = _grade_single_image(
                student_path=student_path,
                reference_path=reference.get("path"),
                rubric=rubric,
                max_score=_score_range(maxScore),
                question_count=_safe_question_count(questionCount),
            )
            rel_path = os.path.relpath(grade_result["annotated_path"], DATA_DIR).replace(os.sep, "/")
            results.append(
                {
                    "filename": file.filename,
                    "status": "success",
                    "score": grade_result["score"],
                    "feedback": grade_result["feedback"],
                    "gradingJson": {
                        "totalQuestions": len(grade_result["questionResults"]),
                        "correctCount": len([q for q in grade_result["questionResults"] if q.get("isCorrect")]),
                        "wrongCount": len([q for q in grade_result["questionResults"] if not q.get("isCorrect")]),
                        "questions": grade_result["questionResults"],
                    },
                    "teacherFeedback": grade_result["teacherFeedback"],
                    "studentFeedback": grade_result["studentFeedback"],
                    "annotatedImageUrl": f"/files/{rel_path}",
                }
            )
        except Exception as e:
            results.append({"filename": file.filename, "status": "error", "message": str(e)})
    return {"results": results}

# 获取所有数据集接口（与前端匹配）
@app.get("/rag-api/datasets")
async def get_datasets():
    result = RAGService.get_datasets()
    # 如果返回的是错误信息，抛出HTTP异常
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result

# 为兼容前端，添加/datasets端点作为别名
@app.get("/datasets")
async def get_datasets_alias():
    return await get_datasets()

# 删除数据集接口（与前端匹配）
@app.delete("/rag-api/datasets/{dataset_id}")
async def delete_dataset(dataset_id: int = Path(..., description="数据集ID")):
    result = RAGService.delete_dataset(dataset_id)
    # 如果返回的是错误信息，抛出HTTP异常
    if "error" in result:
        if result["error"] == "数据集不存在":
            raise HTTPException(status_code=404, detail=result["error"])
        else:
            raise HTTPException(status_code=500, detail=result["error"])
    return result

# 为兼容前端，添加/datasets/{dataset_id} DELETE端点作为别名
@app.delete("/datasets/{dataset_id}")
async def delete_dataset_alias(dataset_id: int = Path(..., description="数据集ID")):
    return await delete_dataset(dataset_id)

# 获取数据集详情接口（与前端匹配）
@app.get("/rag-api/datasets/{dataset_id}")
async def get_dataset_detail(dataset_id: int = Path(..., description="数据集ID")):
    result = RAGService.get_dataset_detail(dataset_id)
    # 如果返回的是错误信息，抛出HTTP异常
    if "error" in result:
        if result["error"] == "数据集不存在或已删除":
            raise HTTPException(status_code=404, detail=result["error"])
        else:
            raise HTTPException(status_code=500, detail=result["error"])
    return result

# 为兼容前端，添加/datasets/{dataset_id} GET端点作为别名
@app.get("/datasets/{dataset_id}")
async def get_dataset_detail_alias(dataset_id: int = Path(..., description="数据集ID")):
    return await get_dataset_detail(dataset_id)

# 训练预测模型接口
@app.post("/train-prediction-model")
async def train_prediction_model(file: UploadFile = File(..., description="上传的CSV文件")):
    """训练学生成绩预测模型
    
    支持上传CSV文件进行模型训练
    """
    try:
        # 检查文件扩展名是否为CSV
        if not (file.filename or "").lower().endswith(CSV_EXT):
            raise HTTPException(status_code=400, detail="只支持CSV文件格式")
        
        # 训练模型（传入文件对象）
        result = PredictionService.train_model_from_csv(file.file)
        return {"status": "success", "message": "模型训练成功", "result": result}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"训练模型时出错: {str(e)}")

# 预测学生成绩接口
@app.post("/predict-score")
async def predict_score(input_data: dict = Body(..., embed=True)):
    """预测学生成绩"""
    result = PredictionService.predict_student_score(input_data)
    
    # 检查预测结果
    if result["status"] == "error":
        if "模型不存在" in result["message"]:
            raise HTTPException(status_code=404, detail=result["message"])
        else:
            raise HTTPException(status_code=500, detail=result["message"])
    
    return result

# 获取模型信息接口
@app.get("/model-info")
async def get_model_info():
    """获取模型信息"""
    result = PredictionService.get_model_info()
    
    # 检查获取结果
    if result["status"] == "error":
        raise HTTPException(status_code=404, detail=result["message"])
    
    return result

# 启动服务
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main.py", host="0.0.0.0", port=8000, reload=True)
