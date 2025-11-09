from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class SignUpRequest(BaseModel):
    email: EmailStr
    password: str
    username: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "strongPassword123!",
                "username": "johndoe",
            }
        }


class SignInRequest(BaseModel):
    email: EmailStr
    password: str

    class Config:
        json_schema_extra = {
            "example": {"email": "user@example.com", "password": "strongPassword123!"}
        }


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    expires_at: Optional[int] = None


class UserResponse(BaseModel):
    id: int
    email: str
    username: Optional[str] = None
    created_at: Optional[datetime] = None
    last_sign_in_at: Optional[datetime] = None
    email_confirmed_at: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "email": "user@example.com",
                "username": "johndoe",
                "created_at": "2024-01-01T00:00:00Z",
                "last_sign_in_at": "2024-01-15T10:30:00Z",
                "email_confirmed_at": "2024-01-01T00:05:00Z",
            }
        }


class AuthResponse(BaseModel):
    user: UserResponse
    session: TokenResponse | None

    class Config:
        json_schema_extra = {
            "example": {
                "user": {
                    "id": 1,
                    "email": "user@example.com",
                    "username": "johndoe",
                },
                "session": {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "refresh_token": "v1.MQ.refresh_token...",
                    "token_type": "bearer",
                    "expires_in": 3600,
                },
            }
        }


class MessageResponse(BaseModel):
    message: str

    class Config:
        json_schema_extra = {"example": {"message": "Operation successful"}}
