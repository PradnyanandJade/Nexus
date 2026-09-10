from sqlalchemy.ext.asyncio import AsyncSession
from app.database import models

async def save_message_to_conversation(role:str,content:str,conversation_id:int,db:AsyncSession):
    new_message = models.Message(conversation_id=conversation_id,role=role,content=content)
    db.add(new_message)
    await db.commit()
    await db.refresh(new_message)
    return new_message

