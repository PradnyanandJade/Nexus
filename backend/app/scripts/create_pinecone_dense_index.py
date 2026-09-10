from pinecone import Pinecone,ServerlessSpec
from app.config import settings
import logging

logger = logging.getLogger(__name__)

pc = Pinecone(
    api_key=settings.PINECONE_API_KEY
)

existing_indexes = [index.name for index in pc.list_indexes()]

if settings.PINECONE_DENSE_INDEX_NAME not in existing_indexes:
    pc.create_index(
        name=settings.PINECONE_DENSE_INDEX_NAME,
        dimension=settings.PINECONE_DIMENSION,
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        )
    )
    logger.info(f"Created Pinecone dense index: {settings.PINECONE_DENSE_INDEX_NAME}")
else:
    logger.info(f"Pinecone dense index already exists: {settings.PINECONE_DENSE_INDEX_NAME}")