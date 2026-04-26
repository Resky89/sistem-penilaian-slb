import pandas as pd
import joblib
import re
import os

# --- CONFIGURATION ---
DATA_PATH = "../DATA MENTAH.xlsx"
MODEL_PATH = "slb_model.joblib"
TFIDF_PATH = "tfidf_vectorizer.joblib"
ENCODERS_PATH = "label_encoders.joblib"
OUTPUT_PATH = "HASIL_PREDIKSI_DETAIL.xlsx"

def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def export_results():
    print("Loading model and components...")
    if not os.path.exists(MODEL_PATH):
        print(f"Error: {MODEL_PATH} not found. Please run train_model.py first.")
        return

    model = joblib.load(MODEL_PATH)
    tfidf = joblib.load(TFIDF_PATH)
    encoders = joblib.load(ENCODERS_PATH)
    le_aspek = encoders['le_aspek']
    le_label = encoders['le_label']

    print(f"Loading data from {DATA_PATH}...")
    xl = pd.ExcelFile(DATA_PATH)
    
    all_results = []

    for sheet in xl.sheet_names:
        print(f"Processing sheet: {sheet}")
        df = pd.read_excel(xl, sheet_name=sheet)
        
        # Standardize column names
        df.rename(columns={'Aspek': 'Aspek / Mapel', 'Nilai': 'X1 (Nilai)'}, inplace=True)
        
        required_cols = ['Aspek / Mapel', 'X1 (Nilai)', 'X2 (Deskripsi Capaian)', 'Y (Label)']
        if not all(col in df.columns for col in required_cols):
            print(f"Skipping sheet {sheet}: Required columns missing.")
            continue

        # Add student identification if not present
        if 'Siswa' not in df.columns:
            df['Siswa'] = sheet

        # Process each row
        rows_to_process = df.dropna(subset=['X2 (Deskripsi Capaian)']).copy()
        
        if rows_to_process.empty:
            continue

        # Prepare features
        rows_to_process['clean_X2'] = rows_to_process['X2 (Deskripsi Capaian)'].apply(clean_text)
        X_tfidf = tfidf.transform(rows_to_process['clean_X2']).toarray()
        
        # Combine with Nilai
        import numpy as np
        rows_to_process['X1 (Nilai)'] = pd.to_numeric(rows_to_process['X1 (Nilai)'], errors='coerce').fillna(0)
        X_nilai = rows_to_process[['X1 (Nilai)']].values
        X = np.hstack([X_nilai, X_tfidf])
        
        # Predict
        preds = model.predict(X)
        
        # Decode predictions
        rows_to_process['Prediksi Aspek'] = le_aspek.inverse_transform(preds[:, 0])
        rows_to_process['Prediksi Label'] = le_label.inverse_transform(preds[:, 1])
        
        # Check correctness
        rows_to_process['Status Aspek'] = rows_to_process.apply(
            lambda x: "BENAR" if str(x['Aspek / Mapel']).strip() == str(x['Prediksi Aspek']).strip() else "SALAH", axis=1
        )
        rows_to_process['Status Label'] = rows_to_process.apply(
            lambda x: "BENAR" if str(x['Y (Label)']).strip() == str(x['Prediksi Label']).strip() else "SALAH", axis=1
        )

        all_results.append(rows_to_process)

    if not all_results:
        print("No data processed.")
        return

    final_df = pd.concat(all_results, ignore_index=True)
    
    # Reorder columns for readability
    cols = ['Siswa', 'Aspek / Mapel', 'Prediksi Aspek', 'Status Aspek', 
            'X1 (Nilai)', 'X2 (Deskripsi Capaian)', 'Y (Label)', 'Prediksi Label', 'Status Label']
    
    # Only keep existing columns
    cols = [c for c in cols if c in final_df.columns]
    final_df = final_df[cols]

    print(f"Saving results to {OUTPUT_PATH}...")
    final_df.to_excel(OUTPUT_PATH, index=False)
    print("Export complete!")

if __name__ == "__main__":
    export_results()
