from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import List, Optional

# --- STUDENT SCHEMAS ---
class StudentCreate(BaseModel):
    student_number: str = Field(..., description="Nomor Induk Siswa (NIS)")
    full_name: str
    gender: str = Field(..., pattern="^(M|F)$", description="M (Male) atau F (Female)")
    birth_date: date
    disability_category: str = Field(..., description="Kategori Disabilitas, e.g. Tunagrahita Ringan C")
    guardian_name: str
    class_level: str
    semester: str = Field(..., pattern="^(Odd|Even)$")

class StudentResponse(StudentCreate):
    id: int

    class Config:
        from_attributes = True

class StudentUpdate(BaseModel):
    student_number: Optional[str] = Field(None, description="Nomor Induk Siswa (NIS)")
    full_name: Optional[str] = None
    gender: Optional[str] = Field(None, pattern="^(M|F)$", description="M (Male) atau F (Female)")
    birth_date: Optional[date] = None
    disability_category: Optional[str] = Field(None, description="Kategori Disabilitas")
    guardian_name: Optional[str] = None
    class_level: Optional[str] = None
    semester: Optional[str] = Field(None, pattern="^(Odd|Even)$")


# --- ASSESSMENT ASPECT SCHEMAS ---
class AssessmentAspectCreate(BaseModel):
    aspect_name: str
    aspect_type: str = Field(..., pattern="^(quantitative|qualitative)$")

class AssessmentAspectResponse(AssessmentAspectCreate):
    id: int

    class Config:
        from_attributes = True

class AssessmentAspectUpdate(BaseModel):
    aspect_name: Optional[str] = None
    aspect_type: Optional[str] = Field(None, pattern="^(quantitative|qualitative)$")


# --- SCORE INPUT SCHEMAS ---
class ReportScoreInput(BaseModel):
    aspect_id: int
    numeric_score: float

class PortfolioScoreInput(BaseModel):
    aspect_id: int
    narrative_description: str


# --- TRANSACTION ASSESSMENT SCHEMAS ---
class AssessmentCreate(BaseModel):
    student_id: int
    academic_year: str
    semester: str = Field(..., pattern="^(Odd|Even)$")
    assessment_date: date
    report_scores: List[ReportScoreInput]
    portfolio_scores: List[PortfolioScoreInput]


# --- PREDICTION / ML SCHEMAS ---
class PredictionResponse(BaseModel):
    development_status: str
    probability_score: Optional[float] = None
    iep_recommendation: str
    shap_explanation: Optional[dict] = None

    class Config:
        from_attributes = True


# --- SCORE DETAILED RESPONSES ---
class ReportScoreResponse(BaseModel):
    id: int
    aspect_id: int
    aspect_name: str
    numeric_score: float

    class Config:
        from_attributes = True

class PortfolioScoreResponse(BaseModel):
    id: int
    aspect_id: int
    aspect_name: str
    narrative_description: str

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
    report_scores: List[ReportScoreResponse]
    portfolio_scores: List[PortfolioScoreResponse]
    prediction: Optional[PredictionResponse] = None

    class Config:
        from_attributes = True
