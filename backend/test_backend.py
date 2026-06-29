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

# Tambahkan direktori root proyek ke path Python agar modul 'app' dapat ditemukan
sys.path.append(base_dir)

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import app
from app.database.connection import get_db, Base
from app.models.db_models import User, Student, AssessmentAspect, Assessment, ReportScore, PortfolioScore, Prediction
from app.services.ml_service import MLService

# --- SETUP DATABASE UJI COBA (SQLite File Fisik Sementara) ---
# Trik ini mengisolasi testing sehingga tidak mencemari database MySQL utama
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_temp.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Buat semua tabel di SQLite
Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Override dependency get_db di FastAPI dengan database SQLite lokal sementara
app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

def test_workflow():
    print("\n[TEST] 1. Pengujian Healthcheck Root API...")
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "Running"
    print("-> Sukses!")

    print("\n[TEST] 2. Registrasi Guru (User) Baru...")
    reg_data = {
        "full_name": "Pak Budi Guru SLB",
        "username": "budislb",
        "password": "secretpassword123"
    }
    response = client.post("/api/auth/register", json=reg_data)
    assert response.status_code == 201
    res = response.json()
    assert res["success"] is True
    assert res["data"]["username"] == "budislb"
    print("-> Sukses! Terbungkus ApiResponse.")

    print("\n[TEST] 3. Login Guru...")
    login_data = {
        "username": "budislb",
        "password": "secretpassword123"
    }
    response = client.post("/api/auth/login", json=login_data)
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True
    token = res["data"]["access_token"]
    assert token is not None
    headers = {"Authorization": f"Bearer {token}"}
    print("-> Sukses! Token JWT didapatkan.")

    print("\n[TEST] 4. Mendaftarkan Siswa Baru...")
    student_data = {
        "student_number": "NIS998877",
        "full_name": "Deni Siswa SLB",
        "gender": "M",
        "birth_date": "2013-05-12",
        "disability_category": "Tunagrahita Ringan C",
        "guardian_name": "Ibu Deni",
        "class_level": "4",
        "semester": "Odd"
    }
    response = client.post("/api/students", json=student_data, headers=headers)
    assert response.status_code == 201
    res = response.json()
    assert res["success"] is True
    student_id = res["data"]["id"]
    assert student_id is not None
    print(f"-> Sukses! Siswa terdaftar dengan ID: {student_id}")

    print("\n[TEST] 5. Menambahkan Referensi Aspek Penilaian...")
    # Aspek Kuantitatif
    asp_qnt = {
        "aspect_name": "Matematika",
        "aspect_type": "quantitative"
    }
    resp_qnt = client.post("/api/aspects", json=asp_qnt, headers=headers)
    assert resp_qnt.status_code == 201
    aspect_qnt_id = resp_qnt.json()["data"]["id"]

    # Aspek Kualitatif
    asp_ql = {
        "aspect_name": "Kemandirian Toilet Training",
        "aspect_type": "qualitative"
    }
    resp_ql = client.post("/api/aspects", json=asp_ql, headers=headers)
    assert resp_ql.status_code == 201
    aspect_ql_id = resp_ql.json()["data"]["id"]
    print(f"-> Sukses! Aspek Terdaftar. Kuantitatif ID: {aspect_qnt_id}, Kualitatif ID: {aspect_ql_id}")

    print("\n[TEST] 6. Menjalankan Transaksi Penilaian & Prediksi ML (Random Forest + SHAP)...")
    assessment_data = {
        "student_id": student_id,
        "academic_year": "2025/2026",
        "semester": "Odd",
        "assessment_date": "2026-06-27",
        "report_scores": [
            {
                "aspect_id": aspect_qnt_id,
                "numeric_score": 85.0
            }
        ],
        "portfolio_scores": [
            {
                "aspect_id": aspect_ql_id,
                "narrative_description": "Siswa mampu ke toilet secara mandiri dengan bimbingan verbal minimal dari guru."
            }
        ]
    }
    response = client.post("/api/assessments", json=assessment_data, headers=headers)
    assert response.status_code == 201
    res = response.json()
    assert res["success"] is True
    res_data = res["data"]
    
    # Verifikasi hasil prediksi ML yang diintegrasikan
    assert res_data["prediction"] is not None
    pred = res_data["prediction"]
    print(f"   -> Status Perkembangan: {pred['development_status']}")
    print(f"   -> Probabilitas Keyakinan Model: {pred['probability_score']}")
    print(f"   -> Rekomendasi PPI: {pred['iep_recommendation']}")
    
    # Ambil list penilaian siswa untuk memastikan tersimpan di database
    print("\n[TEST] 7. Mengambil Riwayat Penilaian Siswa dari Database...")
    history_resp = client.get(f"/api/assessments/student/{student_id}", headers=headers)
    assert history_resp.status_code == 200
    res = history_resp.json()
    assert res["success"] is True
    assert len(res["data"]) == 1
    print("-> Sukses!")

    # --- FITUR BARU: UPDATE & DELETE TESTING ---

    print("\n[TEST] 8. Mengubah Profil Siswa (Update Student)...")
    update_data = {
        "full_name": "Deni Siswa SLB Diperbarui",
        "class_level": "5"
    }
    up_resp = client.put(f"/api/students/{student_id}", json=update_data, headers=headers)
    assert up_resp.status_code == 200
    res = up_resp.json()
    assert res["success"] is True
    assert res["data"]["full_name"] == "Deni Siswa SLB Diperbarui"
    assert res["data"]["class_level"] == "5"
    print("-> Sukses!")

    print("\n[TEST] 9. Mengubah Kategori Aspek Penilaian (Update Aspect)...")
    update_aspect_data = {
        "aspect_name": "Matematika & Berhitung"
    }
    up_asp_resp = client.put(f"/api/aspects/{aspect_qnt_id}", json=update_aspect_data, headers=headers)
    assert up_asp_resp.status_code == 200
    res = up_asp_resp.json()
    assert res["success"] is True
    assert res["data"]["aspect_name"] == "Matematika & Berhitung"
    print("-> Sukses!")

    print("\n[TEST] 10. Pengujian Global Validation Error (Format 422 Kustom)...")
    bad_student_data = {
        "student_number": "NIS000000",
        "full_name": "Test Salah Input",
        "gender": "X",  # Gender salah (harus M atau F)
        "birth_date": "2015-01-01",
        "disability_category": "Test",
        "guardian_name": "Test",
        "class_level": "1",
        "semester": "Odd"
    }
    err_resp = client.post("/api/students", json=bad_student_data, headers=headers)
    assert err_resp.status_code == 422
    res = err_resp.json()
    assert res["success"] is False
    assert res["error_code"] == "VALIDATION_ERROR"
    assert len(res["details"]) > 0
    print(f"-> Sukses! Detail error: {res['details'][0]}")

    print("\n[TEST] 11. Menghapus Kategori Aspek (Delete Aspect - Cascade Delete)...")
    del_asp_resp = client.delete(f"/api/aspects/{aspect_ql_id}", headers=headers)
    assert del_asp_resp.status_code == 200
    assert del_asp_resp.json()["success"] is True
    
    # Ambil riwayat penilaian kembali, detail portfolio_scores untuk aspek tersebut harus terhapus
    chk_resp = client.get(f"/api/assessments/student/{student_id}", headers=headers)
    assert chk_resp.status_code == 200
    assert len(chk_resp.json()["data"][0]["portfolio_scores"]) == 0
    print("-> Sukses! Nilai portfolio dengan aspek tersebut otomatis terhapus secara cascade.")

    print("\n[TEST] 12. Menghapus Data Siswa (Delete Student - Cascade Delete)...")
    del_std_resp = client.delete(f"/api/students/{student_id}", headers=headers)
    assert del_std_resp.status_code == 200
    assert del_std_resp.json()["success"] is True

    # Cek riwayat penilaian siswa, harus mengembalikan 404 karena data siswa & penilaiannya terhapus secara cascade
    final_chk_resp = client.get(f"/api/assessments/student/{student_id}", headers=headers)
    assert final_chk_resp.status_code == 404
    res = final_chk_resp.json()
    assert res["success"] is False
    assert res["error_code"] == "HTTP_404"
    print("-> Sukses! Seluruh data transaksi penilaian siswa terhapus bersih secara cascade.")


if __name__ == "__main__":
    # Pastikan model ML ter-load
    MLService.load_models()
    try:
        test_workflow()
        print("\n===========================================")
        print("[SUCCESS] SEMUA TEST BERJALAN DENGAN SUKSES!")
        print("===========================================")
    except AssertionError as e:
        print(f"\n[FAILED] TEST GAGAL: Terjadi AssertionError {str(e)}")
    except Exception as e:
        print(f"\n[ERROR] TEST EROR: {str(e)}")
    finally:
        # Tutup semua koneksi ke database SQLite agar tidak terkunci di Windows (mencegah WinError 32)
        engine.dispose()
        if os.path.exists("./test_temp.db"):
            try:
                os.remove("./test_temp.db")
            except Exception as e:
                print(f"\n[WARNING] Gagal menghapus file database sementara: {str(e)}")
