from sqlalchemy.orm import Session
from app.models.document import Chunk  # 确认你的 models 路径
from app.kb.embedder import embedder


def retrieve_chunks(
    db: Session, query: str, top_k: int = 3, distance_threshold: float = 1.2
):
    """
    distance_threshold: L2距离阈值，大于该值认为不相关，直接丢弃。
    （具体数值需要根据你的模型和实际数据测试微调，0.8 是个不错的起点）
    """
    query_vector = embedder.get_embedding(query)

    # 加上 .label("distance") 方便我们获取距离
    results = (
        db.query(
            Chunk.content,
            Chunk.embedding.l2_distance(query_vector).label("distance"),
        )
        .order_by("distance")
        .limit(top_k)
        .all()
    )

    valid_chunks = []
    for row in results:
        if row.distance < distance_threshold:
            valid_chunks.append(row.content)
        else:
            print(f"⚠️ 抛弃低相关度片段，距离: {row.distance:.4f}")

    return valid_chunks
