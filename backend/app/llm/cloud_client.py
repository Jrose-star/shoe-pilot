import os
import httpx
from openai import OpenAI
from app.config import settings
from typing import Generator

for proxy_key in [
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "http_proxy",
    "https_proxy",
    "ALL_PROXY",
    "all_proxy",
]:
    os.environ.pop(proxy_key, None)


class LLMClient:
    def __init__(self):
        http_client = httpx.Client(proxy=None, trust_env=False, timeout=60.0)
        self.client = OpenAI(
            api_key=settings.DASHSCOPE_API_KEY,
            base_url=settings.DASHSCOPE_BASE_URL,
            http_client=http_client,
        )

    def chat_with_messages(self, messages: list) -> str:
        """接收完整的 messages 列表进行对话"""
        response = self.client.chat.completions.create(
            model=settings.LLM_MODEL_NAME,
            messages=messages,
            temperature=0.3,  # RAG 场景下温度调低，减少幻觉，让它更严谨
        )
        return response.choices[0].message.content

    def stream_chat(self, messages: list) -> Generator[str, None, None]:
        """新增：流式对话方法"""
        response = self.client.chat.completions.create(
            model=settings.LLM_MODEL_NAME,
            messages=messages,
            temperature=0.3,
            stream=True,  # 开启流式
        )
        for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


llm_client = LLMClient()
