import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.kb.retriever import retrieve_chunks


def test_retrieve():
    db = SessionLocal()

    # 模拟用户的提问
    queries = [
        "这双鞋适合脚宽的人穿吗？",
        "鞋底开胶了怎么售后？",
        "能直接扔洗衣机里洗吗？",
    ]

    for q in queries:
        print(f"\n🙋 用户提问：{q}")
        print("🔍 检索中...")

        try:
            chunks = retrieve_chunks(db, q, top_k=1)  # 我们只存了一段，所以 top_k=1

            if not chunks:
                print("❌ 没找到相关内容")
                continue

            for i, text in enumerate(chunks):
                print(f"🎯 匹配结果 {i+1}:\n{text}")

        except Exception as e:
            print(f"❌ 报错啦: {e}")

    db.close()


if __name__ == "__main__":
    test_retrieve()
