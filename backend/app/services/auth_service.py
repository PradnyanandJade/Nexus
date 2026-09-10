from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,update
from app.database import models
from app.database.models import User, RefreshToken
from app.schemas.User import UserCreate, UserResponse
from app.utils.security import hash_password, verify_password, create_access_token, create_refresh_token
from fastapi import HTTPException, status
from datetime import datetime, timedelta, timezone
from app.config import settings

async def create_user(db: AsyncSession, user: UserCreate) -> UserResponse:
    """Create a new user with hashed password"""
    result = await db.execute(
        select(models.User)
        .where(
            models.User.username == user.username
        )
    )
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    hashed_password = hash_password(user.password)
    db_user = User(username=user.username, password_hash=hashed_password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return UserResponse.model_validate(db_user)

async def authenticate_user(db: AsyncSession, username: str, password: str) -> User | None:
    """Authenticate user by username and password"""
    result = await db.execute(
        select(User).where(
            User.username == username
        )
    )
    user = result.scalar_one_or_none()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user

async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    """Get user by ID"""
    result = await db.execute(
        select(User).where(
            User.id == user_id
        )
    )
    return result.scalar_one_or_none()


# NEW FUNCTIONS FOR REFRESH TOKEN MANAGEMENT

async def store_refresh_token(db: AsyncSession, user_id: int, token: str) -> RefreshToken:
    """Store refresh token in database"""
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRATION_DAYS)
    
    db_token = RefreshToken(
        user_id=user_id,
        token=token,
        expires_at=expires_at
    )
    db.add(db_token)
    await db.commit()
    await db.refresh(db_token)
    return db_token

async def verify_refresh_token(db: AsyncSession, user_id: int, token: str) -> bool:
    """Verify if refresh token exists and is valid"""
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.user_id == user_id,
            RefreshToken.token == token,
            RefreshToken.is_revoked.is_(False),
            RefreshToken.expires_at > datetime.now(timezone.utc)
        )
    )
    db_token = result.scalar_one_or_none()
    return db_token is not None

async def revoke_refresh_token(db: AsyncSession, token: str) -> bool:
    """Revoke a refresh token (logout)"""
    result = await db.execute(
        select(models.RefreshToken)
        .where(
            models.RefreshToken.token == token
        )
    )
    db_token = result.scalar_one_or_none()
    if not db_token:
        return False
    db_token.is_revoked = True
    await db.commit()
    return True

async def revoke_all_user_tokens(db: AsyncSession, user_id: int):
    """Revoke all refresh tokens for a user (logout from all devices)"""
    await db.execute(
        update(RefreshToken)
        .where(
            RefreshToken.user_id == user_id
        )
        .values(
            is_revoked=True
        )
    )
    await db.commit()