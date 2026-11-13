from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class ChatRequest(BaseModel):
    question: str
    session_id: Optional[int] = None  # 如果是新会话，前端传 null
    history: List[Dict[str, Any]] = []  # 保留这个，作为前端快照


class SessionUpdate(BaseModel):
    title: str
