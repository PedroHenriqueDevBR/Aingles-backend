from typing import Annotated
import os

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlmodel import select

from models.user_model import User
from services.sqlite_service import get_session
from schemas.auth_schema import UserResponse

# Security scheme for JWT Bearer tokens
security = HTTPBearer()

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET", "your-secret-key-change-this")
ALGORITHM = "HS256"


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> UserResponse:
    token = credentials.credentials

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode JWT token
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        user_id: str = payload.get("sub")
        email: str = payload.get("email")

        if user_id is None or email is None:
            raise credentials_exception

        # Get user from database
        session = next(get_session())
        user = session.exec(select(User).where(User.id == int(user_id))).first()

        if not user:
            raise credentials_exception

        # Build user response
        user_response = UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            created_at=user.created_at,
            last_sign_in_at=user.last_sign_in_at,
            email_confirmed_at=user.email_confirmed_at,
        )

        session.close()
        return user_response

    except JWTError:
        raise credentials_exception
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication error: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_active_user(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
) -> UserResponse:
    if not current_user.email_confirmed_at:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not confirmed. Please verify your email address.",
        )

    return current_user


CurrentUser = Annotated[UserResponse, Depends(get_current_user)]
CurrentActiveUser = Annotated[UserResponse, Depends(get_current_active_user)]
