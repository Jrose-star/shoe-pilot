from sqlalchemy.orm import Session
from app.models.document import Document, Chunk
from app.kb.embedder import embedder
import traceback


def split_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


def index_document(db: Session, title: str, content: str, source_type: str = "text"):
    print(f"开始处理文档: {title}")

    doc = Document(title=title, source_type=source_type, status="processing")
    db.add(doc)
    db.commit()
    db.refresh(doc)

    text_chunks = split_text(content)
    print(f"共切分为 {len(text_chunks)} 个块")

    try:
        for i, chunk_text in enumerate(text_chunks):
            print(f"  正在向量化第 {i+1}/{len(text_chunks)} 块...")
            # 如果这里报错，会直接跳到 except
            vector = embedder.get_embedding(chunk_text)

            chunk = Chunk(document_id=doc.id, content=chunk_text, embedding=vector)
            db.add(chunk)

        doc.status = "processed"
        db.commit()
        print(f"✅ 文档处理完成: {title}")
        return doc.id

    except Exception as e:
        # 如果中途失败，回滚当前文档的 chunk 插入，修改状态为 failed
        db.rollback()
        doc.status = "failed"
        db.commit()
        print(f"❌ 文档 {title} 向量化失败，原因: {e}")
        traceback.print_exc()
        raise Exception(f"向量化失败: {e}")
