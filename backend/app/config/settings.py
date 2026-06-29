import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str = "mysql+pymysql://root:@localhost:3306/db_penilaian_slb"
    JWT_SECRET: str = "supersecretkeyyangsangatpanjangdanaman123456!"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120

    # Mengatur agar membaca dari file .env di folder backend/
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
