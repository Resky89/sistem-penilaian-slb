import os
import re
import joblib
import numpy as np
import pandas as pd
import shap
from typing import Dict, Any, List

# Indonesian Stopwords (Standard + Domain-Specific + Student Names)
STOPWORDS = [
    'dan', 'di', 'ke', 'dari', 'ini', 'itu', 'juga', 'untuk', 'pada', 'dengan',
    'adalah', 'yang', 'saya', 'kami', 'anda', 'mereka', 'ia', 'dia', 'kita', 
    'dapat', 'harus', 'akan', 'sudah', 'telah', 'sedang', 'ingin',
    'ada', 'bukan', 'hanya', 'saja', 'atau', 'namun', 'tetapi',
    'oleh', 'seperti', 'maka', 'jika', 'karena', 'sehingga', 'bahwa',
    'hal', 'secara', 'tersebut', 'dalam', 'atas', 'bawah', 'serta', 'bagi', 'setelah',
    'peserta', 'didik', 'siswa', 'aspek', 'kegiatan', 'aktivitas', 'cara', 
    'berikan', 'gunakan', 'saran', 'hari',
    'dafa', 'dzikri', 'eria', 'arif', 'arifin', 'rama', 'fadil', 'afif', 
    'azzam', 'dewi', 'faiz', 'ahmad', 'bilqis', 'rizky', 'mia', 'andreansyah', 
    'rahman', 'khansa', 'robi', 'roby'
]

MAPEL_CONFIG = [
    ("pai_score", "pai_desc", "Pendidikan Agama Islam dan Budi Pekerti"),
    ("pkn_score", "pkn_desc", "Pendidikan Pancasila dan Kewarganegaraan"),
    ("ind_score", "ind_desc", "Bahasa Indonesia"),
    ("mat_score", "mat_desc", "Matematika"),
    ("ipas_score", "ipas_desc", "Ilmu Pengetahuan Alam dan Sosial"),
    ("ing_score", "ing_desc", "Bahasa Inggris"),
    ("art_score", "art_desc", "Seni Budaya"),
    ("pjok_score", "pjok_desc", "Pendidikan Jasmani, Olahraga, dan Kesehatan"),
    ("sun_score", "sun_desc", "Bahasa Sunda"),
    ("pro_score", "pro_desc", "Program Khusus"),
    (None, "pramuka_desc", "Ekskul Pramuka"),
    (None, "konsentrasi_desc", "Konsentrasi"),
    (None, "motorik_desc", "Motorik"),
    (None, "interaksi_desc", "Interaksi dan Komunikasi"),
    (None, "emosi_desc", "Emosi"),
    (None, "bina_diri_desc", "Bina Diri"),
    (None, "membaca_desc", "Membaca"),
    (None, "menulis_desc", "Menulis"),
    (None, "berhitung_desc", "Berhitung"),
]

class MLService:
    _model = None
    _tfidf = None
    _encoders = None
    _ohe = None
    _explainer_label = None

    @classmethod
    def load_models(cls):
        """Memuat objek biner model ML ke memori."""
        if cls._model is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            model_dir = os.path.join(base_dir, "models_ml")
            
            cls._model = joblib.load(os.path.join(model_dir, "slb_model.joblib"))
            cls._tfidf = joblib.load(os.path.join(model_dir, "tfidf_vectorizer.joblib"))
            cls._encoders = joblib.load(os.path.join(model_dir, "label_encoders.joblib"))
            cls._ohe = joblib.load(os.path.join(model_dir, "onehot_encoder.joblib"))
            
            # Inisialisasi SHAP Explainer untuk target tunggal (Status Perkembangan)
            cls._explainer_label = shap.TreeExplainer(cls._model)
            print("=== Model Machine Learning & SHAP Explainer Berhasil Dimuat ===")

    @classmethod
    def clean_text(cls, text: str) -> str:
        """Preprocessing teks deskripsi capaian sesuai dengan train_model.py"""
        if not isinstance(text, str):
            return ""
        # Hapus prefix "Deskripsi Perkembangan:" secara case-insensitive
        text = re.sub(r'(?i)deskripsi perkembangan\s*:\s*', '', text)
        text = text.lower()
        text = re.sub(r'[^a-zA-Z\s]', ' ', text)
        words = text.split()
        words = [w for w in words if w not in STOPWORDS and len(w) > 2]
        return " ".join(words)

    @classmethod
    def predict_subject(cls, score: float, text: str, subject_name: str) -> Dict[str, Any]:
        """
        Melakukan prediksi status perkembangan (Label) dan penjelasan SHAP
        untuk satu mapel/aspek tertentu.
        """
        cls.load_models()
        cleaned_text = cls.clean_text(text)
        X_tfidf = cls._tfidf.transform([cleaned_text]).toarray()
        
        # OHE aspect
        X_aspek = cls._ohe.transform(pd.DataFrame([[subject_name]], columns=['Aspek / Mapel']))
        
        X_nilai = np.array([[float(score)]])
        X_combined = np.hstack([X_nilai, X_tfidf, X_aspek])

        # Predict (Single-Output Classifier)
        preds = cls._model.predict(X_combined)
        pred_label_idx = int(preds[0])
        decoded_label = cls._encoders['le_label'].inverse_transform([pred_label_idx])[0]

        # Post-processing heuristics to handle class imbalance biases & unseen high scores
        lower_desc = text.lower() if isinstance(text, str) else ""
        has_positive_keywords = "sangat baik" in lower_desc or ("sangat" in lower_desc and "baik" in lower_desc)
        has_negative_keywords = any(w in lower_desc for w in ["kurang", "belum", "perlu bimbingan", "kesulitan", "lambat", "hambatan"])
        
        is_excellent_academic = score >= 85.0
        portfolio_subjects = ["Ekskul Pramuka", "Konsentrasi", "Motorik", "Interaksi dan Komunikasi", "Emosi", "Bina Diri", "Membaca", "Menulis", "Berhitung"]
        is_portfolio = subject_name in portfolio_subjects
        
        if (is_excellent_academic or is_portfolio) and has_positive_keywords and not has_negative_keywords:
            decoded_label = "Baik"
            try:
                classes_list = list(cls._encoders['le_label'].classes_)
                if "Baik" in classes_list:
                    pred_label_idx = classes_list.index("Baik")
            except Exception:
                pass

        # Probability score
        prob_score = 0.0
        try:
            probs = cls._model.predict_proba(X_combined)
            prob_score = float(probs[0][pred_label_idx])
        except Exception:
            pass

        # SHAP Explanation
        shap_features = []
        shap_values = []
        try:
            shap_vals = cls._explainer_label.shap_values(X_combined)
            aspek_cols = [f'aspek_{a}' for a in cls._ohe.categories_[0]]
            feature_names = ["Nilai"] + list(cls._tfidf.get_feature_names_out()) + aspek_cols

            if isinstance(shap_vals, list):
                class_shap_vals = shap_vals[pred_label_idx][0]
            elif isinstance(shap_vals, np.ndarray):
                if len(shap_vals.shape) == 3:
                    class_shap_vals = shap_vals[0, :, pred_label_idx]
                elif len(shap_vals.shape) == 2:
                    class_shap_vals = shap_vals[0]
            else:
                class_shap_vals = shap_vals[0]

            # Filter out zero/tiny values and sort by absolute contribution
            contribs = []
            for name, val in zip(feature_names, class_shap_vals):
                if abs(val) > 0.0001:
                    contribs.append((name, float(val)))
            
            contribs = sorted(contribs, key=lambda x: abs(x[1]), reverse=True)[:8]
            for name, val in contribs:
                shap_features.append(name)
                shap_values.append(val)
        except Exception as e:
            print(f"Gagal menghitung SHAP: {e}")

        return {
            "status": decoded_label,
            "probability": prob_score,
            "shap": {
                "features": shap_features,
                "values": shap_values
            }
        }

    @classmethod
    def predict(cls, assessment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Melakukan prediksi untuk seluruh mapel/aspek yang diinput secara individu.
        """
        cls.load_models()
        
        predictions_list = []
        status_counts = {}

        for score_field, desc_field, display_name in MAPEL_CONFIG:
            # Dapatkan score dan description
            score = 0.0
            if score_field:
                score_val = assessment_data.get(score_field)
                if score_val is not None:
                    score = float(score_val)
            
            desc = assessment_data.get(desc_field)
            
            # Kita lakukan prediksi jika ada data deskripsi atau nilai yang diisi
            # (Untuk mapel, jika nilai atau deskripsi diisi. Untuk aspek, jika deskripsi diisi)
            has_data = False
            if score_field:
                if assessment_data.get(score_field) is not None or (desc and desc.strip()):
                    has_data = True
            else:
                if desc and desc.strip():
                    has_data = True

            if has_data:
                # Run prediction
                res = cls.predict_subject(score, desc if desc else "", display_name)
                
                predictions_list.append({
                    "subject": display_name,
                    "status": res["status"],
                    "score": score if score_field and assessment_data.get(score_field) is not None else None,
                    "desc": desc if desc else "-",
                    "probability": res["probability"],
                    "shap": res["shap"]
                })

                # Count labels for summary
                status_counts[res["status"]] = status_counts.get(res["status"], 0) + 1

        if not predictions_list:
            # Fallback jika tidak ada data sama sekali
            return {
                "development_status": "Belum Dinilai",
                "probability_score": 0.0,
                "iep_recommendation": "",
                "shap_explanation": {"predictions": []}
            }

        # Menentukan status perkembangan utama berdasarkan mayoritas
        majority_status = max(status_counts, key=status_counts.get)
        avg_prob = sum(p["probability"] for p in predictions_list) / len(predictions_list)

        return {
            "development_status": majority_status,
            "probability_score": avg_prob,
            "iep_recommendation": "", # Rekomendasi PPI dihilangkan sesuai permintaan user
            "shap_explanation": {
                "predictions": predictions_list
            }
        }
