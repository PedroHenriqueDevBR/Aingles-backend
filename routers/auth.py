from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from schemas.auth_schema import (
    AuthResponse,
    MessageResponse,
    RefreshTokenRequest,
    SignInRequest,
    SignUpRequest,
    TokenResponse,
    UserResponse,
)
from services.auth_service import auth_service
from utils.dependencies import CurrentUser

router = APIRouter()
security = HTTPBearer()


@router.post(
    "/signup",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="""
    Register a new user with email and password.
    
    **Note**: Aingles will send a confirmation email to the provided address.
    The user must confirm their email before they can sign in.
    """,
)
async def sign_up(request: SignUpRequest) -> AuthResponse:
    """
    Register a new user account.

    - **email**: Valid email address (will receive confirmation email)
    - **password**: Strong password (minimum 6 characters recommended)
    - **username**: Unique username for the user

    Returns user information and authentication tokens.
    """
    return await auth_service.sign_up(request)


@router.post(
    "/signin",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    summary="Sign in with email and password",
    description="""
    Authenticate a user with their email and password.
    
    Returns user information and JWT tokens (access_token and refresh_token).
    """,
)
async def sign_in(request: SignInRequest) -> AuthResponse:
    """
    Sign in an existing user.

    - **email**: User's email address
    - **password**: User's password

    Returns user information and authentication tokens.
    """
    return await auth_service.sign_in(request)


@router.post(
    "/signout",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Sign out current user",
    description="""
    Sign out the currently authenticated user and invalidate their session.
    
    Requires a valid access token in the Authorization header.
    """,
)
async def sign_out(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> MessageResponse:
    """
    Sign out the current user.

    Invalidates the user's current session.
    """
    await auth_service.sign_out(credentials.credentials)
    return MessageResponse(message="Successfully signed out")


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user information",
    description="""
    Retrieve information about the currently authenticated user.
    
    Requires a valid access token in the Authorization header.
    """,
)
async def get_me(current_user: CurrentUser) -> UserResponse:
    """
    Get the current authenticated user's information.

    Returns user details including email, username, and timestamps.
    """
    return current_user


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
    description="""
    Refresh the user's access token using their refresh token.
    
    Use this endpoint when the access token expires to obtain a new one
    without requiring the user to sign in again.
    """,
)
async def refresh_token(request: RefreshTokenRequest) -> TokenResponse:
    """
    Refresh the access token.

    - **refresh_token**: Valid refresh token from sign in/sign up response

    Returns new access and refresh tokens.
    """
    return await auth_service.refresh_token(request.refresh_token)


@router.get(
    "/verify",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Verify token validity",
    description="""
    Verify if the provided access token is valid.
    
    Useful for checking authentication status without retrieving user data.
    """,
)
async def verify_token(current_user: CurrentUser) -> MessageResponse:
    """
    Verify if the current token is valid.

    Returns a success message if the token is valid, otherwise returns 401.
    """
    return MessageResponse(message=f"Token is valid for user: {current_user.email}")
