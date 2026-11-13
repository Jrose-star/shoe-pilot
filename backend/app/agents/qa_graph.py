from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from sqlalchemy.orm import Session
from app.kb.retriever import retrieve_chunks
from app.llm.cloud_client import llm_client


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    context: str
    citations: List[str]
    need_retrieval: bool  # 新增：是否需要检索


# 1. 路由节点：判断是否需要查库
def route_question(state: AgentState):
    last_user_message = state["messages"][-1].content

    prompt = f"""判断以下用户问题是否需要查阅企业知识库：
用户问题：{last_user_message}
如果是闲聊、打招呼、询问你是谁，回答'no'。
如果是询问具体产品、业务、文档内容，回答'yes'。
只输出 yes 或 no。"""

    response = (
        llm_client.chat_with_messages([{"role": "user", "content": prompt}])
        .strip()
        .lower()
    )
    return {"need_retrieval": "yes" in response}


# 2. 检索节点
def retrieve_node(state: AgentState, db: Session):
    last_user_message = state["messages"][-1].content
    # 使用带阈值的检索
    chunks = retrieve_chunks(db, last_user_message, top_k=3, distance_threshold=0.8)
    context_text = (
        "\n\n".join([f"【片段】\n{text}" for text in chunks]) if chunks else ""
    )
    return {"context": context_text, "citations": chunks}


# 3. 生成节点
def generate_node(state: AgentState):
    context = state.get("context", "")
    messages = state["messages"]
    last_user_message = messages[-1].content

    if context:
        # 有知识库内容时的 Prompt
        system_prompt = f"""你是一个严谨的企业级知识助手。
请严格根据以下【已知信息】来回答用户的问题。
【重要规则】：
1. **你的回答第一句话必须是：“根据知识库内容，”**。
2. 答案必须完全基于已知信息，不要编造。
3. 如果已知信息中没提到，请回答“抱歉，知识库未收录相关信息”。
4. 回答保持简洁、专业。

【已知信息】：
{context}
"""
    else:
        # 没有知识库内容时的 Prompt
        system_prompt = """你是一个智能助手。当前未从企业知识库检索到相关内容。
请直接根据你的通用常识回答用户。如果是具体业务问题且你不确定，请回答“抱歉，知识库中未找到相关业务信息”。"""

    llm_messages = [{"role": "system", "content": system_prompt}]
    for msg in messages:
        role = "user" if msg.type == "human" else "assistant"
        llm_messages.append({"role": role, "content": msg.content})

    llm_messages.append(
        {"role": "system", "content": f"请回答用户的最新问题：“{last_user_message}”。"}
    )

    reply = llm_client.chat_with_messages(llm_messages)
    return {"messages": [{"role": "assistant", "content": reply}]}
    context = state.get("context", "")
    messages = state["messages"]

    # 提取最新的用户问题
    last_user_message = messages[-1].content

    system_prompt = "你是一个严谨、专业的智能助手。"

    if context:
        # 有知识库内容
        system_prompt += f"""
请严格根据以下【已知信息】来回答用户的问题。
规则：
1. 答案必须基于已知信息，不要编造。
2. 如果已知信息中没提到，请回答“抱歉，知识库未收录相关信息”。
3. 回答保持简洁、专业。
4. 第一句一定要这样说：根据知识库检索到相关知识:

【已知信息】：
{context}
"""
    else:
        # 没有知识库内容（闲聊或通用知识）
        system_prompt += """
当前没有从知识库中检索到相关内容。请直接根据你的常识回答用户的问题。
【重要约束】：
1. 如果用户问的是生活常识（如天气、算术等），直接回答即可，**绝对不要强行关联到鞋子或特定业务**。
2. 如果用户问的是你们公司的具体业务，而你并不知道，请回答“抱歉，知识库中未找到相关业务信息”。
"""

    # 构造消息列表
    llm_messages = [{"role": "system", "content": system_prompt}]

    # 加入历史消息（为了处理代词，但稍微改写一下规则）
    for msg in messages:
        role = "user" if msg.type == "human" else "assistant"
        llm_messages.append({"role": role, "content": msg.content})

    # 追加一个强化指令，防止串台
    llm_messages.append(
        {
            "role": "system",
            "content": f"请注意：你当前唯一的任务是回答用户的最新问题：“{last_user_message}”。如果历史对话与当前问题无关，请直接忽略历史对话。",
        }
    )

    reply = llm_client.chat_with_messages(llm_messages)
    return {"messages": [{"role": "assistant", "content": reply}]}


# 4. 构建图
def build_qa_graph(db: Session):
    workflow = StateGraph(AgentState)

    workflow.add_node("router", route_question)
    workflow.add_node("retrieve", lambda state: retrieve_node(state, db))
    workflow.add_node("generate", generate_node)

    workflow.set_entry_point("router")

    # 核心：条件边判断
    workflow.add_conditional_edges(
        "router",
        lambda state: state["need_retrieval"],
        {
            True: "retrieve",  # 需要检索走 retrieve
            False: "generate",  # 不需要检索直接去 generate
        },
    )

    workflow.add_edge("retrieve", "generate")
    workflow.add_edge("generate", END)

    return workflow.compile()
