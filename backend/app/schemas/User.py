from pydantic import BaseModel, Field
from datetime import datetime

class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    password : str = Field(min_length=3, max_length=255)

class UserResponse(BaseModel):
    id: int
    username: str
    created_at: datetime
    model_config = {
        "from_attributes": True
    }

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class TokenData(BaseModel):
    user_id: int | None = None