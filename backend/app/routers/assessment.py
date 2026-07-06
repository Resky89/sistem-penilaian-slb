from flask_openapi3 import APIBlueprint, Tag
from flask import g
from pydantic import BaseModel, Field
from app.schemas.base_response import ApiResponse
from app.schemas.assessment import (
    StudentCreate, StudentResponse, StudentUpdate,
    AssessmentCreate, AssessmentResponse
)
from app.controllers.assessment import AssessmentController
from app.middleware.auth_middleware import require_auth

tag_assessment = Tag(name="Assessments & Students", description="Assessments and Students management endpoints")
assessment_bp = APIBlueprint("assessment", __name__, url_prefix="/api", abp_tags=[tag_assessment])

# --- PATH PARAMETER MODELS FOR SWAGGER ---
class StudentPath(BaseModel):
    student_id: int = Field(..., description="ID Siswa")

class AssessmentPath(BaseModel):
    assessment_id: int = Field(..., description="ID Sesi Penilaian")

# --- ENDPOINTS DATA SISWA (STUDENTS) ---

@assessment_bp.post("/students", security=[{"BearerAuth": []}], responses={"201": ApiResponse})
@require_auth
def create_student(body: StudentCreate):
    """Menambahkan data siswa baru (memerlukan login)."""
    new_student = AssessmentController.create_student(g.db, body)
    data = StudentResponse.model_validate(new_student).model_dump(mode='json')
    return {"success": True, "message": "Data siswa berhasil ditambahkan", "data": data}, 201

@assessment_bp.get("/students", security=[{"BearerAuth": []}], responses={"200": ApiResponse})
@require_auth
def get_students():
    """Mengambil semua daftar siswa."""
    students = AssessmentController.get_all_students(g.db)
    data = [StudentResponse.model_validate(s).model_dump(mode='json') for s in students]
    return {"success": True, "message": "Daftar seluruh siswa berhasil diambil", "data": data}, 200

@assessment_bp.put("/students/<int:student_id>", security=[{"BearerAuth": []}], responses={"200": ApiResponse})
@require_auth
def update_student(path: StudentPath, body: StudentUpdate):
    """Mengubah data profil siswa berdasarkan ID."""
    updated = AssessmentController.update_student(g.db, path.student_id, body)
    data = StudentResponse.model_validate(updated).model_dump(mode='json')
    return {"success": True, "message": f"Profil siswa dengan ID {path.student_id} berhasil diperbarui", "data": data}, 200

@assessment_bp.delete("/students/<int:student_id>", security=[{"BearerAuth": []}], responses={"200": ApiResponse})
@require_auth
def delete_student(path: StudentPath):
    """Menghapus data siswa dan seluruh riwayat penilaian terkait (cascade delete)."""
    AssessmentController.delete_student(g.db, path.student_id)
    return {"success": True, "message": f"Data siswa dengan ID {path.student_id} beserta seluruh riwayat penilaian berhasil dihapus", "data": None}, 200


# --- ENDPOINTS TRANSAKSI PENILAIAN & PREDIKSI ML ---

@assessment_bp.post("/assessments", security=[{"BearerAuth": []}], responses={"201": ApiResponse})
@require_auth
def create_assessment(body: AssessmentCreate):
    """
    Menyimpan sesi penilaian baru dengan semua nilai dan deskripsi mapel/aspek,
    lalu memicu prediksi Machine Learning (Random Forest + SHAP).
    """
    new_assessment = AssessmentController.create_assessment(g.db, body, g.current_user)
    data = AssessmentResponse.model_validate(new_assessment).model_dump(mode='json')
    return {"success": True, "message": "Sesi penilaian dan prediksi capaian perkembangan siswa berhasil diproses dan disimpan", "data": data}, 201

@assessment_bp.get("/assessments", security=[{"BearerAuth": []}], responses={"200": ApiResponse})
@require_auth
def get_assessments():
    """Mengambil semua daftar penilaian yang tercatat."""
    assessments = AssessmentController.get_all_assessments(g.db)
    data = [AssessmentResponse.model_validate(a).model_dump(mode='json') for a in assessments]
    return {"success": True, "message": "Seluruh riwayat transaksi penilaian berhasil diambil", "data": data}, 200

@assessment_bp.get("/assessments/student/<int:student_id>", security=[{"BearerAuth": []}], responses={"200": ApiResponse})
@require_auth
def get_assessments_by_student(path: StudentPath):
    """Mengambil riwayat penilaian untuk siswa tertentu berdasarkan ID."""
    assessments = AssessmentController.get_assessments_by_student(g.db, path.student_id)
    data = [AssessmentResponse.model_validate(a).model_dump(mode='json') for a in assessments]
    return {"success": True, "message": f"Riwayat penilaian untuk siswa ID {path.student_id} berhasil diambil", "data": data}, 200

@assessment_bp.get("/assessments/<int:assessment_id>", security=[{"BearerAuth": []}], responses={"200": ApiResponse})
@require_auth
def get_assessment(path: AssessmentPath):
    """Mengambil detail penilaian berdasarkan ID."""
    assessment = AssessmentController.get_assessment_by_id(g.db, path.assessment_id)
    data = AssessmentResponse.model_validate(assessment).model_dump(mode='json')
    return {"success": True, "message": f"Detail penilaian dengan ID {path.assessment_id} berhasil diambil", "data": data}, 200

@assessment_bp.put("/assessments/<int:assessment_id>", security=[{"BearerAuth": []}], responses={"200": ApiResponse})
@require_auth
def update_assessment(path: AssessmentPath, body: AssessmentCreate):
    """Mengubah data penilaian berdasarkan ID dan memperbarui prediksi."""
    updated = AssessmentController.update_assessment(g.db, path.assessment_id, body)
    data = AssessmentResponse.model_validate(updated).model_dump(mode='json')
    return {"success": True, "message": f"Penilaian dengan ID {path.assessment_id} berhasil diperbarui", "data": data}, 200

@assessment_bp.delete("/assessments/<int:assessment_id>", security=[{"BearerAuth": []}], responses={"200": ApiResponse})
@require_auth
def delete_assessment(path: AssessmentPath):
    """Menghapus data penilaian berdasarkan ID."""
    AssessmentController.delete_assessment(g.db, path.assessment_id)
    return {"success": True, "message": f"Penilaian dengan ID {path.assessment_id} berhasil dihapus", "data": None}, 200
