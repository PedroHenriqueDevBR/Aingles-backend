import os
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlmodel import select

from models.auth_models import TokenBlacklist
from models.user_models import User
from schemas.auth_schema import AuthenticatedUserResponse
from services.sqlite_service import get_session

# Security scheme for JWT Bearer tokens
security = HTTPBearer()

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET", "your-secret-key-change-this")
ALGORITHM = "HS256"


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> AuthenticatedUserResponse:
    session = next(get_session())
    token = credentials.credentials

    blacklist_entry = session.exec(
        select(TokenBlacklist).where(TokenBlacklist.token == token)
    ).first()

    if blacklist_entry:
        session.close()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")

        if user_id is None:
            raise credentials_exception

        user = session.exec(select(User).where(User.id == UUID(user_id))).first()

        if not user:
            raise credentials_exception

        user_response = AuthenticatedUserResponse(
            id=str(user.id),
            email=user.email or "",
            username=user.username,
            name=user.name or "",
            is_active=user.is_active,
            is_superuser=user.is_superuser,
        )
        session.close()
        return user_response

    except JWTError as err:
        raise credentials_exception from err
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication error: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


async def get_current_active_user(
    current_user: Annotated[AuthenticatedUserResponse, Depends(get_current_user)],
) -> AuthenticatedUserResponse:
    if not current_user.email_confirmed_at:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not confirmed. Please verify your email address.",
        )

    return current_user


CurrentUser = Annotated[AuthenticatedUserResponse, Depends(get_current_user)]
CurrentActiveUser = Annotated[
    AuthenticatedUserResponse, Depends(get_current_active_user)
]
