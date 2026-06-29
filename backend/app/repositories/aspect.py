from sqlalchemy.orm import Session
from app.models.db_models import AssessmentAspect
from app.schemas.assessment import AssessmentAspectCreate
from typing import List

class AspectRepository:
    @staticmethod
    def get_all(db: Session) -> List[AssessmentAspect]:
        return db.query(AssessmentAspect).all()

    @staticmethod
    def get_by_id(db: Session, aspect_id: int) -> AssessmentAspect:
        return db.query(AssessmentAspect).filter(AssessmentAspect.id == aspect_id).first()

    @staticmethod
    def create(db: Session, aspect: AssessmentAspectCreate) -> AssessmentAspect:
        db_aspect = AssessmentAspect(
            aspect_name=aspect.aspect_name,
            aspect_type=aspect.aspect_type
        )
        db.add(db_aspect)
        db.commit()
        db.refresh(db_aspect)
        return db_aspect

    @staticmethod
    def update(db: Session, aspect_id: int, aspect_data: dict) -> AssessmentAspect:
        db_aspect = db.query(AssessmentAspect).filter(AssessmentAspect.id == aspect_id).first()
        if db_aspect:
            for key, value in aspect_data.items():
                if value is not None:
                    setattr(db_aspect, key, value)
            db.commit()
            db.refresh(db_aspect)
        return db_aspect

    @staticmethod
    def delete(db: Session, aspect_id: int) -> bool:
        db_aspect = db.query(AssessmentAspect).filter(AssessmentAspect.id == aspect_id).first()
        if db_aspect:
            db.delete(db_aspect)
            db.commit()
            return True
        return False
