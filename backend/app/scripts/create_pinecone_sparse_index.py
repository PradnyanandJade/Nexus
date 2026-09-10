from pinecone import Pinecone,ServerlessSpec
from app.config import settings
import logging

logger = logging.getLogger(__name__)

pc = Pinecone(
    api_key=settings.PINECONE_API_KEY
)

existing_indexes = [index.name for index in pc.list_indexes()]

if settings.PINECONE_SPARSE_INDEX_NAME not in existing_indexes:
    pc.create_index(
        name=settings.PINECONE_SPARSE_INDEX_NAME,
        vector_type="sparse",
        metric="dotproduct",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        )
    )
    logger.info(f"Created Pinecone sparse index: {settings.PINECONE_SPARSE_INDEX_NAME}")
else:
    logger.info(f"Pinecone sparse index already exists: {settings.PINECONE_SPARSE_INDEX_NAME}")