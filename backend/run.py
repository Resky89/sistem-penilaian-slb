import os
import sys

# Paksa Python untuk mendahulukan library di venv/site-packages agar terhindar dari modul usang di python global
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
venv_site_packages = os.path.join(base_dir, "venv", "Lib", "site-packages")
if os.path.exists(venv_site_packages):
    sys.path.insert(0, venv_site_packages)

# Hapus cache typing_extensions dari sys.modules agar Python me-load ulang versi terbaru dari venv
if 'typing_extensions' in sys.modules:
    del sys.modules['typing_extensions']

import uvicorn

if __name__ == "__main__":
    # Menjalankan server lokal FastAPI di port 8001 dengan fitur reload otomatis
    # Uvicorn akan membaca inisialisasi aplikasi dari modul 'app' di folder yang sama
    uvicorn.run("app:app", host="127.0.0.1", port=8001, reload=True)
