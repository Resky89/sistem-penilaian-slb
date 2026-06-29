from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.db_models import Student, AssessmentAspect, Assessment, User
from app.schemas.assessment import (
    StudentCreate, StudentResponse, StudentUpdate,
    AssessmentAspectCreate, AssessmentAspectResponse, AssessmentAspectUpdate,
    AssessmentCreate, AssessmentResponse
)
from app.repositories.student import StudentRepository
from app.repositories.aspect import AspectRepository
from app.repositories.assessment import AssessmentRepository
from app.services.ml_service import MLService
from typing import List

class AssessmentController:
    # --- STUDENT OPERATIONS ---
    @staticmethod
    def create_student(db: Session, student: StudentCreate) -> StudentResponse:
        # Cek duplikasi NIS
        db_student = StudentRepository.get_by_student_number(db, student.student_number)
        if db_student:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Siswa dengan NIS {student.student_number} sudah terdaftar"
            )
        return StudentRepository.create(db, student)

    @staticmethod
    def get_all_students(db: Session) -> List[StudentResponse]:
        return StudentRepository.get_all(db)

    # --- ASPECT OPERATIONS ---
    @staticmethod
    def create_aspect(db: Session, aspect: AssessmentAspectCreate) -> AssessmentAspectResponse:
        return AspectRepository.create(db, aspect)

    @staticmethod
    def get_all_aspects(db: Session) -> List[AssessmentAspectResponse]:
        return AspectRepository.get_all(db)

    # --- TRANSACTION ASSESSMENT & PREDICTION ---
    @staticmethod
    def create_assessment(db: Session, assessment_in: AssessmentCreate, current_user: User) -> AssessmentResponse:
        # 1. Validasi Siswa
        student = StudentRepository.get_by_id(db, assessment_in.student_id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Siswa dengan ID {assessment_in.student_id} tidak ditemukan"
            )

        # 2. Validasi & Ambil data Aspek untuk Report Scores (Kuantitatif)
        numeric_scores = []
        aspect_names = []
        for r_score in assessment_in.report_scores:
            aspect = AspectRepository.get_by_id(db, r_score.aspect_id)
            if not aspect or aspect.aspect_type != "quantitative":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Aspek ID {r_score.aspect_id} tidak valid untuk penilaian kuantitatif"
                )
            numeric_scores.append(r_score.numeric_score)
            aspect_names.append(aspect.aspect_name)

        # 3. Validasi & Ambil data Aspek untuk Portfolio Scores (Kualitatif)
        narrative_texts = []
        for p_score in assessment_in.portfolio_scores:
            aspect = AspectRepository.get_by_id(db, p_score.aspect_id)
            if not aspect or aspect.aspect_type != "qualitative":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Aspek ID {p_score.aspect_id} tidak valid untuk penilaian kualitatif"
                )
            narrative_texts.append(p_score.narrative_description)
            aspect_names.append(aspect.aspect_name)

        if not numeric_scores and not narrative_texts:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Penilaian harus berisi minimal satu skor kuantitatif atau deskripsi kualitatif"
            )

        # 4. Agregasi data untuk input ke model Machine Learning (Random Forest)
        avg_nilai = sum(numeric_scores) / len(numeric_scores) if numeric_scores else 0.0
        combined_text = " ".join(narrative_texts) if narrative_texts else ""
        combined_aspect_name = ", ".join(list(set(aspect_names))) if aspect_names else "Capaian Belajar"

        # 5. Jalankan Prediksi ML & SHAP
        try:
            prediction_res = MLService.predict(
                numeric_score=avg_nilai,
                narrative_text=combined_text,
                aspect_name=combined_aspect_name
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal memproses prediksi Machine Learning: {str(e)}"
            )

        # 6. Jalankan Transaksi Simpan Database
        try:
            created_assessment = AssessmentRepository.create_transaction(
                db=db,
                assessment_in=assessment_in,
                user_id=current_user.id,
                prediction_result=prediction_res
            )
            return created_assessment
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal menyimpan data penilaian ke MySQL: {str(e)}"
            )

    @staticmethod
    def get_all_assessments(db: Session) -> List[AssessmentResponse]:
        return AssessmentRepository.get_all(db)

    @staticmethod
    def get_assessments_by_student(db: Session, student_id: int) -> List[AssessmentResponse]:
        student = StudentRepository.get_by_id(db, student_id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Siswa dengan ID {student_id} tidak ditemukan"
            )
        return AssessmentRepository.get_by_student_id(db, student_id)

    # --- CRUD SISWA (UPDATE & DELETE) ---
    @staticmethod
    def update_student(db: Session, student_id: int, student: StudentUpdate) -> StudentResponse:
        db_student = StudentRepository.get_by_id(db, student_id)
        if not db_student:
            raise HTTPException(
                status_code=status.HTTP_444_RESOURCE_NOT_FOUND if False else status.HTTP_404_NOT_FOUND,
                detail=f"Siswa dengan ID {student_id} tidak ditemukan"
            )
        
        # Jika NIS (student_number) diubah, validasi duplikasi NIS
        if student.student_number and student.student_number != db_student.student_number:
            conflict_student = StudentRepository.get_by_student_number(db, student.student_number)
            if conflict_student:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Siswa dengan NIS {student.student_number} sudah terdaftar"
                )
        
        updated_student = StudentRepository.update(db, student_id, student.dict(exclude_unset=True))
        return updated_student

    @staticmethod
    def delete_student(db: Session, student_id: int) -> bool:
        db_student = StudentRepository.get_by_id(db, student_id)
        if not db_student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Siswa dengan ID {student_id} tidak ditemukan"
            )
        return StudentRepository.delete(db, student_id)

    # --- CRUD ASPEK (UPDATE & DELETE) ---
    @staticmethod
    def update_aspect(db: Session, aspect_id: int, aspect: AssessmentAspectUpdate) -> AssessmentAspectResponse:
        db_aspect = AspectRepository.get_by_id(db, aspect_id)
        if not db_aspect:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Aspek penilaian dengan ID {aspect_id} tidak ditemukan"
            )
        updated_aspect = AspectRepository.update(db, aspect_id, aspect.dict(exclude_unset=True))
        return updated_aspect

    @staticmethod
    def delete_aspect(db: Session, aspect_id: int) -> bool:
        db_aspect = AspectRepository.get_by_id(db, aspect_id)
        if not db_aspect:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Aspek penilaian dengan ID {aspect_id} tidak ditemukan"
            )
        return AspectRepository.delete(db, aspect_id)
