import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()


class Settings:
    DASHSCOPE_API_KEY: str = os.getenv("DASHSCOPE_API_KEY", "")
    DASHSCOPE_BASE_URL: str = os.getenv(
        "DASHSCOPE_BASE_URL", "https://api.deepseek.com"
    )
    LLM_MODEL_NAME: str = os.getenv("LLM_MODEL_NAME", "deepseek-chat")

    # 把你在 test_conn.py 里测试成功的真实参数填在这里
    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"
    DB_USER: str = "postgres"
    DB_PASS: str = "1234"  # 记得换成真实密码
    DB_NAME: str = "shoepilot_db"

    SECRET_KEY: str = "shoe_pilot_secret_key_2026_change_me_in_prod"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # Token 有效期 7 天


settings = Settings()
