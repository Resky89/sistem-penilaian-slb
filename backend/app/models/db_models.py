import datetime
from sqlalchemy import Column, Integer, String, Date, DateTime, Enum, ForeignKey, Float, Text, JSON
from sqlalchemy.orm import relationship
from app.database.connection import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(255), nullable=False)
    username = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relasi
    assessments = relationship("Assessment", back_populates="user")


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_number = Column(String(255), unique=True, nullable=False, index=True) # NIS
    full_name = Column(String(255), nullable=False)
    gender = Column(Enum("M", "F", name="student_gender"), nullable=False)
    birth_date = Column(Date, nullable=False)
    disability_category = Column(String(255), nullable=False)
    guardian_name = Column(String(255), nullable=False)
    class_level = Column(String(255), nullable=False)
    semester = Column(Enum("Odd", "Even", name="semester_type"), nullable=False)

    # Relasi
    assessments = relationship("Assessment", back_populates="student", cascade="all, delete-orphan")


class AssessmentAspect(Base):
    __tablename__ = "assessment_aspects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    aspect_name = Column(String(255), nullable=False)
    aspect_type = Column(Enum("quantitative", "qualitative", name="aspect_type"), nullable=False)

    # Relasi
    report_scores = relationship("ReportScore", back_populates="aspect", cascade="all, delete-orphan")
    portfolio_scores = relationship("PortfolioScore", back_populates="aspect", cascade="all, delete-orphan")


class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    academic_year = Column(String(255), nullable=False)
    semester = Column(Enum("Odd", "Even", name="semester_type"), nullable=False)
    assessment_date = Column(Date, default=datetime.date.today, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relasi
    student = relationship("Student", back_populates="assessments")
    user = relationship("User", back_populates="assessments")
    report_scores = relationship("ReportScore", back_populates="assessment", cascade="all, delete-orphan")
    portfolio_scores = relationship("PortfolioScore", back_populates="assessment", cascade="all, delete-orphan")
    prediction = relationship("Prediction", back_populates="assessment", uselist=False, cascade="all, delete-orphan")


class ReportScore(Base):
    __tablename__ = "report_scores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    aspect_id = Column(Integer, ForeignKey("assessment_aspects.id"), nullable=False)
    numeric_score = Column(Float, nullable=False)

    # Relasi
    assessment = relationship("Assessment", back_populates="report_scores")
    aspect = relationship("AssessmentAspect", back_populates="report_scores")

    @property
    def aspect_name(self) -> str:
        return self.aspect.aspect_name if self.aspect else ""


class PortfolioScore(Base):
    __tablename__ = "portfolio_scores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    aspect_id = Column(Integer, ForeignKey("assessment_aspects.id"), nullable=False)
    narrative_description = Column(Text, nullable=False)

    # Relasi
    assessment = relationship("Assessment", back_populates="portfolio_scores")
    aspect = relationship("AssessmentAspect", back_populates="portfolio_scores")

    @property
    def aspect_name(self) -> str:
        return self.aspect.aspect_name if self.aspect else ""


class Prediction(Base):
    __tablename__ = "prediction"

    id = Column(Integer, primary_key=True, autoincrement=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), unique=True, nullable=False)
    development_status = Column(String(255), nullable=False)
    probability_score = Column(Float, nullable=True)
    iep_recommendation = Column(Text, nullable=False)
    shap_explanation = Column(JSON, nullable=True)

    # Relasi
    assessment = relationship("Assessment", back_populates="prediction")
