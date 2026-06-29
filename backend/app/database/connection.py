from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.engine import make_url
from app.config.settings import settings

def create_database_if_not_exists():
    """Memastikan database MySQL target ada. Jika belum ada, akan dibuat otomatis."""
    try:
        url = make_url(settings.DATABASE_URL)
        db_name = url.database
        # Koneksi ke MySQL server tanpa menyertakan nama database
        server_url = f"mysql+pymysql://{url.username or ''}:{url.password or ''}@{url.host}:{url.port or 3306}"
        temp_engine = create_engine(server_url)
        with temp_engine.connect() as conn:
            # Menggunakan isolation_level agar query dijalankan langsung
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {db_name}"))
        temp_engine.dispose()
        print(f"=== Database '{db_name}' Berhasil Diverifikasi/Dibuat Otomatis ===")
    except Exception as e:
        print(f"=== [INFO] Gagal/Melewati auto-create database (kemungkinan server belum aktif): {str(e)} ===")

# Jalankan pembuatan database otomatis
create_database_if_not_exists()

# Engine koneksi MySQL utama
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Pembuat session database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class untuk Model ORM
Base = declarative_base()

# Dependency get_db untuk manajemen session database pada request FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
