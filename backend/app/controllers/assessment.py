from sqlalchemy.orm import Session
from app.utils.exceptions import HTTPException, status
from app.models.db_models import Student, Assessment, User
from app.schemas.assessment import (
    StudentCreate, StudentResponse, StudentUpdate,
    AssessmentCreate, AssessmentResponse
)
from app.repositories.student import StudentRepository
from app.repositories.assessment import AssessmentRepository
from app.services.ml_service import MLService
from typing import List

# Label nama untuk setiap field skor mapel — digunakan untuk menyusun narasi
SUBJECT_SCORE_FIELDS = [
    ("pai_score", "pai_desc", "Pendidikan Agama Islam dan Budi Pekerti"),
    ("pkn_score", "pkn_desc", "Pendidikan Pancasila dan Kewarganegaraan"),
    ("ind_score", "ind_desc", "Bahasa Indonesia"),
    ("mat_score", "mat_desc", "Matematika"),
    ("ipas_score", "ipas_desc", "Ilmu Pengetahuan Alam dan Sosial"),
    ("ing_score", "ing_desc", "Bahasa Inggris"),
    ("art_score", "art_desc", "Seni Budaya"),
    ("pjok_score", "pjok_desc", "Pendidikan Jasmani, Olahraga, dan Kesehatan"),
    ("sun_score", "sun_desc", "Bahasa Sunda"),
    ("pro_score", "pro_desc", "Program Khusus"),
]

PORTFOLIO_DESC_FIELDS = [
    ("pramuka_desc", "Ekskul Pramuka"),
    ("konsentrasi_desc", "Konsentrasi"),
    ("motorik_desc", "Motorik"),
    ("interaksi_desc", "Interaksi dan Komunikasi"),
    ("emosi_desc", "Emosi"),
    ("bina_diri_desc", "Bina Diri"),
    ("membaca_desc", "Membaca"),
    ("menulis_desc", "Menulis"),
    ("berhitung_desc", "Berhitung"),
]


class AssessmentController:
    # --- STUDENT OPERATIONS ---
    @staticmethod
    def create_student(db: Session, student: StudentCreate) -> StudentResponse:
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

    @staticmethod
    def update_student(db: Session, student_id: int, student: StudentUpdate) -> StudentResponse:
        db_student = StudentRepository.get_by_id(db, student_id)
        if not db_student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Siswa dengan ID {student_id} tidak ditemukan"
            )
        if student.student_number and student.student_number != db_student.student_number:
            conflict_student = StudentRepository.get_by_student_number(db, student.student_number)
            if conflict_student:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Siswa dengan NIS {student.student_number} sudah terdaftar"
                )
        return StudentRepository.update(db, student_id, student.dict(exclude_unset=True))

    @staticmethod
    def delete_student(db: Session, student_id: int) -> bool:
        db_student = StudentRepository.get_by_id(db, student_id)
        if not db_student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Siswa dengan ID {student_id} tidak ditemukan"
            )
        return StudentRepository.delete(db, student_id)

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

        # 2. Kumpulkan nilai-nilai kuantitatif mapel dan gabungkan deskripsi untuk input ML
        numeric_scores = []
        all_desc_texts = []
        subject_names_used = []

        for score_field, desc_field, label in SUBJECT_SCORE_FIELDS:
            score_val = getattr(assessment_in, score_field, None)
            desc_val = getattr(assessment_in, desc_field, None)
            if score_val is not None:
                numeric_scores.append(score_val)
                subject_names_used.append(label)
            if desc_val:
                all_desc_texts.append(desc_val)

        for desc_field, label in PORTFOLIO_DESC_FIELDS:
            desc_val = getattr(assessment_in, desc_field, None)
            if desc_val:
                all_desc_texts.append(desc_val)
                subject_names_used.append(label)

        if not numeric_scores and not all_desc_texts:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Penilaian harus berisi minimal satu nilai atau deskripsi aspek"
            )

        # 3. Jalankan Prediksi ML & SHAP per Mapel/Aspek
        try:
            prediction_res = MLService.predict(assessment_in.dict())
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal memproses prediksi Machine Learning: {str(e)}"
            )

        # 5. Simpan ke Database
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

    @staticmethod
    def get_assessment_by_id(db: Session, assessment_id: int) -> AssessmentResponse:
        assessment = AssessmentRepository.get_by_id(db, assessment_id)
        if not assessment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Penilaian dengan ID {assessment_id} tidak ditemukan"
            )
        return assessment

    @staticmethod
    def update_assessment(db: Session, assessment_id: int, assessment_in: AssessmentCreate) -> AssessmentResponse:
        # 1. Validasi Sesi Penilaian
        db_assessment = AssessmentRepository.get_by_id(db, assessment_id)
        if not db_assessment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Penilaian dengan ID {assessment_id} tidak ditemukan"
            )

        # 2. Validasi Siswa
        student = StudentRepository.get_by_id(db, assessment_in.student_id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Siswa dengan ID {assessment_in.student_id} tidak ditemukan"
            )

        # 3. Jalankan Prediksi ML & SHAP per Mapel/Aspek
        try:
            prediction_res = MLService.predict(assessment_in.dict())
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal memproses prediksi Machine Learning: {str(e)}"
            )

        # 4. Simpan Perubahan ke Database
        try:
            updated = AssessmentRepository.update_transaction(
                db=db,
                assessment_id=assessment_id,
                assessment_in=assessment_in,
                prediction_result=prediction_res
            )
            return updated
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Gagal memperbarui data penilaian di MySQL: {str(e)}"
            )

    @staticmethod
    def delete_assessment(db: Session, assessment_id: int) -> bool:
        db_assessment = AssessmentRepository.get_by_id(db, assessment_id)
        if not db_assessment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Penilaian dengan ID {assessment_id} tidak ditemukan"
            )
        return AssessmentRepository.delete(db, assessment_id)
