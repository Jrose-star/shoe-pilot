import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, Base, SessionLocal
from app.models import Document, Chunk
import traceback


def test_database():
    print("1. 尝试连接数据库并建表...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ 建表成功！")
    except Exception as e:
        print("❌ 建表失败！完整错误如下：")
        # 打印完整堆栈，找出原因是密码错误还是库不存在
        traceback.print_exc()
        return


if __name__ == "__main__":
    test_database()
