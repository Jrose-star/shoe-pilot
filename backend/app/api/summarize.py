from fastapi import APIRouter, HTTPException
from app.services.summarize_service import map_reduce_summarize
from app.schemas.summarize import SummarizeRequest  # 导入抽离出去的校验类

router = APIRouter(prefix="/api", tags=["Summarize"])


@router.post("/summarize")
def summarize_text(request: SummarizeRequest):
    try:
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="文本不能为空")
        result = map_reduce_summarize(request.text, request.summary_type)
        return {"code": 0, "message": "ok", "data": {"result": result}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
