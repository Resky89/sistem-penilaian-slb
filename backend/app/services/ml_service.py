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

class MLService:
    _model = None
    _tfidf = None
    _encoders = None
    _explainer_label = None

    @classmethod
    def load_models(cls):
        """Memuat objek biner model ML ke memori."""
        if cls._model is None:
            # Menggunakan relative path ke folder models_ml
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            model_dir = os.path.join(base_dir, "models_ml")
            
            cls._model = joblib.load(os.path.join(model_dir, "slb_model.joblib"))
            cls._tfidf = joblib.load(os.path.join(model_dir, "tfidf_vectorizer.joblib"))
            cls._encoders = joblib.load(os.path.join(model_dir, "label_encoders.joblib"))
            
            # Inisialisasi SHAP Explainer untuk target 'Label' (estimator indeks 1 di MultiOutputClassifier)
            cls._explainer_label = shap.TreeExplainer(cls._model.estimators_[1])
            print("=== Model Machine Learning & SHAP Explainer Berhasil Dimuat ===")

    @classmethod
    def clean_text(cls, text: str) -> str:
        """Preprocessing teks deskripsi capaian sesuai dengan train_model.py"""
        if not isinstance(text, str):
            return ""
        text = text.lower()
        # Hilangkan tanda baca
        text = re.sub(r'[^a-zA-Z\s]', ' ', text)
        # Tokenisasi & Stopwords Removal
        words = text.split()
        words = [w for w in words if w not in STOPWORDS and len(w) > 2]
        return " ".join(words)

    @classmethod
    def generate_iep_recommendation(cls, label: str, aspect_name: str) -> str:
        """Menghasilkan rekomendasi PPI (IEP) secara otomatis berdasarkan label prediksi dan aspek."""
        recommendations = {
            "Sangat Baik": (
                f"Siswa telah menunjukkan kemampuan yang luar biasa dalam aspek {aspect_name}. "
                "Disarankan untuk memberikan pengayaan materi tingkat lanjut agar bakat dan potensi "
                "siswa dapat berkembang secara optimal."
            ),
            "Cukup": (
                f"Siswa sudah menunjukkan perkembangan yang cukup baik dalam aspek {aspect_name}, "
                "namun masih membutuhkan latihan berkala. Pendekatan pembelajaran terstruktur dan "
                "apresiasi kecil (reward) disarankan untuk menjaga motivasi belajarnya."
            ),
            "Kurang": (
                f"Siswa membutuhkan bimbingan intensif dan perhatian lebih dalam aspek {aspect_name}. "
                "Disarankan untuk menyederhanakan instruksi tugas, menggunakan media visual yang konkret, "
                "serta melakukan pendampingan secara langsung (one-on-one) agar siswa dapat memahami konsep dasar."
            )
        }
        return recommendations.get(label, f"Siswa memerlukan pendampingan berkelanjutan dalam aspek {aspect_name}.")

    @classmethod
    def predict(cls, numeric_score: float, narrative_text: str, aspect_name: str) -> Dict[str, Any]:
        """
        Melakukan prediksi klasifikasi perkembangan dan kontribusi fitur SHAP.
        """
        # Pastikan model sudah ter-load
        cls.load_models()

        # 1. Preprocessing Deskripsi
        cleaned_text = cls.clean_text(narrative_text)
        
        # 2. Transformasi TF-IDF
        X_tfidf = cls._tfidf.transform([cleaned_text]).toarray()
        
        # 3. Gabungkan dengan Nilai Angka
        X_nilai = np.array([[float(numeric_score)]])
        X_combined = np.hstack([X_nilai, X_tfidf])

        # 4. Jalankan Prediksi (MultiOutput)
        # Preds shape: (1, 2) -> [[aspek_idx, label_idx]]
        preds = cls._model.predict(X_combined)

        # 5. Decode Hasil Prediksi
        pred_label_idx = int(preds[0][1])
        decoded_label = cls._encoders['le_label'].inverse_transform([pred_label_idx])[0]

        # Estimasi probabilitas jika tersedia
        prob_score = None
        try:
            # Model target 'Label' adalah estimator indeks 1
            probs = cls._model.estimators_[1].predict_proba(X_combined)
            prob_score = float(probs[0][pred_label_idx])
        except Exception:
            pass

        # 6. Hitung SHAP Values untuk Menjelaskan Prediksi Label
        shap_explanation = {}
        try:
            shap_vals = cls._explainer_label.shap_values(X_combined)
            feature_names = ["Nilai Kuantitatif"] + list(cls._tfidf.get_feature_names_out())
            
            # Handle modern SHAP return formats defensively
            if isinstance(shap_vals, np.ndarray) and len(shap_vals.shape) == 3:
                class_shap_vals = shap_vals[0, :, pred_label_idx]
            elif isinstance(shap_vals, list):
                class_shap_vals = shap_vals[pred_label_idx][0]
            else:
                class_shap_vals = shap_vals[0]
            
            feat_contribs = []
            for name, val in zip(feature_names, class_shap_vals):
                if abs(val) > 0.0001:
                    feat_contribs.append({"feature": name, "shap_value": float(val)})
            
            feat_contribs = sorted(feat_contribs, key=lambda x: abs(x["shap_value"]), reverse=True)
            shap_explanation = {
                "base_value": float(cls._explainer_label.expected_value[pred_label_idx]),
                "predictions_contributions": feat_contribs[:8]
            }
        except Exception as e:
            shap_explanation = {"error": f"Gagal menghitung SHAP: {str(e)}"}

        # 7. Generate Rekomendasi PPI
        iep_rec = cls.generate_iep_recommendation(decoded_label, aspect_name)

        return {
            "development_status": decoded_label,
            "probability_score": prob_score,
            "iep_recommendation": iep_rec,
            "shap_explanation": shap_explanation
        }
