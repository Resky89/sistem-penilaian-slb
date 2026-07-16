import joblib
import re
import pandas as pd
import numpy as np

def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def predict_assessment(text, nilai, aspek):
    """Predicts Status Perkembangan from achievement description, score, and aspect/subject."""
    try:
        # Load components
        model = joblib.load("slb_model.joblib")
        tfidf = joblib.load("tfidf_vectorizer.joblib")
        encoders = joblib.load("label_encoders.joblib")
        ohe = joblib.load("onehot_encoder.joblib")
        
        # Preprocess
        cleaned = clean_text(text)
        X_tfidf = tfidf.transform([cleaned]).toarray()
        
        # OHE aspect
        X_aspek = ohe.transform(pd.DataFrame([[aspek]], columns=['Aspek / Mapel']))
        
        # Combine with Nilai
        X_nilai = np.array([[float(nilai)]])
        X = np.hstack([X_nilai, X_tfidf, X_aspek])
        
        # Predict
        preds = model.predict(X)
        
        # Decode
        label = encoders['le_label'].inverse_transform([preds[0]])[0]
        
        return {
            'Status Perkembangan': label
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    print("-" * 30)
    print("SLB Prediction System (Single-Output)")
    print("-" * 30)
    sample_aspek = input("Masukkan Aspek / Mapel (misal: Matematika): ")
    sample_text = input("Masukkan Deskripsi Capaian: ")
    sample_nilai = input("Masukkan Nilai (0-100): ")
    
    if not sample_aspek:
        sample_aspek = "PAI & Budi Pekerti"
    if not sample_text:
        sample_text = "Siswa mampu membaca huruf hijaiyah dengan lancar dan memahami kandungan surah pendek."
    if not sample_nilai:
        sample_nilai = 85
    
    result = predict_assessment(sample_text, sample_nilai, sample_aspek)
    print("\nHasil Prediksi:")
    print(f"- Aspek / Mapel Input: {sample_aspek}")
    print(f"- Status Perkembangan Prediksi: {result.get('Status Perkembangan')}")

