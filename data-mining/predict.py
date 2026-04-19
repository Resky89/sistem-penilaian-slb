import joblib
import re
import pandas as pd

def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def predict_assessment(text):
    """Predicts Aspect and Label from achievement description."""
    try:
        # Load components
        model = joblib.load("slb_model.joblib")
        tfidf = joblib.load("tfidf_vectorizer.joblib")
        encoders = joblib.load("label_encoders.joblib")
        
        # Preprocess
        cleaned = clean_text(text)
        X_tfidf = tfidf.transform([cleaned])
        
        # Predict
        preds = model.predict(X_tfidf)
        
        # Decode
        aspek = encoders['le_aspek'].inverse_transform([preds[0][0]])[0]
        label = encoders['le_label'].inverse_transform([preds[0][1]])[0]
        
        return {
            'Aspek / Mapel': aspek,
            'Label': label
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    print("-" * 30)
    print("SLB Prediction System")
    print("-" * 30)
    sample_text = input("Masukkan Deskripsi Capaian: ")
    if not sample_text:
        sample_text = "Siswa mampu membaca huruf hijaiyah dengan lancar dan memahami kandungan surah pendek."
    
    result = predict_assessment(sample_text)
    print("\nHasil Prediksi:")
    print(f"- Aspek / Mapel: {result.get('Aspek / Mapel')}")
    print(f"- Label Prediksi: {result.get('Label')}")
