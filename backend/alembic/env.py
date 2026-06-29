import os
import sys

# Paksa Python untuk mendahulukan library di venv/site-packages
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
venv_site_packages = os.path.join(base_dir, "venv", "Lib", "site-packages")
if os.path.exists(venv_site_packages):
    sys.path.insert(0, venv_site_packages)

# Hapus cache typing_extensions dari sys.modules agar Python me-load ulang versi terbaru dari venv
if 'typing_extensions' in sys.modules:
    del sys.modules['typing_extensions']

from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from alembic import context

# Tambahkan direktori root proyek (backend/) ke path Python agar modul 'app' dapat ditemukan
sys.path.insert(1, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import settings, Base, dan seluruh models agar didaftarkan ke metadata
from app.config.settings import settings
from app.database.connection import Base
from app.models import db_models # Memastikan seluruh tabel terdaftar

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Definisikan target metadata untuk autogenerate migrasi
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.
    Menggunakan URL database dinamis dari settings.py (.env)
    """
    url = settings.DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.
    Membuat database connection engine secara dinamis dari settings.py (.env)
    """
    connectable = create_engine(
        settings.DATABASE_URL,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
