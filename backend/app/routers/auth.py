from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.schemas.base_response import ApiResponse
from app.schemas.auth import UserCreate, UserLogin, Token, UserResponse
from app.controllers.auth import AuthController

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=ApiResponse[UserResponse], status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """Mendaftarkan pengguna (guru) baru."""
    new_user = AuthController.register(db, user)
    return ApiResponse(
        success=True,
        message="Registrasi akun guru berhasil diproses",
        data=new_user
    )

@router.post("/login", response_model=ApiResponse[Token])
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Masuk (login) untuk mendapatkan JWT access token."""
    token = AuthController.login(db, credentials)
    return ApiResponse(
        success=True,
        message="Login sukses, token otentikasi berhasil diterbitkan",
        data=token
    )

@router.post("/login-oauth2", response_model=Token, include_in_schema=False)
def login_oauth2(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Rute khusus untuk integrasi tombol 'Authorize' Swagger UI.
    Mengembalikan token mentah (raw Token) sesuai spesifikasi standard OAuth2.
    """
    credentials = UserLogin(username=form_data.username, password=form_data.password)
    return AuthController.login(db, credentials)
