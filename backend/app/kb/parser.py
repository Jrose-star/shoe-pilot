import fitz  # PyMuPDF
from docx import Document
import pymupdf


def parse_pdf(file_path: str) -> str:
    """解析 PDF 文件"""
    text = ""
    try:
        doc = fitz.open(file_path)
        for page in doc:
            text += page.get_text() + "\n"
    except Exception as e:
        print(f"PDF解析失败: {e}")
    return text


from docx import Document


def parse_docx(file_path: str) -> str:
    """解析 Word 文件（支持段落和表格）"""
    text = ""
    try:
        doc = Document(file_path)
        # 1. 提取段落
        for para in doc.paragraphs:
            if para.text.strip():
                text += para.text + "\n"

        # 2. 提取表格（白酒知识等业务文档常常用表格排版）
        for table in doc.tables:
            for row in table.rows:
                row_data = [
                    cell.text.strip() for cell in row.cells if cell.text.strip()
                ]
                if row_data:
                    text += " | ".join(row_data) + "\n"
    except Exception as e:
        print(f"Word解析失败: {e}")
    return text


def parse_file(file_path: str, file_ext: str) -> str:
    """根据后缀名路由到对应的解析器"""
    file_ext = file_ext.lower()
    if file_ext == ".pdf":
        return parse_pdf(file_path)
    elif file_ext in [".docx", ".doc"]:
        return parse_docx(file_path)
    elif file_ext in [".txt", ".md"]:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        raise ValueError(f"不支持的文件格式: {file_ext}")
