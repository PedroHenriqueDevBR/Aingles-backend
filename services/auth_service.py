import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlmodel import select

from models.user_model import User
from schemas.auth_schema import (
    AuthResponse,
    SignInRequest,
    SignUpRequest,
    TokenResponse,
    UserResponse,
)
from services.sqlite_service import get_session

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("JWT_SECRET", "your-secret-key-change-this")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours
REFRESH_TOKEN_EXPIRE_DAYS = 30  # 30 days


class AuthService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(
        data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def create_refresh_token(
        data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    async def sign_up(self, request: SignUpRequest) -> AuthResponse:
        try:
            session = next(get_session())

            existing_user = session.exec(
                select(User).where(User.email == request.email)
            ).first()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered",
                )

            existing_username = session.exec(
                select(User).where(User.username == request.username)
            ).first()
            if existing_username:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken",
                )

            hashed_password = self.get_password_hash(request.password)
            new_user = User(
                email=request.email,
                username=request.username,
                hashed_password=hashed_password,
                created_at=datetime.utcnow(),
                email_confirmed_at=datetime.utcnow(),  # Auto-confirm for SQLite
            )

            session.add(new_user)
            session.commit()
            session.refresh(new_user)

            access_token = self.create_access_token(
                data={
                    "sub": new_user.id,
                    "email": new_user.email,
                    "username": new_user.username,
                }
            )
            refresh_token = self.create_refresh_token(
                data={
                    "sub": new_user.id,
                    "email": new_user.email,
                    "username": new_user.username,
                }
            )

            user_data = UserResponse(
                id=new_user.id,
                email=new_user.email,
                username=new_user.username,
                created_at=new_user.created_at,
                email_confirmed_at=new_user.email_confirmed_at,
            )

            session_data = TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                expires_at=int(
                    (
                        datetime.utcnow()
                        + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
                    ).timestamp()
                ),
            )

            session.close()
            return AuthResponse(user=user_data, session=session_data)

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An error occurred during sign up: {str(e)}",
            ) from e

    async def sign_in(self, request: SignInRequest) -> AuthResponse:
        try:
            session = next(get_session())

            user = session.exec(
                select(User).where(User.username == request.username)
            ).first()

            if not user or not self.verify_password(
                request.password,
                user.hashed_password,
            ):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials",
                )

            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User account is inactive",
                )

            user.last_sign_in_at = datetime.utcnow()
            session.add(user)
            session.commit()
            session.refresh(user)

            access_token = self.create_access_token(
                data={
                    "sub": str(user.id),
                    "email": user.email,
                    "username": user.username,
                }
            )
            refresh_token = self.create_refresh_token(
                data={
                    "sub": str(user.id),
                    "email": user.email,
                    "username": user.username,
                }
            )

            user_data = UserResponse(
                id=user.id,
                email=user.email,
                username=user.username,
            )

            session_data = TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                expires_at=int(
                    (
                        datetime.utcnow()
                        + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
                    ).timestamp()
                ),
            )

            session.close()
            return AuthResponse(user=user_data, session=session_data)

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An error occurred during sign in: {str(e)}",
            ) from e

    async def sign_out(self, access_token: str) -> None:
        try:
            jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        except JWTError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            ) from exc
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An error occurred during sign out: {str(e)}",
            ) from e

    async def get_user(self, access_token: str) -> UserResponse:
        try:
            payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: str = payload.get("sub")

            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired token",
                )

            session = next(get_session())
            user = session.exec(select(User).where(User.id == int(user_id))).first()

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found",
                )

            session.close()

            return UserResponse(
                id=user.id,
                email=user.email,
                username=user.username,
                created_at=user.created_at,
                last_sign_in_at=user.last_sign_in_at,
                email_confirmed_at=user.email_confirmed_at,
            )

        except JWTError as err:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            ) from err
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An error occurred while getting user: {str(e)}",
            ) from e

    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        try:
            payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: str = payload.get("sub")
            token_type: str = payload.get("type")

            if user_id is None or token_type != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token",
                )

            session = next(get_session())
            user = session.exec(select(User).where(User.id == int(user_id))).first()

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found",
                )

            session.close()

            access_token = self.create_access_token(
                data={
                    "sub": str(user.id),
                    "email": user.email,
                }
            )
            new_refresh_token = self.create_refresh_token(
                data={
                    "sub": str(user.id),
                    "email": user.email,
                }
            )

            return TokenResponse(
                access_token=access_token,
                refresh_token=new_refresh_token,
                token_type="bearer",
                expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                expires_at=int(
                    (
                        datetime.utcnow()
                        + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
                    ).timestamp()
                ),
            )

        except JWTError as err:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            ) from err
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An error occurred during token refresh: {str(e)}",
            ) from e


# Singleton instance
auth_service = AuthService()
