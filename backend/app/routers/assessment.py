from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.db_models import User
from app.schemas.base_response import ApiResponse
from app.schemas.assessment import (
    StudentCreate, StudentResponse, StudentUpdate,
    AssessmentAspectCreate, AssessmentAspectResponse, AssessmentAspectUpdate,
    AssessmentCreate, AssessmentResponse
)
from app.controllers.assessment import AssessmentController
from app.controllers.auth import AuthController
from typing import List

router = APIRouter(prefix="/api", tags=["Assessments & Students"])

# --- ENDPOINTS DATA SISWA (STUDENTS) ---

@router.post("/students", response_model=ApiResponse[StudentResponse], status_code=status.HTTP_201_CREATED)
def create_student(
    student: StudentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthController.get_current_user)
):
    """Menambahkan data siswa baru (memerlukan login)."""
    new_student = AssessmentController.create_student(db, student)
    return ApiResponse(
        success=True,
        message="Data siswa berhasil ditambahkan",
        data=new_student
    )

@router.get("/students", response_model=ApiResponse[List[StudentResponse]])
def get_students(
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthController.get_current_user)
):
    """Mengambil semua daftar siswa."""
    students = AssessmentController.get_all_students(db)
    return ApiResponse(
        success=True,
        message="Daftar seluruh siswa berhasil diambil",
        data=students
    )

@router.put("/students/{student_id}", response_model=ApiResponse[StudentResponse])
def update_student(
    student_id: int,
    student: StudentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthController.get_current_user)
):
    """Mengubah data profil siswa berdasarkan ID."""
    updated = AssessmentController.update_student(db, student_id, student)
    return ApiResponse(
        success=True,
        message=f"Profil siswa dengan ID {student_id} berhasil diperbarui",
        data=updated
    )

@router.delete("/students/{student_id}", response_model=ApiResponse[None])
def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthController.get_current_user)
):
    """Menghapus data siswa dan seluruh riwayat penilaian terkait (cascade delete)."""
    AssessmentController.delete_student(db, student_id)
    return ApiResponse(
        success=True,
        message=f"Data siswa dengan ID {student_id} beserta seluruh riwayat penilaian berhasil dihapus",
        data=None
    )


# --- ENDPOINTS REFERENSI ASPEK (ASPECTS) ---

@router.post("/aspects", response_model=ApiResponse[AssessmentAspectResponse], status_code=status.HTTP_201_CREATED)
def create_aspect(
    aspect: AssessmentAspectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthController.get_current_user)
):
    """Menambahkan kategori aspek/mata pelajaran baru."""
    new_aspect = AssessmentController.create_aspect(db, aspect)
    return ApiResponse(
        success=True,
        message="Aspek penilaian baru berhasil ditambahkan",
        data=new_aspect
    )

@router.get("/aspects", response_model=ApiResponse[List[AssessmentAspectResponse]])
def get_aspects(
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthController.get_current_user)
):
    """Mengambil semua daftar aspek penilaian."""
    aspects = AssessmentController.get_all_aspects(db)
    return ApiResponse(
        success=True,
        message="Daftar seluruh aspek penilaian berhasil diambil",
        data=aspects
    )

@router.put("/aspects/{aspect_id}", response_model=ApiResponse[AssessmentAspectResponse])
def update_aspect(
    aspect_id: int,
    aspect: AssessmentAspectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthController.get_current_user)
):
    """Mengubah kategori aspek penilaian berdasarkan ID."""
    updated = AssessmentController.update_aspect(db, aspect_id, aspect)
    return ApiResponse(
        success=True,
        message=f"Kategori aspek dengan ID {aspect_id} berhasil diperbarui",
        data=updated
    )

@router.delete("/aspects/{aspect_id}", response_model=ApiResponse[None])
def delete_aspect(
    aspect_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthController.get_current_user)
):
    """Menghapus kategori aspek penilaian dan seluruh skor terkait (cascade delete)."""
    AssessmentController.delete_aspect(db, aspect_id)
    return ApiResponse(
        success=True,
        message=f"Kategori aspek dengan ID {aspect_id} beserta seluruh skor terkait berhasil dihapus",
        data=None
    )


# --- ENDPOINTS TRANSAKSI PENILAIAN & PREDIKSI ML ---

@router.post("/assessments", response_model=ApiResponse[AssessmentResponse], status_code=status.HTTP_201_CREATED)
def create_assessment(
    assessment: AssessmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthController.get_current_user)
):
    """
    Menyimpan sesi penilaian baru dan memicu model Machine Learning untuk prediksi serta kontribusi SHAP.
    """
    new_assessment = AssessmentController.create_assessment(db, assessment, current_user)
    return ApiResponse(
        success=True,
        message="Sesi penilaian dan prediksi capaian perkembangan siswa berhasil diproses dan disimpan",
        data=new_assessment
    )

@router.get("/assessments", response_model=ApiResponse[List[AssessmentResponse]])
def get_assessments(
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthController.get_current_user)
):
    """Mengambil semua daftar penilaian yang tercatat."""
    assessments = AssessmentController.get_all_assessments(db)
    return ApiResponse(
        success=True,
        message="Seluruh riwayat transaksi penilaian berhasil diambil",
        data=assessments
    )

@router.get("/assessments/student/{student_id}", response_model=ApiResponse[List[AssessmentResponse]])
def get_assessments_by_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthController.get_current_user)
):
    """Mengambil riwayat penilaian untuk siswa tertentu berdasarkan ID."""
    assessments = AssessmentController.get_assessments_by_student(db, student_id)
    return ApiResponse(
        success=True,
        message=f"Riwayat penilaian untuk siswa ID {student_id} berhasil diambil",
        data=assessments
    )
