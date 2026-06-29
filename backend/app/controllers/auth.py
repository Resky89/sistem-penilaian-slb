from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from app.models.db_models import User
from app.schemas.auth import UserCreate, UserLogin, Token, UserResponse
from app.repositories.user import UserRepository
from app.services.auth import AuthService
from app.database.connection import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login-oauth2")

class AuthController:
    @staticmethod
    def register(db: Session, user: UserCreate) -> UserResponse:
        # Cek apakah username sudah terdaftar
        db_user = UserRepository.get_by_username(db, user.username)
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username sudah terdaftar"
            )
        
        # Hash password dan buat user
        hashed_password = AuthService.get_password_hash(user.password)
        created_user = UserRepository.create(db, user, hashed_password)
        return created_user

    @staticmethod
    def login(db: Session, credentials: UserLogin) -> Token:
        # Cek apakah user terdaftar
        db_user = UserRepository.get_by_username(db, credentials.username)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username atau Password salah"
            )
        
        # Verifikasi password
        if not AuthService.verify_password(credentials.password, db_user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Username atau Password salah"
            )
        
        # Buat token JWT
        access_token = AuthService.create_access_token(data={"sub": db_user.username})
        refresh_token = AuthService.create_refresh_token(data={"sub": db_user.username})
        return Token(access_token=access_token, token_type="bearer", refresh_token=refresh_token)

    @staticmethod
    def refresh(db: Session, refresh_token: str) -> Token:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token tidak valid atau kadaluarsa",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        username = AuthService.verify_token(refresh_token, expected_type="refresh")
        if username is None:
            raise credentials_exception
            
        user = UserRepository.get_by_username(db, username=username)
        if user is None:
            raise credentials_exception
            
        # Buat token baru
        new_access_token = AuthService.create_access_token(data={"sub": user.username})
        new_refresh_token = AuthService.create_refresh_token(data={"sub": user.username})
        return Token(access_token=new_access_token, token_type="bearer", refresh_token=new_refresh_token)

    @staticmethod
    def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token autentikasi tidak valid atau kadaluarsa",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        username = AuthService.verify_token(token)
        if username is None:
            raise credentials_exception
            
        user = UserRepository.get_by_username(db, username=username)
        if user is None:
            raise credentials_exception
        return user
