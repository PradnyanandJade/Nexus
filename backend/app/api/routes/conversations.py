import json
from fastapi import APIRouter, Depends,HTTPException,Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_db
from app.api.dependencies import get_current_user
from app.database.models import User
from app.schemas.Message import MessageResponse
from app.schemas.Chat import ChatRequest
from app.schemas.Conversation import ConversationCreate,ConversationResponse
from app.database.database import AsyncSessionLocal
from app.services.conversation_service import (
    get_all_conversations,
    get_conversation_by_id,
    delete_conversation_by_id,
    create_new_conversation,
    update_existing_conversation,
    get_messages_by_conversation_id,
    chat_in_conversation,
    chat_in_conversation_stream,
    attach_document,
    get_attached_documents,
    validate_conversation,
)

router = APIRouter(prefix='/conversations',tags=["Conversations"])

@router.get("/",response_model=list[ConversationResponse])
async def get_conversations(
    current_user:User=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve all conversations from the database."""
    return await get_all_conversations(current_user.id,db=db)


@router.get("/{conversation_id}",response_model=ConversationResponse)
async def get_conversation(
    conversation_id: int,
    current_user:User=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve a specific conversation by its ID."""
    conversation = await get_conversation_by_id(conversation_id=conversation_id,user_id=current_user.id,db=db)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@router.post("/",response_model=ConversationResponse)
async def create_conversation(
    conversation: ConversationCreate,
    current_user:User=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new conversation."""
    return await create_new_conversation(conversation=conversation,user_id=current_user.id,db=db)  


@router.put("/{conversation_id}",response_model=ConversationResponse)
async def update_conversation(
    conversation_id: int, 
    conversation: ConversationCreate,
    current_user:User=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    updated_conversation = await update_existing_conversation(conversation_id,conversation.title,current_user.id,db)
    if not updated_conversation:
        raise HTTPException(status_code=404,detail="Conversation not found.")
    return updated_conversation


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    current_user:User=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a specific conversation by its ID."""
    result = await delete_conversation_by_id(conversation_id=conversation_id,user_id=current_user.id,db=db)
    if result:
        return {"message": "Conversation deleted successfully."}
    else:
        raise HTTPException(status_code=404, detail="Conversation not found")


@router.get("/{conversation_id}/messages", response_model=list[MessageResponse])
async def get_conversation_messages(
    conversation_id: int,
    current_user:User =Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve all messages for a specific conversation."""
    messages = await get_messages_by_conversation_id(conversation_id=conversation_id,user_id=current_user.id,db=db)
    return messages

@router.post("/{conversation_id}/chat")
async def chat(
    request:Request,
    conversation_id:int,
    chat_request:ChatRequest,
    db:AsyncSession = Depends(get_db),
    current_user:User= Depends(get_current_user)
):
    return await chat_in_conversation(
        request=request,
        conversation_id=conversation_id,
        user_id=current_user.id,
        content=chat_request.content,
        db=db
    )

@router.post("/{conversation_id}/stream-chat")
async def chat(
    request:Request,
    conversation_id:int,
    chat_request:ChatRequest,
    # db:AsyncSession = Depends(get_db),
    current_user:User= Depends(get_current_user)
):
    async def event_generator():
        async for event in chat_in_conversation_stream(
            request=request,
            conversation_id=conversation_id,
            user_id=current_user.id,
            content=chat_request.content,
            # db=db
        ):
            yield (
                f"data: {json.dumps(event)}\n\n"
            )
            
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.post("/{conversation_id}/documents/{document_id}")
async def attach_document_to_a_conversation(
    conversation_id : int,
    document_id : int, 
    db : AsyncSession = Depends(get_db),
    current_user : User = Depends(get_current_user)
):
    return await attach_document(conversation_id=conversation_id,document_id=document_id,db=db,user_id = current_user.id)

@router.get("/{conversation_id}/documents")
async def get_conversation_documents(
    conversation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        await validate_conversation(user_id=current_user.id,conversation_id=conversation_id,db=db)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return await get_attached_documents(
        conversation_id=conversation_id,
        user_id=current_user.id,
        db=db,
    )
