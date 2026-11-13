from app.database import engine, Base
from app.models import Document, DocumentChunk

print("正在删除旧表...")
Base.metadata.drop_all(bind=engine)
print("正在创建新表(512维)...")
Base.metadata.create_all(bind=engine)
print("完成！")
