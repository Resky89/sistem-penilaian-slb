from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional


# --- STUDENT SCHEMAS ---
class StudentCreate(BaseModel):
    student_number: str = Field(..., description="Nomor Induk Siswa (NIS)")
    full_name: str
    class_level: str
    semester: str = Field(..., pattern="^(Odd|Even)$")
    disability_category: str = Field(..., description="Kategori Disabilitas, e.g. Tunagrahita Ringan C")
    school_name: str = Field(..., description="Nama Sekolah")
    academic_year: str = Field(..., description="Tahun Ajaran, contoh 2025/2026")


class StudentResponse(StudentCreate):
    id: int

    class Config:
        from_attributes = True


class StudentUpdate(BaseModel):
    student_number: Optional[str] = Field(None, description="Nomor Induk Siswa (NIS)")
    full_name: Optional[str] = None
    class_level: Optional[str] = None
    semester: Optional[str] = Field(None, pattern="^(Odd|Even)$")
    disability_category: Optional[str] = Field(None, description="Kategori Disabilitas")
    school_name: Optional[str] = None
    academic_year: Optional[str] = None


# --- TRANSACTION ASSESSMENT SCHEMAS ---
class AssessmentCreate(BaseModel):
    student_id: int
    academic_year: str
    semester: str = Field(..., pattern="^(Odd|Even)$")
    assessment_date: date

    # Mata Pelajaran (Nilai + Deskripsi)
    pai_score: Optional[float] = Field(None, ge=0, le=100)
    pai_desc: Optional[str] = None

    pkn_score: Optional[float] = Field(None, ge=0, le=100)
    pkn_desc: Optional[str] = None

    ind_score: Optional[float] = Field(None, ge=0, le=100)
    ind_desc: Optional[str] = None

    mat_score: Optional[float] = Field(None, ge=0, le=100)
    mat_desc: Optional[str] = None

    ipas_score: Optional[float] = Field(None, ge=0, le=100)
    ipas_desc: Optional[str] = None

    ing_score: Optional[float] = Field(None, ge=0, le=100)
    ing_desc: Optional[str] = None

    art_score: Optional[float] = Field(None, ge=0, le=100)
    art_desc: Optional[str] = None

    pjok_score: Optional[float] = Field(None, ge=0, le=100)
    pjok_desc: Optional[str] = None

    sun_score: Optional[float] = Field(None, ge=0, le=100)
    sun_desc: Optional[str] = None

    pro_score: Optional[float] = Field(None, ge=0, le=100)
    pro_desc: Optional[str] = None

    # Aspek Portofolio (Deskripsi saja)
    pramuka_desc: Optional[str] = None
    konsentrasi_desc: Optional[str] = None
    motorik_desc: Optional[str] = None
    interaksi_desc: Optional[str] = None
    emosi_desc: Optional[str] = None
    bina_diri_desc: Optional[str] = None
    membaca_desc: Optional[str] = None
    menulis_desc: Optional[str] = None
    berhitung_desc: Optional[str] = None


# --- PREDICTION / ML SCHEMAS ---
class PredictionResponse(BaseModel):
    development_status: str
    probability_score: Optional[float] = None
    iep_recommendation: str
    shap_explanation: Optional[dict] = None

    class Config:
        from_attributes = True


# --- STUDENT EMBEDDED IN ASSESSMENT RESPONSE ---
class StudentEmbedded(BaseModel):
    id: int
    student_number: str
    full_name: str
    class_level: str
    semester: str
    disability_category: str
    school_name: str
    academic_year: str

    class Config:
        from_attributes = True


# --- TRANSACTION ASSESSMENT DETAILED RESPONSE ---
class AssessmentResponse(BaseModel):
    id: int
    student_id: int
    user_id: int
    academic_year: str
    semester: str
    assessment_date: date
    created_at: datetime

    # Mata Pelajaran
    pai_score: Optional[float] = None
    pai_desc: Optional[str] = None
    pkn_score: Optional[float] = None
    pkn_desc: Optional[str] = None
    ind_score: Optional[float] = None
    ind_desc: Optional[str] = None
    mat_score: Optional[float] = None
    mat_desc: Optional[str] = None
    ipas_score: Optional[float] = None
    ipas_desc: Optional[str] = None
    ing_score: Optional[float] = None
    ing_desc: Optional[str] = None
    art_score: Optional[float] = None
    art_desc: Optional[str] = None
    pjok_score: Optional[float] = None
    pjok_desc: Optional[str] = None
    sun_score: Optional[float] = None
    sun_desc: Optional[str] = None
    pro_score: Optional[float] = None
    pro_desc: Optional[str] = None

    # Portofolio
    pramuka_desc: Optional[str] = None
    konsentrasi_desc: Optional[str] = None
    motorik_desc: Optional[str] = None
    interaksi_desc: Optional[str] = None
    emosi_desc: Optional[str] = None
    bina_diri_desc: Optional[str] = None
    membaca_desc: Optional[str] = None
    menulis_desc: Optional[str] = None
    berhitung_desc: Optional[str] = None

    student: Optional[StudentEmbedded] = None
    prediction: Optional[PredictionResponse] = None

    class Config:
        from_attributes = True
