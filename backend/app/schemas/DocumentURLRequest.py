from pydantic import BaseModel

class DocumentURLRequest(BaseModel):
    document_ids: list[int]