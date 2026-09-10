from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import models
from fastapi import Request
from langchain_core.messages import HumanMessage
from app.services.message_service import save_message_to_conversation
from app.streaming.streaming_service import stream_graph
from app.database.database import AsyncSessionLocal

async def get_all_conversations(user_id:int,db: AsyncSession):
    result = await db.execute(
            select(models.Conversation)
            .where(
                models.Conversation.user_id == user_id
            )
        )
    return result.scalars().all()

async def get_conversation_by_id(conversation_id: int,user_id:int,db: AsyncSession):
    query = select(models.Conversation).where(models.Conversation.id == conversation_id)
    if user_id is not None: 
        query = query.where(models.Conversation.user_id == user_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def create_new_conversation(conversation: models.Conversation,user_id:int,db: AsyncSession):
    new_conversation = models.Conversation(user_id=user_id, title=conversation.title)
    db.add(new_conversation)
    await db.commit()
    await db.refresh(new_conversation)
    return new_conversation

async def update_existing_conversation(conversation_id: int, title : str,user_id : int, db: AsyncSession):
    """Update an existing conversation's information."""
    conversation = await get_conversation_by_id(conversation_id,user_id,db)
    if conversation:
        conversation.title = title
        await db.commit()
        await db.refresh(conversation)
        return conversation
    return None

async def delete_conversation_by_id(conversation_id: int,user_id:int,db: AsyncSession):
    """Delete a conversation by ID."""
    conversation = await get_conversation_by_id(conversation_id,user_id,db)    
    if conversation:
        await db.delete(conversation)
        await db.commit()
        return True
    return False

async def validate_conversation(user_id: int,conversation_id: int,db: AsyncSession):
    """Make sure the conversation belongs to the user."""
    result = await db.execute(
        select(models.Conversation).where(
            models.Conversation.id == conversation_id,
            models.Conversation.user_id == user_id
        )
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise ValueError(
            "Conversation not found or does not belong to the user."
        )
    return conversation

async def get_messages_by_conversation_id(conversation_id: int,user_id:int,db: AsyncSession):
    result = await db.execute(
        select(models.Message)
        .join(models.Conversation)
        .where(
            models.Message.conversation_id==conversation_id,
            models.Conversation.user_id==user_id
        )
        .order_by(models.Message.created_at)
    )
    return result.scalars().all()

async def get_attached_document_ids(
    conversation_id: int,
    db: AsyncSession
):
    result = await db.execute(
        select(models.ConversationDocument.document_id)
        .where(
            models.ConversationDocument.conversation_id == conversation_id
        )
    )

    return result.scalars().all()

async def get_attached_documents(
    conversation_id: int,
    user_id: int,
    db: AsyncSession,
):
    result = await db.execute(
        select(models.Document)
        .join(
            models.ConversationDocument,
            models.ConversationDocument.document_id == models.Document.id,
        )
        .join(
            models.Conversation,
            models.Conversation.id == models.ConversationDocument.conversation_id,
        )
        .where(
            models.ConversationDocument.conversation_id == conversation_id,
            models.Conversation.user_id == user_id,
            models.Document.user_id == user_id,
        )
        .order_by(models.ConversationDocument.created_at)
    )
    return result.scalars().all()

async def chat_in_conversation(request:Request,conversation_id:int,user_id:int,content:str,db:AsyncSession):
    await validate_conversation(user_id=user_id,conversation_id=conversation_id,db=db)
    document_ids = await get_attached_document_ids(conversation_id=conversation_id,db=db)
    initial_state = {
        "messages": [
            HumanMessage(content=content)
        ],
        "document_ids": document_ids
    }
    config = {
        "configurable": {
            "thread_id": str(conversation_id)
        }
    }
    response = await request.app.state.graph.ainvoke(
        initial_state,
        config=config
    )
    ai_reply = response["messages"][-1].content
    await save_message_to_conversation(role="Human",content=content,conversation_id=conversation_id,db=db)
    await save_message_to_conversation(role="AI",content=ai_reply,conversation_id=conversation_id,db=db)

    return {
        "reply":response["messages"][-1].content,
        "context":response["context"],
        "context_documents":response["context_documents"]
    }

async def chat_in_conversation_stream(request:Request,conversation_id:int,user_id:int,content:str):
    async with AsyncSessionLocal() as db:
        await validate_conversation(user_id=user_id,conversation_id=conversation_id,db=db)
        document_ids = await get_attached_document_ids(conversation_id=conversation_id,db=db)

    initial_state = {
        "messages": [
            HumanMessage(content=content)
        ],
        "document_ids": document_ids
    }
    config = {
        "configurable": {
            "thread_id": str(conversation_id)
        }
    }
    graph = request.app.state.graph
    ai_reply = None
    async for event in stream_graph(graph=graph,initial_state=initial_state,config=config):
        yield event
        if event["type"] == "answer":
            ai_reply = event["content"]
        elif event["type"] == "guardrail_block":
            ai_reply = event["message"]

    if ai_reply:
        async with AsyncSessionLocal() as db:
            await save_message_to_conversation(role="Human",content=content,conversation_id=conversation_id,db=db)
            await save_message_to_conversation(role="AI",content=ai_reply,conversation_id=conversation_id,db=db)

async def attach_document(conversation_id:int,document_id:int,db:AsyncSession,user_id:int):
    result = await db.execute(
        select(models.Document)
        .where(
            models.Document.id == document_id,
            models.Document.user_id == user_id
        )
    )
    document = result.scalar_one_or_none()
    if not document:
        return None
    result = await db.execute(
        select(models.Conversation)
        .where(
            models.Conversation.id == conversation_id,
            models.Conversation.user_id == user_id
        )
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        return None
    result = await db.execute(
        select(models.ConversationDocument).where(
            models.ConversationDocument.document_id == document_id,
            models.ConversationDocument.conversation_id == conversation_id
        )
    )
    existing_association = result.scalar_one_or_none()
    if existing_association:
        return existing_association
    association = models.ConversationDocument(
        conversation_id=conversation_id,
        document_id=document_id
    )
    db.add(association)
    await db.commit()
    await db.refresh(association)
    return association
