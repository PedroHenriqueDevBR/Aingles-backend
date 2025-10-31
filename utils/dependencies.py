from typing import Annotated
import os

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt.exceptions import InvalidTokenError

from services.supabase_service import get_supabase_client
from schemas.auth_schema import UserResponse

# Security scheme for JWT Bearer tokens
security = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> UserResponse:
    """
    Dependency to get the current authenticated user from JWT token.

    This validates the JWT token from the Authorization header and returns
    the user information. Use this dependency in protected routes.

    Args:
        credentials: HTTP Authorization credentials with Bearer token

    Returns:
        UserResponse: The authenticated user's information

    Raises:
        HTTPException 401: If token is invalid or expired

    Example:
        ```python
        @router.get("/protected")
        async def protected_route(
            current_user: Annotated[UserResponse, Depends(get_current_user)]
        ):
            return {"message": f"Hello {current_user.email}"}
        ```
    """
    token = credentials.credentials

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        jwt_secret = os.getenv("SUPABASE_JWT_SECRET")

        if not jwt_secret:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="JWT secret not configured",
            )

        payload = jwt.decode(
            token,
            jwt_secret,
            algorithms=["HS256"],
            audience="authenticated",
        )

        user_id: str = payload.get("sub")
        email: str = payload.get("email")

        if user_id is None or email is None:
            raise credentials_exception

        supabase = get_supabase_client()

        try:
            user_response = supabase.auth.get_user(token)

            if not user_response.user:
                raise credentials_exception

            # Build user response
            user = UserResponse(
                id=user_response.user.id,
                email=user_response.user.email or email,
                username=user_response.user.user_metadata.get("username"),
                created_at=user_response.user.created_at,
                last_sign_in_at=user_response.user.last_sign_in_at,
                email_confirmed_at=user_response.user.email_confirmed_at,
            )

            return user

        except Exception as e:
            # If Supabase call fails, return basic user info from JWT
            return UserResponse(
                id=user_id,
                email=email,
                username=payload.get("user_metadata", {}).get("username"),
            )

    except InvalidTokenError:
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
    """
    Dependency to get the current active user.

    Validates that the user's email is confirmed.
    Use this for routes that require email verification.

    Args:
        current_user: The current authenticated user

    Returns:
        UserResponse: The authenticated and verified user

    Raises:
        HTTPException 403: If user's email is not confirmed
    """
    if not current_user.email_confirmed_at:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not confirmed. Please verify your email address.",
        )

    return current_user


CurrentUser = Annotated[UserResponse, Depends(get_current_user)]
CurrentActiveUser = Annotated[UserResponse, Depends(get_current_active_user)]
