from pydantic import BaseModel


class SummarizeRequest(BaseModel):
    text: str
    summary_type: str = "document"
