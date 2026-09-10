from pydantic import BaseModel
from datetime import datetime

class ConversationCreate(BaseModel):
    title: str

class ConversationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }