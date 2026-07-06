from flask_openapi3 import APIBlueprint, Tag
from flask import g
from app.schemas.auth import UserCreate, UserLogin, Token, UserResponse, RefreshTokenRequest
from app.database.connection import get_session
from app.controllers.auth import AuthController
from app.schemas.base_response import ApiResponse
from app.middleware.auth_middleware import require_auth

tag_auth = Tag(name="Authentication", description="Authentication endpoints")
auth_bp = APIBlueprint("auth", __name__, url_prefix="/api/auth", abp_tags=[tag_auth])

@auth_bp.post("/register", responses={"201": ApiResponse})
def register(body: UserCreate):
    """Mendaftarkan pengguna (guru) baru."""
    db = get_session()
    try:
        new_user = AuthController.register(db, body)
        data = UserResponse.model_validate(new_user).model_dump(mode='json')
        return {"success": True, "message": "Registrasi akun guru berhasil diproses", "data": data}, 201
    finally:
        db.close()

@auth_bp.post("/login", responses={"200": ApiResponse})
def login(body: UserLogin):
    """Masuk (login) untuk mendapatkan JWT access token."""
    db = get_session()
    try:
        token = AuthController.login(db, body)
        data = token.model_dump(mode='json')
        return {"success": True, "message": "Login sukses, token otentikasi berhasil diterbitkan", "data": data}, 200
    finally:
        db.close()

@auth_bp.post("/refresh", responses={"200": ApiResponse})
def refresh(body: RefreshTokenRequest):
    """Memperbarui access token menggunakan refresh token."""
    db = get_session()
    try:
        token = AuthController.refresh(db, body.refresh_token)
        data = token.model_dump(mode='json')
        return {"success": True, "message": "Token otentikasi berhasil diperbarui", "data": data}, 200
    finally:
        db.close()

@auth_bp.get("/me", security=[{"BearerAuth": []}], responses={"200": ApiResponse})
@require_auth
def get_me():
    """Mengambil data profil pengguna yang sedang login."""
    data = UserResponse.model_validate(g.current_user).model_dump(mode='json')
    return {"success": True, "message": "Profil pengguna berhasil diambil", "data": data}, 200

@auth_bp.post("/logout", security=[{"BearerAuth": []}], responses={"200": ApiResponse})
@require_auth
def logout():
    """Keluar (logout) dari sistem."""
    return {"success": True, "message": "Logout berhasil, sesi telah diakhiri", "data": None}, 200
