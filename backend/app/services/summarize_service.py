from app.llm.cloud_client import llm_client


def map_reduce_summarize(text: str, summary_type: str = "document") -> str:
    """长文本摘要核心逻辑 (Map-Reduce)"""

    # 如果文本比较短（比如小于 2000 字），直接一步到位总结，不用分块
    if len(text) < 2000:
        return _direct_summarize(text, summary_type)

    # 1. Map 阶段：简单切分（每 1500 字一块）
    chunk_size = 1500
    chunks = [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]

    chunk_summaries = []
    for chunk in chunks:
        prompt = f"请简要提取以下文本的核心要点，不要遗漏关键数据：\n\n{chunk}"
        messages = [{"role": "user", "content": prompt}]
        summary = llm_client.chat_with_messages(messages)
        chunk_summaries.append(summary)

    # 2. Reduce 阶段：合并
    combined_text = "\n\n".join(chunk_summaries)
    return _direct_summarize(combined_text, summary_type, is_final=True)


def _direct_summarize(text: str, summary_type: str, is_final: bool = False) -> str:
    """单次调用生成最终摘要"""

    if summary_type == "weekly":
        system_prompt = "你是一个职场效率专家。请将用户提供的工作记录，整理成一份结构清晰的【周报初稿】。必须包含：本周完成、进行中、风险/问题、下周计划。"
    elif summary_type == "meeting":
        system_prompt = "你是一个高级行政助理。请将用户提供的会议记录，提取为【会议纪要】。必须包含：核心决议、待办行动项（带负责人）、重要讨论点。"
    else:
        # 默认长文档摘要
        system_prompt = "你是一个专业的知识库助手。请将用户提供的长篇文本，浓缩为一份结构清晰的【一页读懂】摘要。必须包含：核心要点、关键数据。如果这是对碎片摘要的合并，请整合去重。"

    if is_final:
        system_prompt += (
            "\n（注意：以下是分块提取的要点汇总，请整合成一份逻辑连贯的最终文档。）"
        )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": text},
    ]

    return llm_client.chat_with_messages(messages)
