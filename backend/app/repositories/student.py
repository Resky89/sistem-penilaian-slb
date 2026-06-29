from sqlalchemy.orm import Session
from app.models.db_models import Student
from app.schemas.assessment import StudentCreate
from typing import List

class StudentRepository:
    @staticmethod
    def get_all(db: Session) -> List[Student]:
        return db.query(Student).all()

    @staticmethod
    def get_by_id(db: Session, student_id: int) -> Student:
        return db.query(Student).filter(Student.id == student_id).first()

    @staticmethod
    def get_by_student_number(db: Session, student_number: str) -> Student:
        return db.query(Student).filter(Student.student_number == student_number).first()

    @staticmethod
    def create(db: Session, student: StudentCreate) -> Student:
        db_student = Student(
            student_number=student.student_number,
            full_name=student.full_name,
            gender=student.gender,
            birth_date=student.birth_date,
            disability_category=student.disability_category,
            guardian_name=student.guardian_name,
            class_level=student.class_level,
            semester=student.semester
        )
        db.add(db_student)
        db.commit()
        db.refresh(db_student)
        return db_student

    @staticmethod
    def update(db: Session, student_id: int, student_data: dict) -> Student:
        db_student = db.query(Student).filter(Student.id == student_id).first()
        if db_student:
            for key, value in student_data.items():
                if value is not None:
                    setattr(db_student, key, value)
            db.commit()
            db.refresh(db_student)
        return db_student

    @staticmethod
    def delete(db: Session, student_id: int) -> bool:
        db_student = db.query(Student).filter(Student.id == student_id).first()
        if db_student:
            db.delete(db_student)
            db.commit()
            return True
        return False
