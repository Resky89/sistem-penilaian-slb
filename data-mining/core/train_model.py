import pandas as pd
import numpy as np
import joblib
import re
import os
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.multioutput import MultiOutputClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix, ConfusionMatrixDisplay
import shap
import matplotlib.pyplot as plt
from imblearn.over_sampling import SMOTE
from sklearn.neighbors import NearestNeighbors

# --- CONFIGURATION ---
DATA_PATH = r"d:\projects\Sistem-Penilaian-SLB\DATA MENTAH.xlsx"
SPLIT_PATH = r"d:\projects\Sistem-Penilaian-SLB\DATA_SPLIT_TRAIN_TEST.xlsx"
MODEL_PATH = r"d:\projects\Sistem-Penilaian-SLB\data-mining\core\slb_model.joblib"
TFIDF_PATH = r"d:\projects\Sistem-Penilaian-SLB\data-mining\core\tfidf_vectorizer.joblib"
ENCODERS_PATH = r"d:\projects\Sistem-Penilaian-SLB\data-mining\core\label_encoders.joblib"

# Indonesian Stopwords (Standard list + Domain Specific + Student Names)
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

def clean_text(text):
    """Basic text cleaning for Indonesian achievement descriptions."""
    if not isinstance(text, str):
        return ""
    text = re.sub(r'(?i)deskripsi perkembangan\s*:\s*', '', text)
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    words = text.split()
    words = [w for w in words if w not in STOPWORDS and len(w) > 2]
    return " ".join(words)

def recover_missing_values(df_split, raw_path):
    if not os.path.exists(raw_path):
        return df_split
    xl_raw = pd.ExcelFile(raw_path)
    raw_sheets = {}
    for sheet in xl_raw.sheet_names:
        df_raw = pd.read_excel(xl_raw, sheet_name=sheet)
        df_raw = df_raw.copy()
        if 'Sumber Data' not in df_raw.columns:
            df_raw['Sumber Data'] = sheet.replace('Data Mentah ', '')
        raw_sheets[sheet.replace('Data Mentah ', '')] = df_raw

    df_split = df_split.copy()
    for idx, row in df_split.iterrows():
        student = row.get('Nama Siswa', '')
        if not isinstance(student, str) or not student:
            student = row.get('Sumber Data', '')
        if student in raw_sheets:
            raw_df = raw_sheets[student]
            match_mask = (raw_df['Label'].astype(str).str.strip() == str(row['Label']).strip())
            
            raw_val_str = raw_df['Nilai'].astype(str).str.strip().str.replace('.0', '', regex=False)
            split_val_str = str(row['Nilai']).strip().replace('.0', '')
            match_mask = match_mask & (raw_val_str == split_val_str)
            
            matches = raw_df[match_mask]
            if len(matches) == 1:
                recovered_row = matches.iloc[0]
                if pd.isnull(row['Aspek / Mapel']) or str(row['Aspek / Mapel']) == 'nan':
                    df_split.at[idx, 'Aspek / Mapel'] = recovered_row['Aspek / Mapel']
                if pd.isnull(row['Deskripsi Penilaian']) or str(row['Deskripsi Penilaian']) == 'nan':
                    df_split.at[idx, 'Deskripsi Penilaian'] = recovered_row['Deskripsi Penilaian']
            elif len(matches) > 1:
                if not pd.isnull(row['Deskripsi Penilaian']) and str(row['Deskripsi Penilaian']) != 'nan':
                    narrowed = matches[matches['Deskripsi Penilaian'].astype(str).str.strip() == str(row['Deskripsi Penilaian']).strip()]
                    if len(narrowed) == 1:
                        recovered_row = narrowed.iloc[0]
                        if pd.isnull(row['Aspek / Mapel']) or str(row['Aspek / Mapel']) == 'nan':
                            df_split.at[idx, 'Aspek / Mapel'] = recovered_row['Aspek / Mapel']
                elif not pd.isnull(row['Aspek / Mapel']) and str(row['Aspek / Mapel']) != 'nan':
                    narrowed = matches[matches['Aspek / Mapel'].astype(str).str.strip() == str(row['Aspek / Mapel']).strip()]
                    if len(narrowed) == 1:
                        recovered_row = narrowed.iloc[0]
                        if pd.isnull(row['Deskripsi Penilaian']) or str(row['Deskripsi Penilaian']) == 'nan':
                            df_split.at[idx, 'Deskripsi Penilaian'] = recovered_row['Deskripsi Penilaian']
    return df_split

def load_split_data_with_recovery(split_path, raw_path):
    print(f"Loading data split from {split_path} with recovery from {raw_path}...")
    tr = pd.read_excel(split_path, sheet_name='Data Training (80%)')
    te = pd.read_excel(split_path, sheet_name='Data Testing (20%)')
    
    def normalize_cols(df):
        df = df.copy()
        if 'Sumber Data' not in df.columns:
            df['Sumber Data'] = df['Nama Siswa'] if 'Nama Siswa' in df.columns else ''
        return df
        
    tr = normalize_cols(tr)
    te = normalize_cols(te)
    
    tr = recover_missing_values(tr, raw_path)
    te = recover_missing_values(te, raw_path)
    
    tr['Set Data'] = 'Training'
    te['Set Data'] = 'Testing'
    
    df = pd.concat([tr, te], ignore_index=True)
    
    df['Nilai'] = pd.to_numeric(df['Nilai'], errors='coerce')
    df['Nilai'] = df['Nilai'].fillna(df['Nilai'].mean() if not df['Nilai'].isna().all() else 0)
    
    df.dropna(subset=['Deskripsi Penilaian', 'Aspek / Mapel', 'Label'], inplace=True)
    df['Deskripsi Penilaian'] = df['Deskripsi Penilaian'].astype(str).str.replace(r'(?i)deskripsi perkembangan\s*:\s*', '', regex=True)
    return df

def train_system_smote():
    # 1. Load Data
    df = load_split_data_with_recovery(SPLIT_PATH, DATA_PATH)
    print(f"Total rows: {len(df)}")

    # 2. Preprocessing
    df['clean_X2'] = df['Deskripsi Penilaian'].apply(clean_text)
    
    # 3. Encoding Targets
    le_aspek = LabelEncoder()
    le_label = LabelEncoder()
    
    y = np.vstack([
        le_aspek.fit_transform(df['Aspek / Mapel']),
        le_label.fit_transform(df['Label'])
    ]).T
    
    encoders = {'le_aspek': le_aspek, 'le_label': le_label}

    train_mask = (df['Set Data'] == 'Training').values
    test_mask = (df['Set Data'] == 'Testing').values

    # 4. Feature Extraction (TF-IDF)
    tfidf = TfidfVectorizer(max_features=500, ngram_range=(1, 1)) 
    tfidf.fit(df.loc[train_mask, 'clean_X2'])
    X_tfidf = tfidf.transform(df['clean_X2']).toarray()
    
    X_nilai = df[['Nilai']].values
    X = np.hstack([X_nilai, X_tfidf])
    
    # Split
    X_train, X_test = X[train_mask], X[test_mask]
    y_train, y_test = y[train_mask], y[test_mask]

    # --- APPLY SMOTE TO TRAINING DATA ---
    print(f"Original training distribution for Label (Y): {dict(pd.Series(y_train[:, 1]).value_counts())}")
    
    smote = SMOTE(random_state=42)
    X_train_res, y_train_label_res = smote.fit_resample(X_train, y_train[:, 1])
    
    y_train_aspek_res = np.zeros(len(X_train_res), dtype=int)
    y_train_aspek_res[:len(X_train)] = y_train[:, 0]
    
    if len(X_train_res) > len(X_train):
        nn = NearestNeighbors(n_neighbors=1)
        nn.fit(X_train)
        _, indices = nn.kneighbors(X_train_res[len(X_train):])
        for idx, orig_idx in enumerate(indices.flatten()):
            y_train_aspek_res[len(X_train) + idx] = y_train[orig_idx, 0]
            
    y_train_res = np.vstack([y_train_aspek_res, y_train_label_res]).T
    
    print(f"Resampled training distribution for Label (Y) after SMOTE: {dict(pd.Series(y_train_label_res).value_counts())}")
    print(f"Training features shape resampled: {X_train_res.shape}")

    # 5. Model Build
    rf = RandomForestClassifier(random_state=42)
    mo_clf = MultiOutputClassifier(rf)
    
    param_dist = {
        'estimator__n_estimators': [100, 200, 300, 400, 500],
        'estimator__max_depth': [10, 20, 30, None],
        'estimator__min_samples_split': [2, 5, 10],
        'estimator__min_samples_leaf': [1, 2, 4],
        'estimator__max_features': ['sqrt', 'log2']
    }
    
    random_search = RandomizedSearchCV(
        estimator=mo_clf,
        param_distributions=param_dist,
        n_iter=20,
        cv=5,
        n_jobs=-1,
        random_state=42,
        verbose=1
    )
    random_search.fit(X_train_res, y_train_res)
    
    best_model = random_search.best_estimator_
    print(f"Best Params: {random_search.best_params_}")

    # Evaluation
    print("\nEvaluation Results (SMOTE version):")
    y_pred = best_model.predict(X_test)
    
    outputs = [('Aspek / Mapel', le_aspek), ('Label', le_label)]
    for i, (name, encoder) in enumerate(outputs):
        print(f"\n--- Output {i+1}: {name} ---")
        unique_test = sorted(list(set(y_test[:, i]) | set(y_pred[:, i])))
        target_names = [encoder.classes_[idx] for idx in unique_test]
        print(classification_report(y_test[:, i], y_pred[:, i], labels=unique_test, target_names=target_names))
        
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

    # Explainable AI (SHAP)
    print("\nGenerating SHAP explanations...")
    X_sample = X_test[:50]
    feature_names_all = ['Nilai'] + ['tfidf_' + w for w in tfidf.get_feature_names_out()]

    for i, (name, encoder) in enumerate(outputs):
        print(f"Calculating SHAP for {name}...")
        explainer = shap.TreeExplainer(best_model.estimators_[i])
        shap_values = explainer.shap_values(X_sample)
        
        plt.figure(figsize=(10, 6))
        shap.summary_plot(shap_values, X_sample, feature_names=feature_names_all, show=False)
        plt.title(f"SHAP Summary: {name}")
        plt.savefig(f"shap_summary_{name.replace(' ', '_').replace('/', '')}.png")
        plt.close()
    
    print("SHAP plots saved.")

    # Save
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(best_model, MODEL_PATH)
    joblib.dump(tfidf, TFIDF_PATH)
    joblib.dump(encoders, ENCODERS_PATH)
    print(f"SMOTE System saved to: {MODEL_PATH}")

if __name__ == "__main__":
    train_system_smote()
