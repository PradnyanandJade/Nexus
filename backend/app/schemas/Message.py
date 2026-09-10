from pydantic import BaseModel
from datetime import datetime

class MessageCreate(BaseModel):
    conversation_id: int
    content: str

class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    content: str
    created_at: datetime
    role : str

    model_config = {
        "from_attributes": True
    }
