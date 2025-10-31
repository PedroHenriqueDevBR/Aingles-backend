from datetime import datetime

from fastapi import HTTPException, status
from supabase_auth.errors import AuthApiError

from schemas.auth_schema import (
    AuthResponse,
    SignInRequest,
    SignUpRequest,
    TokenResponse,
    UserResponse,
)
from services.supabase_service import get_supabase_client


class AuthService:
    """
    Service layer for handling Supabase Authentication operations.
    Handles sign up, sign in, sign out, token refresh, and user retrieval.
    """

    def __init__(self):
        self.supabase = get_supabase_client()

    async def sign_up(self, request: SignUpRequest) -> AuthResponse:
        """
        Register a new user with email and password.
        Supabase will send a confirmation email automatically if enabled.

        Args:
            request: SignUpRequest with email, password, and username

        Returns:
            AuthResponse with user data and session tokens

        Raises:
            HTTPException: If registration fails
        """
        try:
            # Sign up with Supabase Auth
            response = self.supabase.auth.sign_up(
                {
                    "email": request.email,
                    "password": request.password,
                    "options": {
                        "data": {
                            "username": request.username,
                        }
                    },
                }
            )

            if not response.user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to create user account",
                )

            user_data = UserResponse(
                id=response.user.id,
                email=response.user.email or request.email,
                username=request.username,
                created_at=response.user.created_at,
                email_confirmed_at=response.user.email_confirmed_at,
            )

            session_data = None
            if response.session:
                session_data = TokenResponse(
                    access_token=response.session.access_token,
                    refresh_token=response.session.refresh_token or "",
                    token_type="bearer",
                    expires_in=response.session.expires_in or 3600,
                    expires_at=response.session.expires_at,
                )

            return AuthResponse(user=user_data, session=session_data)

        except AuthApiError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Authentication error: {str(e)}",
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An error occurred during sign up: {str(e)}",
            )

    async def sign_in(self, request: SignInRequest) -> AuthResponse:
        """
        Authenticate user with email and password.

        Args:
            request: SignInRequest with email and password

        Returns:
            AuthResponse with user data and session tokens

        Raises:
            HTTPException: If authentication fails
        """
        try:
            # Sign in with Supabase Auth
            response = self.supabase.auth.sign_in_with_password(
                {"email": request.email, "password": request.password}
            )

            if not response.user or not response.session:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials",
                )

            # Build user response
            user_data = UserResponse(
                id=response.user.id,
                email=response.user.email or request.email,
                username=response.user.user_metadata.get("username"),
                created_at=response.user.created_at,
                last_sign_in_at=response.user.last_sign_in_at,
                email_confirmed_at=response.user.email_confirmed_at,
            )

            # Build session response
            session_data = TokenResponse(
                access_token=response.session.access_token,
                refresh_token=response.session.refresh_token or "",
                token_type="bearer",
                expires_in=response.session.expires_in or 3600,
                expires_at=response.session.expires_at,
            )

            return AuthResponse(user=user_data, session=session_data)

        except AuthApiError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Authentication failed: {str(e)}",
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An error occurred during sign in: {str(e)}",
            )

    async def sign_out(self, access_token: str) -> None:
        """
        Sign out the current user and invalidate their session.

        Args:
            access_token: The user's access token

        Raises:
            HTTPException: If sign out fails
        """
        try:
            # Set the session before signing out
            self.supabase.auth.set_session(access_token, "")
            self.supabase.auth.sign_out()

        except AuthApiError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Sign out failed: {str(e)}",
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An error occurred during sign out: {str(e)}",
            )

    async def get_user(self, access_token: str) -> UserResponse:
        """
        Get the current user's information from their access token.

        Args:
            access_token: The user's access token

        Returns:
            UserResponse with user data

        Raises:
            HTTPException: If user retrieval fails
        """
        try:
            # Get user from token
            response = self.supabase.auth.get_user(access_token)

            if not response.user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired token",
                )

            return UserResponse(
                id=response.user.id,
                email=response.user.email or "",
                username=response.user.user_metadata.get("username"),
                created_at=(
                    datetime.fromisoformat(
                        response.user.created_at.replace("Z", "+00:00")
                    )
                    if response.user.created_at
                    else None
                ),
                last_sign_in_at=(
                    datetime.fromisoformat(
                        response.user.last_sign_in_at.replace("Z", "+00:00")
                    )
                    if response.user.last_sign_in_at
                    else None
                ),
                email_confirmed_at=(
                    datetime.fromisoformat(
                        response.user.email_confirmed_at.replace("Z", "+00:00")
                    )
                    if response.user.email_confirmed_at
                    else None
                ),
            )

        except AuthApiError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Failed to get user: {str(e)}",
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An error occurred while getting user: {str(e)}",
            )

    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        """
        Refresh the user's access token using their refresh token.

        Args:
            refresh_token: The user's refresh token

        Returns:
            TokenResponse with new access and refresh tokens

        Raises:
            HTTPException: If token refresh fails
        """
        try:
            # Refresh session
            response = self.supabase.auth.refresh_session(refresh_token)

            if not response.session:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Failed to refresh token",
                )

            return TokenResponse(
                access_token=response.session.access_token,
                refresh_token=response.session.refresh_token or "",
                token_type="bearer",
                expires_in=response.session.expires_in or 3600,
                expires_at=response.session.expires_at,
            )

        except AuthApiError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token refresh failed: {str(e)}",
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An error occurred during token refresh: {str(e)}",
            )


# Singleton instance
auth_service = AuthService()
