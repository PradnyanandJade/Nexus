from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile,Request
from pathlib import Path
from uuid import uuid4
import hashlib
from app.config import UPLOADS_DIR
from app.database import models
from app.services.rag_service import chunk_file
from app.services.aws_s3_service import upload_file_to_s3,delete_file_from_s3,generate_presigned_url
from app.services.vectorstore_services import save_file_to_both_indexes,delete_file_from_both_indexes
from app.config import settings
from sqlalchemy import select
from app.schemas.DocumentURLRequest import DocumentURLRequest
import io

async def get_all_documents(user_id:int,db:AsyncSession):
    result = await db.execute(
        select(models.Document)
        .where(models.Document.user_id == user_id)
    )
    return result.scalars().all()


async def get_document_by_id(document_id:int,user_id:int,db:AsyncSession):
    result = await db.execute(
        select(models.Document)
        .where(
            models.Document.user_id == user_id,
            models.Document.id == document_id
        )
    )
    return result.scalar_one_or_none()


async def save_file_to_directory(file:UploadFile,content:bytes):
    """Save the uploaded file to the specified directory."""
    
    file_name = f"{uuid4()}_{file.filename}"
    file_path = Path(UPLOADS_DIR) / file_name
    with open(file_path, "wb") as f:
        f.write(content)
    return str(file_path)


async def save_file_to_database(user_id:int,filename:str,s3_key:str,file_hash:str,db:AsyncSession):
    """Save the file information to the database."""
    document = models.Document(
        filename=filename,
        user_id=user_id,
        s3_key = s3_key,
        file_hash=file_hash
    )
    db.add(document)
    await db.commit()
    await db.refresh(document)
    return document.id

async def save_file_to_vectorstore(request:Request,file_name:str,file_path:str,user_id:int,document_id:int):
    """Save the file to the vectorstore by chunking it."""  
    chunks = await chunk_file(
        file_name=file_name,
        file_path=file_path,
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        user_id=user_id,
        document_id=document_id
    )
    await save_file_to_both_indexes(
        chunks=chunks,
        dense_index=request.app.state.dense_index,
        sparse_index=request.app.state.sparse_index,    
        embedding=request.app.state.embedding,
        bm25_encoder=request.app.state.bm25_encoder
    )
    return "File uploaded and processed successfully."


async def save_file(request:Request,user_id:int,file:UploadFile,db:AsyncSession):
    """Save the uploaded file to the directory, database, and vectorstore."""
    if not file.filename:
        raise ValueError("Filename is required.")
    suffix = Path(file.filename).suffix.lower()
    if suffix not in {".pdf", ".docx", ".txt"}:
        raise ValueError("Only PDF, DOCX, and TXT files are allowed.")
    content = await file.read()
    file_hash = hashlib.sha256(content).hexdigest()
    result = await db.execute(
        select(models.Document)
        .where(
            models.Document.file_hash == file_hash,
            models.Document.user_id == user_id
        )
    )
    existing_document = result.scalar_one_or_none()
    if existing_document:
        return {
            "message": "Document already exists.",
            "document_id": existing_document.id,
            "existing": True
        }
    file_path = await save_file_to_directory(file, content)
    document_id = None
    try:
        s3_key = f"users/{user_id}/documents/{uuid4()}_{file.filename}"
        await upload_file_to_s3(
            file_obj=io.BytesIO(content),
            s3_key=s3_key,
            content_type=file.content_type or "application/octet-stream"
        )
        document_id = await save_file_to_database(user_id=user_id,filename=file.filename,s3_key=s3_key,file_hash=file_hash,db=db)
        await save_file_to_vectorstore(request,file.filename,file_path,user_id,document_id)
        await delete_file_from_directory(file_path=file_path)
        return {
            "message": "Document uploaded and indexed successfully.",
            "document_id": document_id,
            "existing": False
        }
    except Exception:
        if document_id is not None:
            await delete_file_from_vectorstore(
                request,
                user_id,
                document_id
            )
            await delete_file_from_database(user_id=user_id,document_id=document_id,db=db)
        await delete_file_from_directory(file_path)
        await delete_file_from_s3(s3_key=s3_key)
        raise


async def delete_file_from_directory(file_path:str):
    """Delete the file from the specified directory."""
    path = Path(file_path)
    if path.exists():
        path.unlink()
        return "File deleted from directory successfully."
    else:
        return "File not found in directory."


async def delete_file_from_database(user_id:int,document_id:int,db:AsyncSession):
    """Delete the file information from the database."""
    result = await db.execute(
        select(models.Document)
        .where(
            models.Document.id == document_id,
            models.Document.user_id == user_id
        )
    )
    document = result.scalar_one_or_none()
    if document:
        await db.delete(document)
        await db.commit()
        return "File deleted from database successfully."
    else:
        return "File not found in database."


async def delete_file_from_vectorstore(request:Request,user_id:int,document_id:int):
    await delete_file_from_both_indexes(user_id=user_id,document_id=document_id,dense_index=request.app.state.dense_index,sparse_index=request.app.state.sparse_index)
    return "File deleted from vectorstore successfully."


async def delete_file(request:Request,user_id:int,document_id:int,db:AsyncSession):
    """Delete the file from the directory, database, and vectorstore."""
    # delete from database
    result = await db.execute(
        select(models.Document)
        .where(
            models.Document.id == document_id,
            models.Document.user_id == user_id
        )
    )
    document = result.scalar_one_or_none()
    if not document:
        return "File not found in database."
    s3_key = document.s3_key
    await delete_file_from_s3(s3_key=s3_key)
    await delete_file_from_vectorstore(request,user_id,document_id)
    await delete_file_from_database(user_id,document_id,db)
    return "File deleted successfully."


async def get_document_urls_from_s3(data:DocumentURLRequest,user_id:int,db:AsyncSession):
    result = await db.execute(
            select(models.Document).where(
                models.Document.id.in_(data.document_ids),
                models.Document.user_id == user_id
            )
        )
    documents = result.scalars().all()
    return {
        "documents": [
            {
                "document_id": document.id,
                "filename": document.filename,
                "url": generate_presigned_url(
                        s3_key=document.s3_key,
                        expires_in=300
                )
            }
            for document in documents
        ]
    }