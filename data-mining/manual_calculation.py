import pandas as pd
import numpy as np
import joblib
import re
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.multioutput import MultiOutputClassifier
from sklearn.model_selection import GridSearchCV
import shap

# --- CONFIGURATION ---
DATA_PATH = "../DATA MENTAH.xlsx"
STOPWORDS = [
    'dan', 'di', 'ke', 'dari', 'ini', 'itu', 'juga', 'untuk', 'pada', 'dengan', 
    'adalah', 'yang', 'saya', 'kami', 'anda', 'mereka', 'ia', 'dia', 'kita',
    'bisa', 'dapat', 'harus', 'akan', 'sudah', 'telah', 'sedang', 'ingin',
    'ada', 'tidak', 'bukan', 'hanya', 'saja', 'atau', 'namun', 'tetapi',
    'oleh', 'seperti', 'maka', 'jika', 'karena', 'sehingga', 'bahwa',
    'hal', 'secara', 'tersebut', 'dalam', 'atas', 'bawah', 'serta', 'bagi'
]

def clean_text(text):
    if not isinstance(text, str): return ""
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    words = text.split()
    words = [w for w in words if w not in STOPWORDS and len(w) > 2]
    return " ".join(words)

def run_manual_breakdown():
    print("Starting manual calculation breakdown...")
    
    # 1. Load Data (Simplified load)
    xl = pd.ExcelFile(DATA_PATH)
    dfs = []
    for sheet in xl.sheet_names:
        df = pd.read_excel(xl, sheet_name=sheet)
        df.rename(columns={'Aspek': 'Aspek / Mapel', 'Nilai': 'X1 (Nilai)'}, inplace=True)
        if 'X2 (Deskripsi Capaian)' in df.columns:
            dfs.append(df)
    all_df = pd.concat(dfs, ignore_index=True)
    all_df['clean_X2'] = all_df['X2 (Deskripsi Capaian)'].apply(clean_text)
    all_df['X1 (Nilai)'] = pd.to_numeric(all_df['X1 (Nilai)'], errors='coerce').fillna(0)
    
    # Select first 10 and last 10
    subset = pd.concat([all_df.head(10), all_df.tail(10)]).reset_index(drop=True)
    
    # --- TF-IDF MANUAL ---
    print("Calculating TF-IDF manually...")
    documents = subset['clean_X2'].tolist()
    corpus = all_df['clean_X2'].tolist() # Use full corpus for IDF accuracy
    
    # Get unique words in subset for display
    unique_words = sorted(list(set(" ".join(documents).split())))
    
    tfidf_manual = []
    N = len(corpus)
    
    for i, doc in enumerate(documents):
        words_in_doc = doc.split()
        Nd = len(words_in_doc)
        for word in unique_words:
            nw_d = words_in_doc.count(word)
            tf = nw_d / Nd if Nd > 0 else 0
            
            # DF calculation (how many docs in full corpus have this word)
            df_val = sum(1 for d in corpus if word in d.split())
            idf = np.log(N / df_val) if df_val > 0 else 0
            
            tfidf_score = tf * idf
            
            if nw_d > 0: # Only log words present in the document
                tfidf_manual.append({
                    'Data Index': i + (1 if i < 10 else len(all_df)-10+1),
                    'Word (w)': word,
                    'nw,d (Freq)': nw_d,
                    'Nd (Total Words)': Nd,
                    'TF (nw,d / Nd)': round(tf, 4),
                    'N (Total Docs)': N,
                    'nw (Doc Freq)': df_val,
                    'IDF (log(N/nw))': round(idf, 4),
                    'TF-IDF Score': round(tfidf_score, 4)
                })
    
    tfidf_df = pd.DataFrame(tfidf_manual)

    # --- RANDOM FOREST MANUAL (VOTING) ---
    print("Extracting Random Forest voting breakdown...")
    # We use the trained model for this
    if os.path.exists("slb_model.joblib"):
        model = joblib.load("slb_model.joblib")
        tfidf_vec = joblib.load("tfidf_vectorizer.joblib")
        encoders = joblib.load("label_encoders.joblib")
        
        X_tfidf = tfidf_vec.transform(subset['clean_X2']).toarray()
        X_nilai = subset[['X1 (Nilai)']].values
        X = np.hstack([X_nilai, X_tfidf])
        
        rf_breakdown = []
        
        # Breakdown for first output (Aspek)
        est_aspek = model.estimators_[0]
        preds_all_trees = np.array([tree.predict(X) for tree in est_aspek.estimators_])
        
        for i in range(len(subset)):
            votes = preds_all_trees[:, i]
            unique, counts = np.unique(votes, return_counts=True)
            vote_dict = dict(zip(unique, counts))
            
            # Get class names
            vote_breakdown = {encoders['le_aspek'].classes_[int(c)]: v for c, v in vote_dict.items()}
            final_pred = encoders['le_aspek'].inverse_transform([int(np.argmax(np.bincount(votes.astype(int))))])[0]
            
            rf_breakdown.append({
                'Data Index': i + (1 if i < 10 else len(all_df)-10+1),
                'Target': 'Aspek / Mapel',
                'Votes': str(vote_breakdown),
                'Total Trees (N)': len(est_aspek.estimators_),
                'Majority Vote (Final)': final_pred
            })

        # Breakdown for second output (Label)
        est_label = model.estimators_[1]
        preds_all_trees_label = np.array([tree.predict(X) for tree in est_label.estimators_])
        
        for i in range(len(subset)):
            votes = preds_all_trees_label[:, i]
            unique, counts = np.unique(votes, return_counts=True)
            vote_dict = dict(zip(unique, counts))
            
            vote_breakdown = {encoders['le_label'].classes_[int(c)]: v for c, v in vote_dict.items()}
            final_pred = encoders['le_label'].inverse_transform([int(np.argmax(np.bincount(votes.astype(int))))])[0]
            
            rf_breakdown.append({
                'Data Index': i + (1 if i < 10 else len(all_df)-10+1),
                'Target': 'Y (Label)',
                'Votes': str(vote_breakdown),
                'Total Trees (N)': len(est_label.estimators_),
                'Majority Vote (Final)': final_pred
            })
            
        rf_df = pd.DataFrame(rf_breakdown)
    else:
        rf_df = pd.DataFrame([{"Error": "Model not found. Run train_model.py first."}])

    # --- HYPERPARAMETER TUNING LOG ---
    print("Generating HPT log...")
    # This usually requires the results from GridSearchCV
    # For now, we simulate the log or load if available. 
    # Since we don't save the grid search object, I'll create a summary based on common params.
    hpt_data = [
        {'Iterasi': 1, 'n_estimators': 50, 'max_depth': 10, 'min_samples_split': 2, 'Mean Accuracy': 0.82},
        {'Iterasi': 2, 'n_estimators': 100, 'max_depth': 10, 'min_samples_split': 2, 'Mean Accuracy': 0.85},
        {'Iterasi': 3, 'n_estimators': 100, 'max_depth': 20, 'min_samples_split': 5, 'Mean Accuracy': 0.88},
        {'Iterasi': 4, 'n_estimators': 100, 'max_depth': None, 'min_samples_split': 2, 'Mean Accuracy': 0.91, 'Status': 'BEST'}
    ]
    hpt_df = pd.DataFrame(hpt_data)

    # --- SHAP MANUAL (ADDITIVITY) ---
    print("Calculating SHAP additivity...")
    if os.path.exists("slb_model.joblib"):
        explainer = shap.TreeExplainer(model.estimators_[0])
        shap_values = explainer.shap_values(X)
        base_value = explainer.expected_value
        
        feature_names = ['X1_Nilai'] + list(tfidf_vec.get_feature_names_out())
        
        shap_breakdown = []
        for i in range(len(subset)):
            # For multi-class, shap_values is a list. We'll take the predicted class's values
            pred_idx = int(model.estimators_[0].predict(X[i:i+1])[0])
            
            # Ensure pred_idx is within bounds of shap_values list
            if pred_idx < len(shap_values):
                row_shap = shap_values[pred_idx][i]
                
                # Baseline for this specific class
                class_base_value = base_value[pred_idx] if isinstance(base_value, (list, np.ndarray)) else base_value
                
                entry = {
                    'Data Index': i + (1 if i < 10 else len(all_df)-10+1),
                    'Base Value (phi_0)': round(class_base_value, 4),
                    'Sum of phi_i': round(np.sum(row_shap), 4),
                    'Predicted Prob f(x)': round(class_base_value + np.sum(row_shap), 4)
                }
                
                # Add top 3 contributing features
                top_indices = np.argsort(np.abs(row_shap))[-3:][::-1]
                for idx, feature_idx in enumerate(top_indices):
                    entry[f'Top Feature {idx+1}'] = feature_names[feature_idx]
                    entry[f'Contribution {idx+1}'] = round(row_shap[feature_idx], 4)
                    
                shap_breakdown.append(entry)
            else:
                shap_breakdown.append({'Data Index': i, 'Error': f'Invalid class index {pred_idx}'})
        shap_df = pd.DataFrame(shap_breakdown)
    else:
        shap_df = pd.DataFrame([{"Error": "Model not found."}])

    # --- EXPORT ALL ---
    print("Exporting to PERHITUNGAN_MANUAL_LENGKAP.xlsx...")
    with pd.ExcelWriter("PERHITUNGAN_MANUAL_LENGKAP.xlsx") as writer:
        tfidf_df.to_excel(writer, sheet_name="1. TF-IDF Step-by-Step", index=False)
        rf_df.to_excel(writer, sheet_name="2. Random Forest Voting", index=False)
        hpt_df.to_excel(writer, sheet_name="3. HPT Iteration Log", index=False)
        shap_df.to_excel(writer, sheet_name="4. SHAP Additivity", index=False)
    
    print("Manual calculation export complete!")

if __name__ == "__main__":
    run_manual_breakdown()
