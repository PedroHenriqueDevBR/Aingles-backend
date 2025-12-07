from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr


class SignUpRequest(BaseModel):
    email: EmailStr
    password: str
    username: str
    name: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "strongPassword123!",
                "username": "johndoe",
                "name": "John Doe",
            }
        }


class SignInRequest(BaseModel):
    username: str
    password: str

    class Config:
        json_schema_extra = {
            "example": {"username": "johndoe", "password": "strongPassword123!"}
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
    id: UUID

    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000"
            }
        }
        
class AuthenticatedUserResponse(BaseModel):
    id: str
    uuid: UUID
    email: str
    username: str
    name: str
    is_active: bool
    is_superuser: bool
    has_ai_access: bool

    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "username": "johndoe",
                "name": "John Doe",
                "is_active": True,
                "is_superuser": False
            }
        }


class AuthResponse(BaseModel):
    user: UserResponse
    session: TokenResponse | None

    class Config:
        json_schema_extra = {
            "example": {
                "user": {
                    "id": "550e8400-e29b-41d4-a716-446655440000"
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
