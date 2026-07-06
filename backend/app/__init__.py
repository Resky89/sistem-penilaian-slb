import sys
import os

# Paksa Python untuk mendahulukan library di venv/site-packages agar terhindar dari modul usang di python global
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
venv_site_packages_local = os.path.join(base_dir, "venv", "Lib", "site-packages")
venv_site_packages_parent = os.path.join(os.path.dirname(base_dir), "venv", "Lib", "site-packages")

if os.path.exists(venv_site_packages_local):
    sys.path.insert(0, venv_site_packages_local)
elif os.path.exists(venv_site_packages_parent):
    sys.path.insert(0, venv_site_packages_parent)

# Hapus cache typing_extensions dari sys.modules agar Python me-load ulang versi terbaru dari venv
if 'typing_extensions' in sys.modules:
    del sys.modules['typing_extensions']

import time
from collections import defaultdict
from flask_openapi3 import OpenAPI, Info
from flask_cors import CORS
from flask import jsonify, request
from app.utils.exceptions import HTTPException, status
from werkzeug.exceptions import HTTPException as WerkzeugHTTPException
from pydantic import ValidationError

info = Info(
    title="Sistem Penilaian Capaian Siswa SLB - API",
    description="REST API Backend Python untuk klasifikasi perkembangan siswa menggunakan algoritma Random Forest dan visualisasi kontribusi fitur SHAP.",
    version="1.0.0"
)

security_schemes = {
    "BearerAuth": {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT"
    }
}

def custom_validation_error_handler(e: ValidationError):
    details = []
    for error in e.errors():
        # Clean up 'loc' paths, e.g. ignoring 'body', 'query', etc. if needed,
        # but matching FastAPI loc format
        field_loc = " -> ".join([str(loc) for loc in error["loc"]])
        details.append({
            "field": field_loc,
            "message": error["msg"],
            "type": error["type"]
        })
    
    import json
    from flask import make_response
    response_body = {
        "success": False,
        "message": "Validasi data input gagal",
        "error_code": "VALIDATION_ERROR",
        "details": details
    }
    response = make_response(json.dumps(response_body))
    response.headers["Content-Type"] = "application/json"
    response.status_code = 422
    return response

app = OpenAPI(
    __name__,
    info=info,
    security_schemes=security_schemes,
    doc_prefix="/docs",
    validation_error_callback=custom_validation_error_handler
)

# Konfigurasi CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})

# --- RATE LIMITER MIDDLEWARE ---
RATE_LIMIT_REQUESTS = 60  # max requests per minute
RATE_LIMIT_WINDOW = 60    # window size in seconds
ip_request_history = defaultdict(list)

@app.before_request
def rate_limit_middleware():
    # Bypass docs, swagger, and OPTIONS preflights
    if request.path in ["/", "/docs", "/openapi.json"] or request.path.startswith("/docs") or request.method == "OPTIONS":
        return
        
    client_ip = request.remote_addr or "unknown"
    now = time.time()
    
    # Clean up history older than window
    ip_request_history[client_ip] = [
        t for t in ip_request_history[client_ip]
        if now - t < RATE_LIMIT_WINDOW
    ]
    
    if len(ip_request_history[client_ip]) >= RATE_LIMIT_REQUESTS:
        return jsonify({
            "success": False,
            "message": "Terlalu banyak permintaan. Silakan coba beberapa saat lagi.",
            "error_code": "RATE_LIMIT_EXCEEDED",
            "details": None
        }), 429
        
    ip_request_history[client_ip].append(now)

# --- GLOBAL CUSTOM EXCEPTION HANDLERS ---

@app.errorhandler(HTTPException)
def http_exception_handler(exc: HTTPException):
    """Menyeragamkan format respon error HTTP."""
    response = jsonify({
        "success": False,
        "message": exc.detail,
        "error_code": f"HTTP_{exc.status_code}",
        "details": None
    })
    response.status_code = exc.status_code
    for k, v in exc.headers.items():
        response.headers[k] = v
    return response

@app.errorhandler(WerkzeugHTTPException)
def werkzeug_http_exception_handler(exc: WerkzeugHTTPException):
    """Menyeragamkan format respon error HTTP bawaan Flask/Werkzeug."""
    return jsonify({
        "success": False,
        "message": exc.description,
        "error_code": f"HTTP_{exc.code}",
        "details": None
    }), exc.code

@app.errorhandler(ValidationError)
def pydantic_validation_error_handler(exc: ValidationError):
    """Menyeragamkan format respon error validasi input (422) dari Pydantic."""
    details = []
    for error in exc.errors():
        field_loc = " -> ".join([str(loc) for loc in error["loc"]])
        details.append({
            "field": field_loc,
            "message": error["msg"],
            "type": error["type"]
        })
    
    return jsonify({
        "success": False,
        "message": "Validasi data input gagal",
        "error_code": "VALIDATION_ERROR",
        "details": details
    }), 422

@app.errorhandler(Exception)
def general_exception_handler(exc: Exception):
    """Menyeragamkan format respon error internal server (500) yang tidak terduga."""
    print(f"[ERROR] General exception: {str(exc)}", file=sys.stderr)
    import traceback
    traceback.print_exc()
    return jsonify({
        "success": False,
        "message": "Terjadi kesalahan internal server",
        "error_code": "INTERNAL_SERVER_ERROR",
        "details": str(exc)
    }), 500

# Registrasi Router Endpoints
from app.routers.auth import auth_bp
from app.routers.assessment import assessment_bp

app.register_api(auth_bp)
app.register_api(assessment_bp)

from flask_openapi3 import Tag
tag_general = Tag(name="General", description="General info")

@app.get("/", tags=[tag_general])
def read_root():
    return {
        "app": "Sistem Penilaian SLB API (Flask)",
        "status": "Running",
        "documentation": "/docs"
    }
