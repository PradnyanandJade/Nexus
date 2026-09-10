from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_db
from app.schemas.User import (
    UserCreate, UserResponse, LoginRequest, TokenResponse, RefreshTokenRequest
)
from app.services.auth_service import (
    create_user, authenticate_user, store_refresh_token, 
    verify_refresh_token, revoke_refresh_token, revoke_all_user_tokens, get_user_by_id
)
from app.utils.security import create_access_token, create_refresh_token, decode_token
from app.api.dependencies import get_current_user
from app.database.models import User

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Register a new user
    Returns both access and refresh tokens
    """
    user = await create_user(db, user_data)

    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # Store refresh token in database
    await store_refresh_token(db, user.id, refresh_token)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=user
    )

@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest, db: AsyncSession = Depends(get_db)):
    """
    Login with username and password
    Returns both access and refresh tokens
    """
    user = await authenticate_user(db, credentials.username, credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # Store refresh token in database
    await store_refresh_token(db, user.id, refresh_token)
    
    user_response = UserResponse.model_validate(user)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=user_response
    )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a new access token using refresh token
    
    Frontend flow:
    1. Access token expires after 15 minutes
    2. Automatically call this endpoint with refresh token
    3. Get new access token
    4. Continue making API calls
    """
    # Decode refresh token
    print(request)
    payload = decode_token(request.refresh_token)
    print(payload)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    user_id = int(user_id)

    # Verify token is in database and not revoked

    is_valid = await verify_refresh_token(
        db=db,
        user_id=user_id,
        token=request.refresh_token
    )

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired or revoked"
        )
    
    # Get user
    user = await get_user_by_id(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Create new access token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    user_response = UserResponse.model_validate(user)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=request.refresh_token,  # Return same refresh token
        user=user_response
    )


@router.post("/logout")
async def logout(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Logout user by revoking refresh token
    """
    await revoke_refresh_token(db=db, token=request.refresh_token)
    return {"message": "Successfully logged out"}

@router.post("/logout-all")
async def logout_all_devices(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Logout from all devices by revoking all refresh tokens
    """
    await revoke_all_user_tokens(db=db, user_id=current_user.id)
    return {"message": "Logged out from all devices"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user info
    Protected route - requires valid access token
    """
    return UserResponse.model_validate(current_user)