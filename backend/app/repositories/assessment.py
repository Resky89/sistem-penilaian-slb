from sqlalchemy.orm import Session
from app.models.db_models import Assessment, Prediction
from app.schemas.assessment import AssessmentCreate
from typing import List, Dict, Any

# Daftar semua field penilaian yang akan disimpan langsung ke tabel assessments
ASSESSMENT_FIELDS = [
    "pai_score", "pai_desc",
    "pkn_score", "pkn_desc",
    "ind_score", "ind_desc",
    "mat_score", "mat_desc",
    "ipas_score", "ipas_desc",
    "ing_score", "ing_desc",
    "art_score", "art_desc",
    "pjok_score", "pjok_desc",
    "sun_score", "sun_desc",
    "pro_score", "pro_desc",
    "pramuka_desc",
    "konsentrasi_desc",
    "motorik_desc",
    "interaksi_desc",
    "emosi_desc",
    "bina_diri_desc",
    "membaca_desc",
    "menulis_desc",
    "berhitung_desc",
]


class AssessmentRepository:
    @staticmethod
    def get_by_id(db: Session, assessment_id: int) -> Assessment:
        return db.query(Assessment).filter(Assessment.id == assessment_id).first()

    @staticmethod
    def get_by_student_id(db: Session, student_id: int) -> List[Assessment]:
        return db.query(Assessment).filter(Assessment.student_id == student_id).all()

    @staticmethod
    def get_all(db: Session) -> List[Assessment]:
        return db.query(Assessment).all()

    @staticmethod
    def create_transaction(
        db: Session,
        assessment_in: AssessmentCreate,
        user_id: int,
        prediction_result: Dict[str, Any]
    ) -> Assessment:
        """
        Menyimpan data penilaian secara transaksional (ACID).
        Seluruh nilai mata pelajaran dan deskripsi aspek disimpan langsung
        sebagai kolom di tabel 'assessments'.
        """
        try:
            # Bangun kwargs dari field penilaian yang ada di request
            assessment_kwargs = {
                field: getattr(assessment_in, field, None)
                for field in ASSESSMENT_FIELDS
            }

            db_assessment = Assessment(
                student_id=assessment_in.student_id,
                user_id=user_id,
                academic_year=assessment_in.academic_year,
                semester=assessment_in.semester,
                assessment_date=assessment_in.assessment_date,
                **assessment_kwargs
            )
            db.add(db_assessment)
            db.flush()  # Dapatkan ID assessment untuk relasi Prediction

            # Simpan Hasil Prediksi ML
            db_prediction = Prediction(
                assessment_id=db_assessment.id,
                development_status=prediction_result["development_status"],
                probability_score=prediction_result.get("probability_score"),
                iep_recommendation=prediction_result["iep_recommendation"],
                shap_explanation=prediction_result.get("shap_explanation")
            )
            db.add(db_prediction)

            db.commit()
            db.refresh(db_assessment)
            return db_assessment
        except Exception as e:
            db.rollback()
            raise e

    @staticmethod
    def update_transaction(
        db: Session,
        assessment_id: int,
        assessment_in: AssessmentCreate,
        prediction_result: Dict[str, Any]
    ) -> Assessment:
        """
        Mengubah data penilaian secara transaksional (ACID).
        """
        try:
            db_assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
            if not db_assessment:
                return None

            # Update fields
            db_assessment.student_id = assessment_in.student_id
            db_assessment.academic_year = assessment_in.academic_year
            db_assessment.semester = assessment_in.semester
            db_assessment.assessment_date = assessment_in.assessment_date

            for field in ASSESSMENT_FIELDS:
                setattr(db_assessment, field, getattr(assessment_in, field, None))

            # Update prediction
            db_prediction = db_assessment.prediction
            if db_prediction:
                db_prediction.development_status = prediction_result["development_status"]
                db_prediction.probability_score = prediction_result.get("probability_score")
                db_prediction.iep_recommendation = prediction_result["iep_recommendation"]
                db_prediction.shap_explanation = prediction_result.get("shap_explanation")
            else:
                db_prediction = Prediction(
                    assessment_id=db_assessment.id,
                    development_status=prediction_result["development_status"],
                    probability_score=prediction_result.get("probability_score"),
                    iep_recommendation=prediction_result["iep_recommendation"],
                    shap_explanation=prediction_result.get("shap_explanation")
                )
                db.add(db_prediction)

            db.commit()
            db.refresh(db_assessment)
            return db_assessment
        except Exception as e:
            db.rollback()
            raise e

    @staticmethod
    def delete(db: Session, assessment_id: int) -> bool:
        db_assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
        if not db_assessment:
            return False
        try:
            db.delete(db_assessment)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise e
