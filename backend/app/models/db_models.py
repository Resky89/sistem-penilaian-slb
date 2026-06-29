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
    student_number = Column(String(255), unique=True, nullable=False, index=True)  # NIS
    full_name = Column(String(255), nullable=False)
    class_level = Column(String(255), nullable=False)
    semester = Column(Enum("Odd", "Even", name="semester_type"), nullable=False)
    disability_category = Column(String(255), nullable=False)  # Ketunaan
    school_name = Column(String(255), nullable=False)           # Nama Sekolah
    academic_year = Column(String(255), nullable=False)         # Tahun Ajaran (e.g. 2025/2026)

    # Relasi
    assessments = relationship("Assessment", back_populates="student", cascade="all, delete-orphan")


class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    academic_year = Column(String(255), nullable=False)
    semester = Column(Enum("Odd", "Even", name="semester_type"), nullable=False)
    assessment_date = Column(Date, default=datetime.date.today, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # --- Mata Pelajaran (Nilai + Deskripsi) ---
    pai_score = Column(Float, nullable=True)
    pai_desc = Column(Text, nullable=True)

    pkn_score = Column(Float, nullable=True)
    pkn_desc = Column(Text, nullable=True)

    ind_score = Column(Float, nullable=True)
    ind_desc = Column(Text, nullable=True)

    mat_score = Column(Float, nullable=True)
    mat_desc = Column(Text, nullable=True)

    ipas_score = Column(Float, nullable=True)
    ipas_desc = Column(Text, nullable=True)

    ing_score = Column(Float, nullable=True)
    ing_desc = Column(Text, nullable=True)

    art_score = Column(Float, nullable=True)
    art_desc = Column(Text, nullable=True)

    pjok_score = Column(Float, nullable=True)
    pjok_desc = Column(Text, nullable=True)

    sun_score = Column(Float, nullable=True)
    sun_desc = Column(Text, nullable=True)

    pro_score = Column(Float, nullable=True)
    pro_desc = Column(Text, nullable=True)

    # --- Aspek Portofolio (Deskripsi saja) ---
    pramuka_desc = Column(Text, nullable=True)
    konsentrasi_desc = Column(Text, nullable=True)
    motorik_desc = Column(Text, nullable=True)
    interaksi_desc = Column(Text, nullable=True)
    emosi_desc = Column(Text, nullable=True)
    bina_diri_desc = Column(Text, nullable=True)
    membaca_desc = Column(Text, nullable=True)
    menulis_desc = Column(Text, nullable=True)
    berhitung_desc = Column(Text, nullable=True)

    # Relasi
    student = relationship("Student", back_populates="assessments")
    user = relationship("User", back_populates="assessments")
    prediction = relationship("Prediction", back_populates="assessment", uselist=False, cascade="all, delete-orphan")


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
