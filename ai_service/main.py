from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Path, Body
from fastapi.middleware.cors import CORSMiddleware
import os
from typing import List
from rag_service import RAGService
from prediction_service import PredictionService

# 创建数据存储文件夹（如果不存在）
os.makedirs("./data", exist_ok=True)

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

# 上传知识库文件接口（同时支持单文件和多文件上传）
@app.post("/upload-excel")
async def upload_excel(
    file: UploadFile = File(None),
    files: List[UploadFile] = File(None)
):
    """支持单文件和多文件上传（.xlsx/.xls/.txt）"""
    allow_ext = (".xlsx", ".xls", ".txt")
    # 处理单文件上传
    if file and not files:
        # 验证文件格式
        if not file.filename.lower().endswith(allow_ext):
            raise HTTPException(status_code=400, detail="请上传 .xlsx / .xls / .txt 文件")
        
        # 生成唯一文件名（添加时间戳）
        import time
        timestamp = int(time.time())
        name, ext = os.path.splitext(file.filename)
        unique_filename = f"{name}_{timestamp}{ext}"
        file_path = f"./data/{unique_filename}"
        
        # 保存文件到本地
        with open(file_path, "wb") as f:
            f.write(await file.read())
        
        # 处理并导入数据库
        try:
            result = RAGService.process_file(file_path)
            return {"message": result}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"处理文件时出错: {str(e)}")
    
    # 处理多文件上传
    elif files:
        results = []
        import time
        
        for file_item in files:
            # 验证文件格式
            if not file_item.filename.lower().endswith(allow_ext):
                results.append({
                    "filename": file_item.filename,
                    "status": "error",
                    "message": "请上传 .xlsx / .xls / .txt 文件"
                })
                continue
            
            # 生成唯一文件名（添加时间戳）
            timestamp = int(time.time())
            name, ext = os.path.splitext(file_item.filename)
            unique_filename = f"{name}_{timestamp}{ext}"
            file_path = f"./data/{unique_filename}"
            
            # 保存文件到本地
            with open(file_path, "wb") as f:
                f.write(await file_item.read())
            
            # 处理并导入数据库
            try:
                result = RAGService.process_file(file_path)
                results.append({
                    "filename": file_item.filename,
                    "status": "success",
                    "message": result
                })
            except Exception as e:
                results.append({
                    "filename": file_item.filename,
                    "status": "error",
                    "message": f"处理文件时出错: {str(e)}"
                })
        
        return {"results": results}
    
    # 没有提供文件
    else:
        raise HTTPException(status_code=400, detail="请提供要上传的文件")

# 问答接口
@app.get("/query")
async def query(question: str):
    answer = RAGService.query_answer(question)
    return {"question": question, "answer": answer}

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
        if not file.filename.lower().endswith('.csv'):
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
