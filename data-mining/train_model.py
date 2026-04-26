import pandas as pd
import numpy as np
import joblib
import re
import os
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.multioutput import MultiOutputClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score
import shap
import matplotlib.pyplot as plt

# --- CONFIGURATION ---
DATA_PATH = "../DATA MENTAH.xlsx"
MODEL_PATH = "slb_model.joblib"
TFIDF_PATH = "tfidf_vectorizer.joblib"
ENCODERS_PATH = "label_encoders.joblib"

# Indonesian Stopwords (Standard list)
STOPWORDS = [
    'dan', 'di', 'ke', 'dari', 'ini', 'itu', 'juga', 'untuk', 'pada', 'dengan', 
    'adalah', 'yang', 'saya', 'kami', 'anda', 'mereka', 'ia', 'dia', 'kita',
    'bisa', 'dapat', 'harus', 'akan', 'sudah', 'telah', 'sedang', 'ingin',
    'ada', 'tidak', 'bukan', 'hanya', 'saja', 'atau', 'namun', 'tetapi',
    'oleh', 'seperti', 'maka', 'jika', 'karena', 'sehingga', 'bahwa',
    'hal', 'secara', 'tersebut', 'dalam', 'atas', 'bawah', 'serta', 'bagi'
]

def clean_text(text):
    """Basic text cleaning for Indonesian achievement descriptions."""
    if not isinstance(text, str):
        return ""
    text = text.lower()
    # Remove punctuation
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    # Tokenize and remove stopwords
    words = text.split()
    words = [w for w in words if w not in STOPWORDS and len(w) > 2]
    return " ".join(words)

def load_and_consolidate_data(file_path):
    """Loads all sheets and consolidates them into a single DataFrame."""
    print(f"Loading data from {file_path}...")
    xl = pd.ExcelFile(file_path)
    dfs = []
    
    for sheet in xl.sheet_names:
        df = pd.read_excel(xl, sheet_name=sheet)
        # Handle column naming inconsistencies
        df.rename(columns={'Aspek': 'Aspek / Mapel', 'Nilai': 'X1 (Nilai)'}, inplace=True)
        
        # Ensure required columns exist
        required_cols = ['Sumber Data', 'Aspek / Mapel', 'X1 (Nilai)', 'X2 (Deskripsi Capaian)', 'Y (Label)']
        
        # If Sumber Data is missing, use sheet name
        if 'Sumber Data' not in df.columns and 'Siswa' in df.columns:
            df.rename(columns={'Siswa': 'Sumber Data'}, inplace=True)
        elif 'Sumber Data' not in df.columns:
            df['Sumber Data'] = sheet

        if all(col in df.columns for col in required_cols):
            dfs.append(df[required_cols])
            
    if not dfs:
        raise ValueError("No valid data found in the Excel file.")
        
    all_df = pd.concat(dfs, ignore_index=True)
    
    # Preprocess Nilai: Convert to numeric, handle missing
    all_df['X1 (Nilai)'] = pd.to_numeric(all_df['X1 (Nilai)'], errors='coerce')
    # Fill NaN Nilai with mean or 0 (using mean as per PDF pseudocode)
    all_df['X1 (Nilai)'] = all_df['X1 (Nilai)'].fillna(all_df['X1 (Nilai)'].mean() if not all_df['X1 (Nilai)'].isna().all() else 0)
    
    all_df.dropna(subset=['X2 (Deskripsi Capaian)', 'Aspek / Mapel', 'Y (Label)'], inplace=True)
    return all_df

def train_system():
    # 1. Load Data
    df = load_and_consolidate_data(DATA_PATH)
    print(f"Total rows after consolidation: {len(df)}")

    # 2. Preprocessing
    print("Pre-processing text...")
    df['clean_X2'] = df['X2 (Deskripsi Capaian)'].apply(clean_text)
    
    # 3. Encoding Targets
    print("Encoding target labels...")
    le_aspek = LabelEncoder()
    le_label = LabelEncoder()
    
    y = np.vstack([
        le_aspek.fit_transform(df['Aspek / Mapel']),
        le_label.fit_transform(df['Y (Label)'])
    ]).T
    
    encoders = {'le_aspek': le_aspek, 'le_label': le_label}

    # 4. Feature Extraction (TF-IDF)
    print("Extracting TF-IDF features...")
    tfidf = TfidfVectorizer(max_features=500, ngram_range=(1, 1)) 
    X_tfidf = tfidf.fit_transform(df['clean_X2']).toarray()
    
    # Combine TF-IDF with X1 (Nilai)
    X_nilai = df[['X1 (Nilai)']].values
    X = np.hstack([X_nilai, X_tfidf])
    
    # Export Full Transformed Data
    feature_names = ['X1_Nilai_Feature'] + list(tfidf.get_feature_names_out())
    transformed_df = pd.DataFrame(X, columns=feature_names)
    
    # Add all original columns back for complete transformation data
    original_cols = ['Sumber Data', 'Aspek / Mapel', 'X1 (Nilai)', 'X2 (Deskripsi Capaian)', 'Y (Label)']
    metadata_df = df[original_cols].reset_index(drop=True)
    full_transformed_df = pd.concat([metadata_df, transformed_df], axis=1)
    
    full_transformed_df.to_excel("TRANSFORMED_DATA.xlsx", index=False)
    print("Full transformed data saved to 'TRANSFORMED_DATA.xlsx'.")

    # 5. Train/Test Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 6. Model Build & Tuning
    print("Initializing Random Forest & MultiOutputClassifier...")
    rf = RandomForestClassifier(random_state=42)
    mo_clf = MultiOutputClassifier(rf)
    
    param_grid = {
        'estimator__n_estimators': [50, 100],
        'estimator__max_depth': [None, 10, 20],
        'estimator__min_samples_split': [2, 5]
    }
    
    print("Starting Hyperparameter Tuning (GridSearch)...")
    grid_search = GridSearchCV(mo_clf, param_grid, cv=3, n_jobs=-1, verbose=1)
    grid_search.fit(X_train, y_train)
    
    best_model = grid_search.best_estimator_
    print(f"Best Params: {grid_search.best_params_}")

    # 7. Evaluation
    print("\nEvaluation Results:")
    y_pred = best_model.predict(X_test)
    
    from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

    outputs = [('Aspek / Mapel', le_aspek), ('Y (Label)', le_label)]
    
    for i, (name, encoder) in enumerate(outputs):
        print(f"\n--- Output {i+1}: {name} ---")
        unique_test = sorted(list(set(y_test[:, i]) | set(y_pred[:, i])))
        target_names = [encoder.classes_[idx] for idx in unique_test]
        
        print(classification_report(y_test[:, i], y_pred[:, i], 
                                    labels=unique_test,
                                    target_names=target_names))
        
        # Confusion Matrix
        cm = confusion_matrix(y_test[:, i], y_pred[:, i], labels=unique_test)
        plt.figure(figsize=(12, 8))
        disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=target_names)
        disp.plot(cmap=plt.cm.Blues, xticks_rotation='vertical')
        plt.title(f"Confusion Matrix: {name}")
        plt.tight_layout()
        plt.savefig(f"confusion_matrix_{name.replace(' ', '_').replace('/', '')}.png")
        plt.close()
        print(f"Confusion Matrix saved: confusion_matrix_{name.replace(' ', '_').replace('/', '')}.png")

    # 8. Explainable AI (SHAP)
    print("\nGenerating SHAP explanations...")
    # Note: For MultiOutput, we explain each estimator separately
    X_sample = X_test[:50]
    feature_names_all = feature_names # Already includes Nilai

    for i, (name, encoder) in enumerate(outputs):
        print(f"Calculating SHAP for {name}...")
        explainer = shap.TreeExplainer(best_model.estimators_[i])
        shap_values = explainer.shap_values(X_sample)
        
        plt.figure(figsize=(10, 6))
        # Handle multi-class SHAP return (list of arrays)
        shap.summary_plot(shap_values, X_sample, feature_names=feature_names_all, show=False)
        plt.title(f"SHAP Summary: {name}")
        plt.savefig(f"shap_summary_{name.replace(' ', '_').replace('/', '')}.png")
        plt.close()
    
    print("SHAP plots saved.")

    # 9. Save System
    joblib.dump(best_model, MODEL_PATH)
    joblib.dump(tfidf, TFIDF_PATH)
    joblib.dump(encoders, ENCODERS_PATH)
    print(f"System saved: {MODEL_PATH}, {TFIDF_PATH}, {ENCODERS_PATH}")

if __name__ == "__main__":
    train_system()
