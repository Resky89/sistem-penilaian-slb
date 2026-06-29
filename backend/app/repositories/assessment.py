from sqlalchemy.orm import Session
from app.models.db_models import Assessment, ReportScore, PortfolioScore, Prediction
from app.schemas.assessment import AssessmentCreate
from typing import List, Dict, Any

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
        Menyimpan data penilaian secara transaksional (ACID):
        1. Menyimpan data header di tabel 'assessments'
        2. Menyimpan detail nilai angka di tabel 'report_scores'
        3. Menyimpan detail deskripsi naratif di tabel 'portfolio_scores'
        4. Menyimpan hasil prediksi Machine Learning di tabel 'prediction'
        """
        try:
            # 1. Buat Header Assessment
            db_assessment = Assessment(
                student_id=assessment_in.student_id,
                user_id=user_id,
                academic_year=assessment_in.academic_year,
                semester=assessment_in.semester,
                assessment_date=assessment_in.assessment_date
            )
            db.add(db_assessment)
            db.flush() # Mendapatkan ID assessment untuk dihubungkan ke child record

            # 2. Simpan Report Scores (Kuantitatif)
            for r_score in assessment_in.report_scores:
                db_report = ReportScore(
                    assessment_id=db_assessment.id,
                    aspect_id=r_score.aspect_id,
                    numeric_score=r_score.numeric_score
                )
                db.add(db_report)

            # 3. Simpan Portfolio Scores (Kualitatif)
            for p_score in assessment_in.portfolio_scores:
                db_portfolio = PortfolioScore(
                    assessment_id=db_assessment.id,
                    aspect_id=p_score.aspect_id,
                    narrative_description=p_score.narrative_description
                )
                db.add(db_portfolio)

            # 4. Simpan Hasil Prediksi ML
            db_prediction = Prediction(
                assessment_id=db_assessment.id,
                development_status=prediction_result["development_status"],
                probability_score=prediction_result.get("probability_score"),
                iep_recommendation=prediction_result["iep_recommendation"],
                shap_explanation=prediction_result.get("shap_explanation")
            )
            db.add(db_prediction)

            # Commit seluruh transaksi
            db.commit()
            db.refresh(db_assessment)
            return db_assessment
        except Exception as e:
            db.rollback() # Rollback jika terjadi kesalahan agar database tetap konsisten
            raise e
