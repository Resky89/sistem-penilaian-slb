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
from app.models.db_models import User, Student, Assessment, Prediction
from app.services.ml_service import MLService

# --- SETUP DATABASE UJI COBA (SQLite File Fisik Sementara) ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_temp.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

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
    login_data = {"username": "budislb", "password": "secretpassword123"}
    response = client.post("/api/auth/login", json=login_data)
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True
    token = res["data"]["access_token"]
    refresh_token = res["data"]["refresh_token"]
    assert token is not None
    assert refresh_token is not None
    print("-> Sukses! Access Token & Refresh Token didapatkan.")

    print("\n[TEST] 3.1. Uji Refresh Token...")
    refresh_resp = client.post("/api/auth/refresh", json={"refresh_token": refresh_token})
    assert refresh_resp.status_code == 200
    ref_res = refresh_resp.json()
    assert ref_res["success"] is True
    new_token = ref_res["data"]["access_token"]
    new_refresh = ref_res["data"]["refresh_token"]
    assert new_token is not None
    assert new_refresh is not None
    headers = {"Authorization": f"Bearer {new_token}"}
    print("-> Sukses! Token baru diterbitkan via Refresh Token.")

    print("\n[TEST] 4. Mendaftarkan Siswa Baru...")
    student_data = {
        "student_number": "NIS998877",
        "full_name": "Deni Siswa SLB",
        "class_level": "4",
        "semester": "Odd",
        "disability_category": "Tunagrahita Ringan C",
        "school_name": "SLB Negeri Pembina",
        "academic_year": "2025/2026"
    }
    response = client.post("/api/students", json=student_data, headers=headers)
    assert response.status_code == 201
    res = response.json()
    assert res["success"] is True
    student_id = res["data"]["id"]
    assert student_id is not None
    print(f"-> Sukses! Siswa terdaftar dengan ID: {student_id}")

    print("\n[TEST] 5. Membuat Transaksi Penilaian dengan Kolom Mapel & Aspek Portofolio...")
    assessment_data = {
        "student_id": student_id,
        "academic_year": "2025/2026",
        "semester": "Odd",
        "assessment_date": "2026-06-29",
        # Mata Pelajaran (Nilai + Deskripsi)
        "pai_score": 80.0,
        "pai_desc": "Siswa mampu berdoa sebelum dan sesudah belajar dengan bimbingan.",
        "pkn_score": 75.0,
        "pkn_desc": "Siswa mengenal simbol-simbol Pancasila dengan bantuan gambar.",
        "ind_score": 70.0,
        "ind_desc": "Siswa mulai bisa membaca kalimat pendek dengan bantuan guru.",
        "mat_score": 85.0,
        "mat_desc": "Siswa dapat berhitung 1 sampai 20 secara mandiri.",
        "ipas_score": 72.0,
        "ipas_desc": "Siswa mengenal benda-benda di sekitar lingkungan sekolah.",
        "ing_score": 65.0,
        "ing_desc": "Siswa mengenal kosakata bahasa Inggris sederhana seperti warna dan angka.",
        "art_score": 90.0,
        "art_desc": "Siswa menunjukkan antusiasme tinggi dalam kegiatan menggambar dan mewarnai.",
        "pjok_score": 88.0,
        "pjok_desc": "Siswa aktif mengikuti kegiatan senam dan olahraga ringan.",
        "sun_score": 68.0,
        "sun_desc": "Siswa mengenal beberapa kosakata bahasa Sunda dasar.",
        "pro_score": 78.0,
        "pro_desc": "Siswa mengikuti program pengembangan kemampuan ADL (Activity of Daily Living).",
        # Aspek Portofolio (Deskripsi saja)
        "pramuka_desc": "Siswa aktif mengikuti kegiatan pramuka dengan semangat.",
        "konsentrasi_desc": "Siswa mampu berkonsentrasi selama 15 menit dengan kondisi tenang.",
        "motorik_desc": "Kemampuan motorik halus berkembang baik, terlihat dari kemampuan memegang pensil.",
        "interaksi_desc": "Siswa mulai berani menyapa teman dan guru tanpa perlu didorong.",
        "emosi_desc": "Siswa dapat mengontrol emosi dengan lebih baik dibanding semester sebelumnya.",
        "bina_diri_desc": "Siswa mampu ke toilet secara mandiri dengan bimbingan verbal minimal.",
        "membaca_desc": "Siswa dapat membaca kata-kata sederhana yang terdiri dari 3-4 huruf.",
        "menulis_desc": "Siswa mampu menyalin tulisan dari papan tulis dengan rapi.",
        "berhitung_desc": "Siswa dapat menjumlahkan dua bilangan di bawah 10 secara mandiri."
    }
    response = client.post("/api/assessments", json=assessment_data, headers=headers)
    assert response.status_code == 201
    res = response.json()
    assert res["success"] is True
    res_data = res["data"]

    # Verifikasi kolom mapel tersimpan
    assert res_data["mat_score"] == 85.0
    assert res_data["art_score"] == 90.0
    assert res_data["bina_diri_desc"] is not None

    # Verifikasi hasil prediksi ML
    assert res_data["prediction"] is not None
    pred = res_data["prediction"]
    print(f"   -> Status Perkembangan Utama (Mayoritas): {pred['development_status']}")
    print(f"   -> Rata-rata Probabilitas Keyakinan Model: {pred['probability_score']}")
    assert pred['iep_recommendation'] == ""
    
    # Verifikasi prediksi per-mapel/aspek tersimpan di shap_explanation.predictions
    assert "predictions" in pred["shap_explanation"]
    preds_list = pred["shap_explanation"]["predictions"]
    assert len(preds_list) > 0
    print(f"   -> Ditemukan {len(preds_list)} hasil prediksi individu.")
    
    # Cek salah satu contoh prediksi (misal Matematika)
    math_pred = next((p for p in preds_list if p["subject"] == "Matematika"), None)
    assert math_pred is not None
    assert math_pred["status"] in ["Baik", "Cukup", "Perlu Bimbingan"]
    assert "shap" in math_pred
    assert "features" in math_pred["shap"]
    assert "values" in math_pred["shap"]
    print(f"   -> Contoh Prediksi Matematika: {math_pred['status']} (Prob: {math_pred['probability']:.4f})")
    print("-> Sukses! Semua kolom mapel dan portofolio beserta penjelasan SHAP tersimpan.")

    print("\n[TEST] 6. Mengambil Riwayat Penilaian Siswa dari Database...")
    history_resp = client.get(f"/api/assessments/student/{student_id}", headers=headers)
    assert history_resp.status_code == 200
    res = history_resp.json()
    assert res["success"] is True
    assert len(res["data"]) == 1
    assert res["data"][0]["mat_score"] == 85.0
    print("-> Sukses! Data mapel terkonfirmasi dari database.")

    print("\n[TEST] 7. Mengubah Profil Siswa (Update Student)...")
    update_data = {"full_name": "Deni Siswa SLB Diperbarui", "class_level": "5"}
    up_resp = client.put(f"/api/students/{student_id}", json=update_data, headers=headers)
    assert up_resp.status_code == 200
    res = up_resp.json()
    assert res["success"] is True
    assert res["data"]["full_name"] == "Deni Siswa SLB Diperbarui"
    print("-> Sukses!")

    print("\n[TEST] 8. Pengujian Global Validation Error (Format 422 Kustom)...")
    bad_student_data = {
        "student_number": "NIS000000",
        "full_name": "Test Salah Input",
        "class_level": "1",
        "semester": "InvalidSemester",
        "disability_category": "Test",
        "school_name": "Test",
        "academic_year": "2025/2026"
    }
    err_resp = client.post("/api/students", json=bad_student_data, headers=headers)
    assert err_resp.status_code == 422
    res = err_resp.json()
    assert res["success"] is False
    assert res["error_code"] == "VALIDATION_ERROR"
    assert len(res["details"]) > 0
    print(f"-> Sukses! Detail error: {res['details'][0]}")

    print("\n[TEST] 9. Menghapus Data Siswa (Delete Student - Cascade Delete)...")
    del_std_resp = client.delete(f"/api/students/{student_id}", headers=headers)
    assert del_std_resp.status_code == 200
    assert del_std_resp.json()["success"] is True

    final_chk_resp = client.get(f"/api/assessments/student/{student_id}", headers=headers)
    assert final_chk_resp.status_code == 404
    res = final_chk_resp.json()
    assert res["success"] is False
    assert res["error_code"] == "HTTP_404"
    print("-> Sukses! Seluruh data transaksi penilaian siswa terhapus bersih secara cascade.")


if __name__ == "__main__":
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
        engine.dispose()
        if os.path.exists("./test_temp.db"):
            try:
                os.remove("./test_temp.db")
            except Exception as e:
                print(f"\n[WARNING] Gagal menghapus file database sementara: {str(e)}")
