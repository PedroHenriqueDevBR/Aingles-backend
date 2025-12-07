import os
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlmodel import select

from models.auth_models import TokenBlacklist, TokenReference
from models.user_models import User
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
                name=request.name,
                hashed_password=hashed_password,
                created_at=datetime.utcnow(),
                email_confirmed_at=datetime.utcnow(),  # Auto-confirm for SQLite
            )

            session.add(new_user)
            session.commit()
            session.refresh(new_user)

            access_token = self.create_access_token(data={"sub": str(new_user.id)})
            refresh_token = self.create_refresh_token(data={"sub": str(new_user.id)})
            user_data = UserResponse(id=new_user.id)

            token_reference = TokenReference(
                access_token=access_token,
                refresh_token=refresh_token,
            )
            session.add(token_reference)
            session.commit()

            session_response_data = TokenResponse(
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
            return AuthResponse(user=user_data, session=session_response_data)

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

            access_token = self.create_access_token(data={"sub": str(user.id)})
            refresh_token = self.create_refresh_token(data={"sub": str(user.id)})
            user_data = UserResponse(id=user.id)

            token_reference = TokenReference(
                access_token=access_token,
                refresh_token=refresh_token,
            )
            session.add(token_reference)
            session.commit()

            session_response_data = TokenResponse(
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
            return AuthResponse(user=user_data, session=session_response_data)

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An error occurred during sign in: {str(e)}",
            ) from e

    async def sign_out(self, access_token: str) -> None:
        try:
            response = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
            # session = next(get_session())
            # session.add(TokenBlacklist(**response))
            # session.commit()
            # session.close()
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

    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        try:
            session = next(get_session())

            token_blacklist = session.exec(
                select(TokenBlacklist).where(TokenBlacklist.token == refresh_token)
            ).first()
            if token_blacklist:
                session.close()
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Refresh token has been revoked",
                )

            token_reference = session.exec(
                select(TokenReference).where(
                    TokenReference.refresh_token == refresh_token
                )
            ).first()
            if not token_reference:
                session.close()
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Refresh token not recognized",
                )

            payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: str = payload.get("sub")
            token_type: str = payload.get("type")

            if user_id is None or token_type != "refresh":
                session.close()
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token",
                )

            user = session.exec(select(User).where(User.id == UUID(user_id))).first()

            if not user:
                session.close()
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found",
                )

            # Create new tokens before blacklisting the old ones
            new_access_token = self.create_access_token(data={"sub": str(user.id)})
            new_refresh_token = self.create_refresh_token(data={"sub": str(user.id)})

            # Blacklist old tokens
            refresh_entry = TokenBlacklist(token=refresh_token)
            access_entry = TokenBlacklist(token=token_reference.access_token)
            session.add_all([refresh_entry, access_entry])

            # Add new token reference
            new_token_reference = TokenReference(
                access_token=new_access_token,
                refresh_token=new_refresh_token,
            )
            session.add(new_token_reference)
            session.commit()
            session.close()

            return TokenResponse(
                access_token=new_access_token,
                refresh_token=new_refresh_token,
                token_type="bearer",
                expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                expires_at=int((datetime.now(timezone.utc)
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


auth_service = AuthService()
