from langchain_openai import OpenAIEmbeddings
from app.config import settings

embedding = OpenAIEmbeddings(
    model=settings.OPENAI_EMBEDDING_MODEL_NAME,
    dimensions=settings.PINECONE_DIMENSION,
    api_key=settings.OPENAI_API_KEY
)

