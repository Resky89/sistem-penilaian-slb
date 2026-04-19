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
DATA_PATH = "DATA MENTAH.xlsx"
MODEL_PATH = "slb_model.joblib"
TFIDF_PATH = "tfidf_vectorizer.joblib"
ENCODERS_PATH = "label_encoders.joblib"

def clean_text(text):
    """Basic text cleaning for Indonesian achievement descriptions."""
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def load_and_consolidate_data(file_path):
    """Loads all sheets and consolidates them into a single DataFrame."""
    print(f"Loading data from {file_path}...")
    xl = pd.ExcelFile(file_path)
    dfs = []
    
    for sheet in xl.sheet_names:
        df = pd.read_excel(xl, sheet_name=sheet)
        # Handle column naming inconsistencies
        df.rename(columns={'Aspek': 'Aspek / Mapel'}, inplace=True)
        # Ensure required columns exist
        required_cols = ['Aspek / Mapel', 'X2 (Deskripsi Capaian)', 'Y (Label)']
        if all(col in df.columns for col in required_cols):
            dfs.append(df[required_cols])
            
    if not dfs:
        raise ValueError("No valid data found in the Excel file.")
        
    all_df = pd.concat(dfs, ignore_index=True)
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
    tfidf = TfidfVectorizer(max_features=1000, ngram_range=(1, 2))
    X = tfidf.fit_transform(df['clean_X2'])

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
    
    print("\n--- Output 1: Aspek / Mapel ---")
    unique_test_aspek = sorted(list(set(y_test[:, 0]) | set(y_pred[:, 0])))
    print(classification_report(y_test[:, 0], y_pred[:, 0], 
                                labels=unique_test_aspek,
                                target_names=[le_aspek.classes_[i] for i in unique_test_aspek]))
    
    print("\n--- Output 2: Y (Label) ---")
    unique_test_label = sorted(list(set(y_test[:, 1]) | set(y_pred[:, 1])))
    print(classification_report(y_test[:, 1], y_pred[:, 1], 
                                labels=unique_test_label,
                                target_names=[le_label.classes_[i] for i in unique_test_label]))

    # 8. Explainable AI (SHAP)
    print("\nGenerating SHAP explanations...")
    # SHAP needs a background dataset, we'll use a sample of training data
    # Note: MultiOutput SHAP requires explaining individual estimators
    explainer_aspek = shap.TreeExplainer(best_model.estimators_[0])
    explainer_label = shap.TreeExplainer(best_model.estimators_[1])
    
    # Take a small sample for SHAP values calculation to save time
    X_sample = X_test[:50].toarray()
    shap_values_aspek = explainer_aspek.shap_values(X_sample)
    shap_values_label = explainer_label.shap_values(X_sample)
    
    # Save a summary plot for Aspect (Note: shap 0.45+ has different return types for RF)
    plt.figure(figsize=(10, 6))
    shap.summary_plot(shap_values_aspek, X_sample, feature_names=tfidf.get_feature_names_out(), show=False)
    plt.title("SHAP Summary: Aspek / Mapel")
    plt.savefig("shap_summary_aspek.png")
    plt.close()

    plt.figure(figsize=(10, 6))
    shap.summary_plot(shap_values_label, X_sample, feature_names=tfidf.get_feature_names_out(), show=False)
    plt.title("SHAP Summary: Y (Label)")
    plt.savefig("shap_summary_label.png")
    plt.close()
    
    print("SHAP plots saved as 'shap_summary_aspek.png' and 'shap_summary_label.png'.")

    # 9. Save System
    joblib.dump(best_model, MODEL_PATH)
    joblib.dump(tfidf, TFIDF_PATH)
    joblib.dump(encoders, ENCODERS_PATH)
    print(f"System saved: {MODEL_PATH}, {TFIDF_PATH}, {ENCODERS_PATH}")

if __name__ == "__main__":
    train_system()
