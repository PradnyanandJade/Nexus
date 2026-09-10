from fastapi import APIRouter,Request,File,UploadFile,Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_current_user
from app.database.models import User
from app.schemas.DocumentURLRequest import DocumentURLRequest
from app.database.database import get_db
from app.services.document_service import (
    save_file,
    get_document_by_id,
    delete_file,
    get_all_documents,
    get_document_urls_from_s3
)

router = APIRouter(prefix='/documents')

@router.get('/')
async def get_documents(
    current_user : User = Depends(get_current_user),
    db:AsyncSession = Depends(get_db)
):
    return await get_all_documents(user_id=current_user.id,db=db)

@router.get('/{document_id}')
async def get_document(
    document_id:int,
    current_user : User = Depends(get_current_user),
    db:AsyncSession = Depends(get_db)
):
    return await get_document_by_id(document_id=document_id,user_id=current_user.id,db=db)


@router.post("/urls")
async def get_document_urls(
    data: DocumentURLRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await get_document_urls_from_s3(data,current_user.id,db)

@router.post('/upload')
async def upload_document(
    request:Request,
    file : UploadFile = File(...),
    current_user : User = Depends(get_current_user),
    db:AsyncSession = Depends(get_db)
):
    return await save_file(request,current_user.id,file,db)

@router.delete('/delete/{document_id}')
async def delete_document(
    request:Request,
    document_id : int,
    current_user : User = Depends(get_current_user),
    db:AsyncSession = Depends(get_db)
):
    return await delete_file(request,current_user.id,document_id,db)
