from pydantic_settings import BaseSettings,SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
APP_DIR = BASE_DIR / "app"
UPLOADS_DIR = BASE_DIR / "uploads"

UPLOADS_DIR.mkdir(parents=True,exist_ok=True)

class Settings(BaseSettings):
    OPENAI_API_KEY : str
    OPENAI_MODEL_NAME : str 
    OPENAI_EMBEDDING_MODEL_NAME: str
    ROUTER_MAX_TOKENS : int
    REWRITE_MAX_TOKENS : int
    SUMMARY_MAX_TOKENS : int
    ANSWER_MAX_TOKENS : int
    GUARDRAIL_MAX_TOKENS : int
    PINECONE_DIMENSION : int
    HUGGINGFACE_MODEL_NAME: str
    HUGGINGFACE_EMBEDDING_MODEL_NAME : str
    HF_TOKEN : str
    PINECONE_API_KEY : str
    PINECONE_DENSE_INDEX_NAME : str
    PINECONE_SPARSE_INDEX_NAME : str
    TAVILY_API_KEY : str
    CHECKPOINTER_POSTGRES_URL : str
    SQL_ALCHEMY_POSTGRES_URL : str
    CHUNK_SIZE : int
    CHUNK_OVERLAP : int
    JWT_SECRET_KEY : str
    JWT_ALGORITHM : str
    ACCESS_TOKEN_EXPIRATION_MINUTES : int
    REFRESH_TOKEN_EXPIRATION_DAYS : int 
    COHERE_API_KEY : str
    MAX_HISTORY_TOKENS : int
    RECENT_MESSAGE_COUNT : int
    
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str = "ap-south-1"
    AWS_S3_BUCKET: str
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()