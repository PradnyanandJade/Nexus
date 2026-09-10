from sqlalchemy.ext.asyncio import (create_async_engine,AsyncSession,async_sessionmaker)
from app.config import settings
from app.database import models


engine = create_async_engine(settings.SQL_ALCHEMY_POSTGRES_URL,echo=False,pool_pre_ping=True,pool_recycle=1800,)
AsyncSessionLocal = async_sessionmaker(bind=engine,class_=AsyncSession,expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as db:
        yield db

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)