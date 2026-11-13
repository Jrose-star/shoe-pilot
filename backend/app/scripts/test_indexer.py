import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.kb.indexer import index_document

# 模拟一段鞋类产品知识
MOCK_TEXT = """
ShoePilot 产品说明：缓震跑鞋 X1 系列。
这款跑鞋采用了最新的超临界发泡中底材料，比上一代轻了 15%，回弹性能提升了 20%。
适合日常通勤和 5-10 公里的慢跑。
鞋面采用单层工程网布，透气性极佳，但防水性能较弱，不建议在雨天或积水路面跑步。
关于尺码：X1 系列版型偏窄，建议脚宽的顾客买大半码。
保养说明：鞋面脏了可以用软毛刷蘸取中性洗涤剂轻轻刷洗，不要放入洗衣机机洗，以免破坏中底结构。鞋底开胶属于严重质量问题，如果在三包期内，可以凭购买凭证联系售后免费换新。
"""


def test_index():
    print("--- 开始测试向量化入库 ---")
    db = SessionLocal()
    try:
        doc_id = index_document(db, title="X1跑鞋产品手册.txt", content=MOCK_TEXT)
        print(
            f"\n🎉 全部成功！请在 Navicat 中刷新 chunks 表，查看数据 (文档ID: {doc_id})"
        )
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    test_index()
