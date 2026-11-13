import os
import httpx
from openai import OpenAI
from app.config import settings

# 同样剥离代理环境变量
for proxy_key in [
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "http_proxy",
    "https_proxy",
    "ALL_PROXY",
    "all_proxy",
]:
    os.environ.pop(proxy_key, None)


class Embedder:
    def __init__(self):
        # 针对阿里云百炼，创建禁用代理的客户端
        http_client = httpx.Client(proxy=None, trust_env=False, timeout=60.0)
        self.client = OpenAI(
            api_key=settings.DASHSCOPE_API_KEY,  # 也就是你的 DASHSCOPE_API_KEY
            base_url=settings.DASHSCOPE_BASE_URL,
            http_client=http_client,
        )
        # 阿里云 text-embedding-v2 的模型名
        self.model_name = "qwen3.7-text-embedding-flash"

    def get_embedding(self, text: str) -> list[float]:
        """获取单段文本的向量"""
        try:
            response = self.client.embeddings.create(
                model=self.model_name,
                input=text,
                dimensions=1536,  # 新增这一行，强制模型输出 1536 维
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"❌ Embedding API 调用失败: {e}")
            raise e


# 全局实例
embedder = Embedder()
