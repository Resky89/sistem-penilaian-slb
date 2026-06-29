from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.db_models import User
from app.schemas.base_response import ApiResponse
from app.schemas.auth import UserCreate, UserLogin, Token, UserResponse, RefreshTokenRequest
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

@router.post("/refresh", response_model=ApiResponse[Token])
def refresh(body: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Memperbarui access token menggunakan refresh token."""
    token = AuthController.refresh(db, body.refresh_token)
    return ApiResponse(
        success=True,
        message="Token otentikasi berhasil diperbarui",
        data=token
    )

@router.get("/me", response_model=ApiResponse[UserResponse])
def get_me(
    current_user: User = Depends(AuthController.get_current_user)
):
    """Mengambil data profil pengguna yang sedang login."""
    return ApiResponse(
        success=True,
        message="Profil pengguna berhasil diambil",
        data=current_user
    )

@router.post("/logout", response_model=ApiResponse[None])
def logout(
    current_user: User = Depends(AuthController.get_current_user)
):
    """Keluar (logout) dari sistem."""
    return ApiResponse(
        success=True,
        message="Logout berhasil, sesi telah diakhiri",
        data=None
    )

@router.post("/login-oauth2", response_model=Token, include_in_schema=False)
def login_oauth2(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Rute khusus untuk integrasi tombol 'Authorize' Swagger UI.
    Mengembalikan token mentah (raw Token) sesuai spesifikasi standard OAuth2.
    """
    credentials = UserLogin(username=form_data.username, password=form_data.password)
    return AuthController.login(db, credentials)
