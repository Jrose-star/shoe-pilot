from sqlalchemy.orm import Session
from langchain_core.messages import HumanMessage, AIMessage
from app.agents.qa_graph import build_qa_graph
from app.models.chat import ChatSession, ChatMessage
import json


def ask_question(
    db: Session, user_id: int, question: str, session_id: int = None
) -> dict:
    # 1. 获取或创建会话
    if not session_id:
        # 如果是新会话，用前 10 个字做标题
        title = question[:10] + "..." if len(question) > 10 else question
        session = ChatSession(user_id=user_id, title=title)
        db.add(session)
        db.commit()
        db.refresh(session)
        session_id = session.id
    else:
        session = (
            db.query(ChatSession)
            .filter(ChatSession.id == session_id, ChatSession.user_id == user_id)
            .first()
        )
        if not session:
            raise Exception("会话不存在或无权访问")

    # 2. 从数据库拉取该会话的所有历史消息
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

    # 3. 把当前用户的新问题也加进去
    messages.append(HumanMessage(content=question))

    # 4. 构建并运行图
    graph = build_qa_graph(db)
    final_state = graph.invoke({"messages": messages})

    final_answer = final_state["messages"][-1].content
    citations = final_state.get("citations", [])

    # 5. 将用户问题和 AI 回答持久化到数据库
    user_msg = ChatMessage(session_id=session_id, role="user", content=question)
    ai_msg = ChatMessage(
        session_id=session_id,
        role="assistant",
        content=final_answer,
        citations=json.dumps(citations, ensure_ascii=False) if citations else None,
    )
    db.add(user_msg)
    db.add(ai_msg)
    db.commit()

    return {
        "answer": final_answer,
        "citations": citations,
        "session_id": session_id,  # 返回给前端，下次提问带上它
    }
