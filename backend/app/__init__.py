import sys
import os

# Paksa Python untuk mendahulukan library di venv/site-packages agar terhindar dari modul usang di python global
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
venv_site_packages = os.path.join(base_dir, "venv", "Lib", "site-packages")
if os.path.exists(venv_site_packages):
    sys.path.insert(0, venv_site_packages)

# Hapus cache typing_extensions dari sys.modules agar Python me-load ulang versi terbaru dari venv
if 'typing_extensions' in sys.modules:
    del sys.modules['typing_extensions']

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.routers import auth, assessment
from app.services.ml_service import MLService
from app.database.connection import Base, engine

# Manajemen pembuatan tabel database MySQL dialihkan sepenuhnya ke Alembic Migrations

app = FastAPI(
    title="Sistem Penilaian Capaian Siswa SLB - API",
    description="REST API Backend Python untuk klasifikasi perkembangan siswa menggunakan algoritma Random Forest dan visualisasi kontribusi fitur SHAP.",
    version="1.0.0"
)

# Konfigurasi CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- GLOBAL CUSTOM EXCEPTION HANDLERS ---

@app.exception_handler(StarletteHTTPException)
def http_exception_handler(request, exc: StarletteHTTPException):
    """Menyeragamkan format respon error HTTP (misal 404, 403, 401)."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "error_code": f"HTTP_{exc.status_code}",
            "details": None
        }
    )

@app.exception_handler(RequestValidationError)
def validation_exception_handler(request, exc: RequestValidationError):
    """Menyeragamkan format respon error validasi input (422) dari Pydantic."""
    details = []
    for error in exc.errors():
        # Parsing lokasi field input yang bermasalah agar mudah dibaca
        field_loc = " -> ".join([str(loc) for loc in error["loc"][1:]]) if len(error["loc"]) > 1 else str(error["loc"][0])
        details.append({
            "field": field_loc,
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": "Validasi data input gagal",
            "error_code": "VALIDATION_ERROR",
            "details": details
        }
    )

@app.exception_handler(Exception)
def general_exception_handler(request, exc: Exception):
    """Menyeragamkan format respon error internal server (500) yang tidak terduga."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "Terjadi kesalahan internal server",
            "error_code": "INTERNAL_SERVER_ERROR",
            "details": str(exc)
        }
    )

# Load ML model pada startup aplikasi agar performa request pertama cepat
@app.on_event("startup")
def startup_event():
    MLService.load_models()

# Registrasi Router Endpoints
app.include_router(auth.router)
app.include_router(assessment.router)

@app.get("/", tags=["General"])
def read_root():
    return {
        "app": "Sistem Penilaian SLB API",
        "status": "Running",
        "documentation": "/docs"
    }
