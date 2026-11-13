from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

import urllib.parse

# 自动对密码进行 URL 转义（完美解决密码带 @ 或 # 的报错）
safe_password = urllib.parse.quote_plus(settings.DB_PASS)

# 重新拼接连接串
DATABASE_URL = f"postgresql://{settings.DB_USER}:{safe_password}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"

# 创建数据库引擎
engine = create_engine(DATABASE_URL)

# 创建数据库会话类
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 所有数据库模型的基类
Base = declarative_base()


# 依赖注入函数：为每个请求提供一个独立的数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """初始化数据库：在启动时自动创建所有表"""
    # 这里必须放在函数内部导入，防止循环引用报错
    from app.models.document import Document, Chunk
    from app.models.user import User
    from app.models.chat import ChatMessage, ChatSession

    print("正在检查并创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("✅ 数据库表检查/创建完成！")
