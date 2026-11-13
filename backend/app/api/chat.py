from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.qa_service import ask_question
from app.schemas.chat import ChatRequest, SessionUpdate
from app.api.auth import get_current_user  # 引入认证
from app.models.user import User
from fastapi.responses import StreamingResponse
import json
from app.kb.retriever import retrieve_chunks
from app.llm.cloud_client import llm_client
from app.models.chat import ChatSession, ChatMessage
from langchain_core.messages import HumanMessage, AIMessage
from typing import List

router = APIRouter(prefix="/api", tags=["Chat"])


@router.post("/chat")
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # 强制必须登录才能调此接口
):
    try:
        result = ask_question(db, current_user.id, request.question, request.session_id)
        return {"code": 0, "message": "ok", "data": result}
    except Exception as e:
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions")
def get_user_sessions(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    sessions = (
        db.query(ChatSession)
        .filter(ChatSession.user_id == current_user.id)
        .order_by(ChatSession.created_at.desc())
        .all()
    )
    return {"code": 0, "data": [{"id": s.id, "title": s.title} for s in sessions]}


@router.get("/sessions/{session_id}")
def get_session_messages(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = (
        db.query(ChatSession)
        .filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    msgs = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at)
        .all()
    )
    result = []
    for m in msgs:
        result.append(
            {
                "role": m.role,
                "content": m.content,
                "citations": json.loads(m.citations) if m.citations else [],
            }
        )
    return {"code": 0, "data": result}


@router.put("/sessions/{session_id}")
def update_session_title(
    session_id: int,
    req: SessionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = (
        db.query(ChatSession)
        .filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id)
        .first()
    )

    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    session.title = req.title
    db.commit()
    return {"code": 0, "message": "修改成功"}


# 2. 删除会话
@router.delete("/sessions/{session_id}")
def delete_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = (
        db.query(ChatSession)
        .filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id)
        .first()
    )

    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    # 因为我们在 models/chat.py 里配置了 cascade="all, delete-orphan"
    # 所以删除 Session 会自动级联删除属于该会话的所有 Messages
    db.delete(session)
    db.commit()
    return {"code": 0, "message": "删除成功"}


@router.post("/chat/stream")
def chat_stream(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 1. 处理会话和标题 (与 qa_service 逻辑一致)
    session_id = request.session_id
    if not session_id:
        title = (
            request.question[:10] + "..."
            if len(request.question) > 10
            else request.question
        )
        session = ChatSession(user_id=current_user.id, title=title)
        db.add(session)
        db.commit()
        db.refresh(session)
        session_id = session.id
    else:
        session = (
            db.query(ChatSession)
            .filter(
                ChatSession.id == session_id, ChatSession.user_id == current_user.id
            )
            .first()
        )
        if not session:
            raise HTTPException(status_code=404, detail="会话不存在")

    # 2. 获取数据库历史
    db_messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at)
        .all()
    )
    messages = []
    for msg in db_messages:
        if msg.role == "user":
            messages.append(HumanMessage(content=msg.content))
        elif msg.role == "assistant":
            messages.append(AIMessage(content=msg.content))

    messages.append(HumanMessage(content=request.question))

    # 3. 检索知识库
    chunks = retrieve_chunks(db, request.question, top_k=3, distance_threshold=0.8)
    context = "\n\n".join([f"【片段】\n{t}" for t in chunks]) if chunks else ""

    # 4. 构造 Prompt
    if context:
        system_prompt = f"你是一个严谨的企业级知识助手。请严格根据以下【已知信息】回答，第一句话必须是：'根据知识库内容，'。\n【已知信息】：\n{context}"
    else:
        system_prompt = "你是一个智能助手。当前无知识库信息，请根据常识回答。"

    llm_messages = [{"role": "system", "content": system_prompt}]
    for msg in messages:
        role = "user" if msg.type == "human" else "assistant"
        llm_messages.append({"role": role, "content": msg.content})

    # 5. 构建生成器（边发数据，边存库）
    def generate():
        full_answer = ""
        # 先发一个特殊标记，告诉前端 session_id
        yield f"data: {json.dumps({'session_id': session_id, 'type': 'meta'})}\n\n"

        try:
            for chunk_text in llm_client.stream_chat(llm_messages):
                full_answer += chunk_text
                # 按照 SSE 格式推送文本
                yield f"data: {json.dumps({'text': chunk_text, 'type': 'content'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

        # 流式结束，将完整的问答保存到数据库
        user_msg = ChatMessage(
            session_id=session_id, role="user", content=request.question
        )
        ai_msg = ChatMessage(
            session_id=session_id,
            role="assistant",
            content=full_answer,
            citations=json.dumps(chunks, ensure_ascii=False) if chunks else None,
        )
        db.add(user_msg)
        db.add(ai_msg)
        db.commit()

        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
