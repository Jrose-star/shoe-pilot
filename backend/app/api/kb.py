import os
import shutil
import traceback
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.kb.parser import parse_file
from app.kb.indexer import index_document

# ⚠️ 注意：确保这里导入的 Document 路径和你的 models 文件夹结构匹配
from app.models.document import Document

router = APIRouter(prefix="/api/kb", tags=["Knowledge Base"])


@router.get("/documents")
def list_documents(db: Session = Depends(get_db)):
    try:
        docs = db.query(Document).order_by(Document.id.desc()).all()
        result = [
            {
                "id": d.id,
                "title": d.title,
                "status": d.status,
                "source_type": d.source_type,
            }
            for d in docs
        ]
        return {"code": 0, "data": result}
    except Exception as e:
        print("\n========== 查询列表报错 ==========")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload")
def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    file_ext = os.path.splitext(file.filename)[1]
    if file_ext.lower() not in [".pdf", ".docx", ".txt", ".md"]:
        raise HTTPException(status_code=400, detail="仅支持 PDF, Word, TXT, Markdown")

    temp_file_path = f"temp_{file.filename}"
    try:
        # 1. 保存临时文件
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 2. 解析文本（你刚才缺的就是这一行！）
        content = parse_file(temp_file_path, file_ext)

        if not content or not content.strip():
            raise HTTPException(status_code=400, detail="未能提取到文本")

        # 3. 切块并向量化入库
        index_document(db, title=file.filename, content=content, source_type=file_ext)

        return {"code": 0, "message": f"文件 {file.filename} 入库成功！"}
    except Exception as e:
        print("\n========== 上传入库报错 ==========")
        traceback.print_exc()
        print("==================================\n")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # 4. 清理临时文件
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
