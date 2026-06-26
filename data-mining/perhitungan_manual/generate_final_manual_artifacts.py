import re
import math
import ast
import zipfile
import shutil
import tempfile
from pathlib import Path
from xml.sax.saxutils import escape

import numpy as np
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import RandomizedSearchCV, train_test_split
from sklearn.metrics import accuracy_score

BASE = Path(r"D:/projects/Sistem-Penilaian-SLB")
DM = BASE / "data-mining"
RAW_PATH = BASE / "DATA MENTAH.xlsx"
SPLIT_PATH = BASE / "DATA_SPLIT_TRAIN_TEST.xlsx"
TEMPLATE_DOCX = BASE / "Panduan_Perhitungan_Manual_Skripsi.docx"
OUT_XLSX = DM / "perhitungan_manual" / "PERHITUNGAN_MANUAL_FINAL_SEMUA_DATA_RESKY.xlsx"
OUT_DOCX = BASE / "DOKUMEN_PERHITUNGAN_MANUAL_FINAL_RESKY.docx"

STOPWORDS = set([
     # Standard stopwords
    'dan', 'di', 'ke', 'dari', 'ini', 'itu', 'juga', 'untuk', 'pada', 'dengan',
    'adalah', 'yang', 'saya', 'kami', 'anda', 'mereka', 'ia', 'dia', 'kita', 
    'dapat', 'harus', 'akan', 'sudah', 'telah', 'sedang', 'ingin',
    'ada', 'bukan', 'hanya', 'saja', 'atau', 'namun', 'tetapi',
    'oleh', 'seperti', 'maka', 'jika', 'karena', 'sehingga', 'bahwa',
    'hal', 'secara', 'tersebut', 'dalam', 'atas', 'bawah', 'serta', 'bagi', 'setelah',
    # Domain-specific stopwords (Sistem Penilaian SLB)
    'peserta', 'didik', 'siswa', 'aspek', 'kegiatan', 'aktivitas', 'cara', 
    'berikan', 'gunakan', 'saran', 'hari',
    # Nama Siswa (Ditemukan di dalam teks deskripsi capaian)
    'dafa', 'dzikri', 'eria', 'arif', 'arifin', 'rama', 'fadil', 'afif', 
    'azzam', 'dewi', 'faiz', 'ahmad', 'bilqis', 'rizky', 'mia', 'andreansyah', 
    'rahman', 'khansa', 'robi', 'roby'
])

def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r"[^a-zA-Z\s]", " ", text)
    words = [w for w in text.split() if len(w) > 2 and w not in STOPWORDS]
    return " ".join(words)

def recover_missing_values(df_split, raw_path):
    if not Path(raw_path).exists():
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

def normalize_cols(df):
    df = df.copy()
    if 'Sumber Data' not in df.columns:
        df['Sumber Data'] = df['Nama Siswa'] if 'Nama Siswa' in df.columns else ''
    return df

def load_data():
    if SPLIT_PATH.exists():
        tr = normalize_cols(pd.read_excel(SPLIT_PATH, sheet_name='Data Training (80%)'))
        te = normalize_cols(pd.read_excel(SPLIT_PATH, sheet_name='Data Testing (20%)'))
        tr = recover_missing_values(tr, RAW_PATH)
        te = recover_missing_values(te, RAW_PATH)
        tr['Set Data'] = 'Training'; te['Set Data'] = 'Testing'
        data = pd.concat([tr, te], ignore_index=True)
    else:
        xl = pd.ExcelFile(RAW_PATH)
        rows = []
        for sheet in xl.sheet_names:
            df = normalize_cols(pd.read_excel(RAW_PATH, sheet_name=sheet))
            df['Sumber Data'] = sheet.replace('Data Mentah ', '')
            rows.append(df)
        data = pd.concat(rows, ignore_index=True)
        data['Set Data'] = 'All'
    need = ['Sumber Data','Aspek / Mapel','Nilai','Deskripsi Penilaian','Label','Set Data']
    data = data[[c for c in need if c in data.columns]].copy()
    data['Nilai'] = pd.to_numeric(data['Nilai'], errors='coerce').fillna(0)
    data = data.dropna(subset=['Aspek / Mapel','Deskripsi Penilaian','Label']).reset_index(drop=True)
    data.insert(0, 'ID_Data', np.arange(1, len(data)+1))
    data['Teks Bersih'] = data['Deskripsi Penilaian'].apply(clean_text)
    return data

def gini(counts):
    total = int(np.sum(counts))
    if total == 0:
        return 0.0
    return float(1 - np.sum((np.array(counts) / total) ** 2))

def style_ws(ws):
    fill = PatternFill('solid', fgColor='1F4E78')
    font = Font(color='FFFFFF', bold=True)
    thin = Side(style='thin', color='D9E2F3')
    for row in ws.iter_rows():
        for c in row:
            c.alignment = Alignment(vertical='top', wrap_text=True)
            c.border = Border(left=thin, right=thin, top=thin, bottom=thin)
    if ws.max_row >= 1:
        for c in ws[1]:
            c.fill = fill; c.font = font
            c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    ws.freeze_panes = 'A2'
    for i in range(1, ws.max_column + 1):
        col = get_column_letter(i)
        mx = 10
        for c in ws[col]:
            v = '' if c.value is None else str(c.value)
            mx = min(max(mx, len(v)), 55)
        ws.column_dimensions[col].width = mx + 2

def write_df(ws, df, start_row=1, title=None):
    r = start_row
    if title:
        ws.cell(r, 1, title).font = Font(bold=True, size=13, color='1F4E78')
        r += 1
    for j, col in enumerate(df.columns, 1):
        ws.cell(r, j, col)
    for i, row in enumerate(df.itertuples(index=False), r+1):
        for j, val in enumerate(row, 1):
            ws.cell(i, j, val)
    return r + len(df) + 2

def add_sheet(wb, name, df):
    ws = wb.create_sheet(name[:31])
    write_df(ws, df)
    style_ws(ws)
    return ws

def build():
    data = load_data()
    
    if set(data['Set Data']) >= {'Training','Testing'}:
        train_mask = data['Set Data'].eq('Training').values
        test_mask = data['Set Data'].eq('Testing').values
    else:
        train_mask = np.ones(len(data), dtype=bool)
        test_mask = np.zeros(len(data), dtype=bool)

    # IMPORTANT: this follows sklearn TfidfVectorizer defaults: use_idf=True, smooth_idf=True, norm='l2', sublinear_tf=False.
    # Fit TF-IDF only on training data (train_mask)
    tfidf = TfidfVectorizer(max_features=50, min_df=2, max_df=0.85, ngram_range=(1,1), smooth_idf=True, norm='l2', use_idf=True, sublinear_tf=False)
    tfidf.fit(data.loc[train_mask, 'Teks Bersih'])
    X_tfidf = tfidf.transform(data['Teks Bersih']).toarray()
    words = list(tfidf.get_feature_names_out())
    tfidf_cols = [f'tfidf_{w}' for w in words]

    try:
        ohe = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
    except TypeError:
        ohe = OneHotEncoder(sparse=False, handle_unknown='ignore')
    X_aspek = ohe.fit_transform(data[['Aspek / Mapel']])
    aspek_cols = [f'aspek_{a}' for a in ohe.categories_[0]]
    X = np.hstack([data[['Nilai']].values, X_tfidf, X_aspek])
    feature_names = ['Nilai'] + tfidf_cols + aspek_cols
    le = LabelEncoder(); y = le.fit_transform(data['Label'].astype(str)); labels = list(le.classes_)

    X_train, X_test = X[train_mask], X[test_mask]
    y_train, y_test = y[train_mask], y[test_mask]

    rf = RandomForestClassifier(n_estimators=10, max_depth=3, min_samples_split=2, random_state=42, bootstrap=True)
    rf.fit(X_train, y_train)
    pred_all = rf.predict(X); proba_all = rf.predict_proba(X)

    param_dist = {
        'n_estimators': [100, 200, 300, 400, 500],
        'max_depth': [10, 20, 30, None],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 4],
        'max_features': ['sqrt', 'log2']
    }
    grid = RandomizedSearchCV(
        estimator=RandomForestClassifier(random_state=42, bootstrap=True),
        param_distributions=param_dist,
        n_iter=20,
        cv=5,
        scoring='accuracy',
        n_jobs=-1,
        random_state=42,
        return_train_score=True
    )
    grid.fit(X_train, y_train)

    transformed = data.copy()
    transformed['Y_Encoded'] = y
    transformed['Y_Prediksi'] = le.inverse_transform(pred_all)
    transformed['Prediksi_Benar'] = transformed['Y_Prediksi'].eq(transformed['Label'])

    matrix = pd.concat([data[['ID_Data','Sumber Data','Aspek / Mapel','Set Data','Nilai','Label','Teks Bersih']], pd.DataFrame(np.round(X_tfidf,6), columns=tfidf_cols)], axis=1)

    # Manual TF-IDF identical to sklearn: tf = raw count, idf = ln((1+N)/(1+df))+1, tfidf_raw=tf*idf, final=tfidf_raw/L2_norm.
    vocab_index = {w:i for i,w in enumerate(words)}
    docs = [d.split() for d in data['Teks Bersih']]
    docs_train = [d.split() for d in data.loc[train_mask, 'Teks Bersih']]
    N_train = len(docs_train)
    df_train = {w: sum(1 for doc in docs_train if w in set(doc)) for w in words}
    idf_train = {w: math.log((1+N_train)/(1+df_train[w])) + 1 for w in words}
    rows=[]
    for r, doc in enumerate(docs):
        counts = pd.Series(doc).value_counts().to_dict() if doc else {}
        raw_vals = {w: counts.get(w,0) * idf_train[w] for w in words}
        l2 = math.sqrt(sum(v*v for v in raw_vals.values()))
        for w in words:
            c = counts.get(w,0)
            if c or X_tfidf[r, vocab_index[w]] != 0:
                raw = raw_vals[w]
                final = raw / l2 if l2 else 0
                py_val = float(X_tfidf[r, vocab_index[w]])
                rows.append({
                    'ID_Data': int(data.loc[r,'ID_Data']), 'Siswa': data.loc[r,'Sumber Data'], 'Aspek / Mapel': data.loc[r,'Aspek / Mapel'],
                    'Kata': w, 'tf raw (jumlah kata)': int(c), 'N': N_train, 'df(w)': int(df_train[w]),
                    'idf sklearn = ln((1+N)/(1+df))+1': round(idf_train[w], 9),
                    'tf × idf': round(raw, 9), 'L2 norm dokumen': round(l2, 9),
                    'TF-IDF Manual Setelah L2': round(final, 9), 'TF-IDF Python sklearn': round(py_val, 9),
                    'Selisih': round(final - py_val, 12)
                })
    tfidf_manual = pd.DataFrame(rows)

    # Per-tree calculations.
    tree_paths_all=[]; votes=[]; gini_all=[]; tree_structures=[]
    for t_idx, est in enumerate(rf.estimators_, 1):
        tree = est.tree_
        decision_path_train = est.decision_path(X_train).toarray().astype(bool)
        for node in range(tree.node_count):
            is_leaf = tree.children_left[node] == tree.children_right[node]
            value = tree.value[node][0]
            pred_cls = int(np.argmax(value))
            row = {'Pohon ke-':t_idx,'Node':node,'Jenis Node':'Leaf' if is_leaf else 'Internal','Prediksi Node':le.inverse_transform([pred_cls])[0], 'Distribusi Kelas':str(dict(zip(labels, value.astype(int))))}
            if is_leaf:
                row.update({'Fitur Split':'-','Threshold':'-','Cabang Kiri':'-','Cabang Kanan':'-'})
            else:
                fi=tree.feature[node]
                row.update({'Fitur Split':feature_names[fi],'Threshold':round(float(tree.threshold[node]),9),'Cabang Kiri':int(tree.children_left[node]),'Cabang Kanan':int(tree.children_right[node])})
            tree_structures.append(row)
        for node in range(tree.node_count):
            if tree.children_left[node] == tree.children_right[node]:
                continue
            fi=tree.feature[node]; thr=tree.threshold[node]
            at_node = decision_path_train[:,node]
            left = at_node & (X_train[:,fi] <= thr); right = at_node & (X_train[:,fi] > thr)
            y_node, y_left, y_right = y_train[at_node], y_train[left], y_train[right]
            cnt_node=np.bincount(y_node, minlength=len(labels)); cnt_left=np.bincount(y_left, minlength=len(labels)); cnt_right=np.bincount(y_right, minlength=len(labels))
            gp, gl, gr = gini(cnt_node), gini(cnt_left), gini(cnt_right)
            n, nl, nr = len(y_node), len(y_left), len(y_right)
            gs = (nl/n)*gl + (nr/n)*gr if n else 0
            gini_all.append({'Pohon ke-':t_idx,'Node':node,'Fitur':feature_names[fi],'Threshold':round(float(thr),9),'n Node':n,'Distribusi Node':str(dict(zip(labels,cnt_node.astype(int)))),'Gini Node':round(gp,9),'n Kiri':nl,'Distribusi Kiri':str(dict(zip(labels,cnt_left.astype(int)))),'Gini Kiri':round(gl,9),'n Kanan':nr,'Distribusi Kanan':str(dict(zip(labels,cnt_right.astype(int)))),'Gini Kanan':round(gr,9),'Gini Split':round(gs,9),'Gain Gini':round(gp-gs,9)})
        for i in range(len(data)):
            node=0; step=1; xrow=X[i]
            while tree.children_left[node] != tree.children_right[node]:
                fi=tree.feature[node]; thr=tree.threshold[node]; val=xrow[fi]
                go_left = val <= thr; nxt = tree.children_left[node] if go_left else tree.children_right[node]
                tree_paths_all.append({'ID_Data':int(data.loc[i,'ID_Data']),'Siswa':data.loc[i,'Sumber Data'],'Aspek / Mapel':data.loc[i,'Aspek / Mapel'],'Pohon ke-':t_idx,'Langkah':step,'Node':int(node),'Aturan':f'{feature_names[fi]} <= {thr:.9f}','Nilai Data':round(float(val),9),'Keputusan':'Kiri' if go_left else 'Kanan','Node Berikutnya':int(nxt)})
                node=nxt; step+=1
            pred_cls=int(np.argmax(tree.value[node][0])); pred_label=le.inverse_transform([pred_cls])[0]
            tree_paths_all.append({'ID_Data':int(data.loc[i,'ID_Data']),'Siswa':data.loc[i,'Sumber Data'],'Aspek / Mapel':data.loc[i,'Aspek / Mapel'],'Pohon ke-':t_idx,'Langkah':step,'Node':int(node),'Aturan':'Leaf','Nilai Data':'-','Keputusan':f'Prediksi = {pred_label}','Node Berikutnya':'-'})
            votes.append({'ID_Data':int(data.loc[i,'ID_Data']),'Siswa':data.loc[i,'Sumber Data'],'Aspek / Mapel':data.loc[i,'Aspek / Mapel'],'Pohon ke-':t_idx,'Prediksi Pohon':pred_label})

    tree_structures=pd.DataFrame(tree_structures); gini_all=pd.DataFrame(gini_all); tree_paths_all=pd.DataFrame(tree_paths_all); votes=pd.DataFrame(votes)
    vote_recap = votes.groupby(['ID_Data','Siswa','Aspek / Mapel','Prediksi Pohon']).size().reset_index(name='Jumlah Suara')
    final_vote = vote_recap.sort_values(['ID_Data','Jumlah Suara'], ascending=[True,False]).groupby('ID_Data').head(1).rename(columns={'Prediksi Pohon':'Hasil Voting'})
    final_vote = final_vote.merge(data[['ID_Data','Label']], on='ID_Data', how='left')
    final_vote['Benar/Salah'] = np.where(final_vote['Hasil Voting'].eq(final_vote['Label']), 'Benar', 'Salah')

    hpt = pd.DataFrame(grid.cv_results_)[['param_n_estimators','param_max_depth','param_min_samples_split','param_min_samples_leaf','param_max_features','mean_train_score','mean_test_score','rank_test_score']].copy()
    hpt.columns = ['n_estimators','max_depth','min_samples_split','min_samples_leaf','max_features','Mean Train Accuracy','Mean CV Accuracy','Ranking']
    hpt=hpt.sort_values(['Ranking','n_estimators']).reset_index(drop=True)
    hpt['Status']=np.where(hpt['Ranking'].eq(1),'Best','-')
    hpt['Mean Train Accuracy']=hpt['Mean Train Accuracy'].round(9); hpt['Mean CV Accuracy']=hpt['Mean CV Accuracy'].round(9)

    # Multi-output view: label output for every aspek/mapel per student.
    multi_long = transformed[['Sumber Data','Aspek / Mapel','Nilai','Label','Y_Prediksi']].copy()
    multi_long['Makna'] = 'Output label perkembangan untuk aspek/mapel ini'
    actual = multi_long.pivot_table(index='Sumber Data', columns='Aspek / Mapel', values='Label', aggfunc='first')
    pred = multi_long.pivot_table(index='Sumber Data', columns='Aspek / Mapel', values='Y_Prediksi', aggfunc='first')
    actual.columns=[f'Aktual_{c}' for c in actual.columns]; pred.columns=[f'Prediksi_{c}' for c in pred.columns]
    multi_wide=pd.concat([actual,pred],axis=1).reset_index()

    # SHAP-like manual additive using feature ablation. Documented as manual approximation for explaining RF prediction.
    baseline = np.mean(X_train, axis=0)
    shap_rows=[]; shap_summary=[]
    for i in range(len(data)):
        xrow=X[i]; cls=int(pred_all[i]); cls_label=le.inverse_transform([cls])[0]
        fx=float(proba_all[i,cls]); base=float(np.mean(rf.predict_proba(X_train)[:,cls]))
        active=[0]+[j for j,v in enumerate(xrow) if j>0 and abs(v)>1e-12]
        raw=[]
        for fi in active:
            xabl=xrow.copy(); xabl[fi]=baseline[fi]
            pabl=float(rf.predict_proba(xabl.reshape(1,-1))[0,cls])
            raw.append((fi, fx-pabl, pabl))
        raw=sorted(raw,key=lambda z:abs(z[1]),reverse=True)[:10]
        total=sum(v for _,v,_ in raw); scale=(fx-base)/total if abs(total)>1e-12 else 0
        sum_phi=0
        for fi,delta,pabl in raw:
            phi=delta*scale; sum_phi += phi
            shap_rows.append({'ID_Data':int(data.loc[i,'ID_Data']),'Siswa':data.loc[i,'Sumber Data'],'Aspek / Mapel':data.loc[i,'Aspek / Mapel'],'Kelas Dijelaskan':cls_label,'Fitur':feature_names[fi],'Nilai Fitur':round(float(xrow[fi]),9),'f(x) Asli':round(fx,9),'f(x) Tanpa Fitur':round(pabl,9),'Δ=f(x)-f(x tanpa fitur)':round(delta,9),'φi SHAP Manual':round(phi,9),'Interpretasi':'Menaikkan peluang output' if phi>0 else ('Menurunkan peluang output' if phi<0 else 'Netral')})
        shap_summary.append({'ID_Data':int(data.loc[i,'ID_Data']),'Siswa':data.loc[i,'Sumber Data'],'Aspek / Mapel':data.loc[i,'Aspek / Mapel'],'Output Prediksi':cls_label,'φ0 Base Value':round(base,9),'Σφi':round(sum_phi,9),'f(x)=φ0+Σφi':round(base+sum_phi,9),'Probabilitas Model':round(fx,9)})
    shap_rows=pd.DataFrame(shap_rows); shap_summary=pd.DataFrame(shap_summary)

    formula = pd.DataFrame([
        ['TF raw sklearn','tf(w,d)=n(w,d)','TfidfVectorizer memakai raw count, bukan n/Nd.'],
        ['IDF sklearn','idf(w)=ln((1+N)/(1+df(w)))+1','Karena smooth_idf=True secara default.'],
        ['TF-IDF sebelum normalisasi','v(w,d)=tf(w,d)×idf(w)','Bobot awal kata.'],
        ['L2 norm','||v_d||₂=sqrt(Σ v(w,d)^2)','Panjang vektor dokumen.'],
        ['TF-IDF akhir','tfidf(w,d)=v(w,d)/||v_d||₂','Nilai ini sama dengan Python sklearn.'],
        ['Gini','Gini(D)=1-Σp_i²','Impurity node.'],
        ['Gini Split','Gini_split=(n1/n)Gini(D1)+(n2/n)Gini(D2)','Nilai pemisahan node.'],
        ['Voting','ŷ=mode{h1(x),h2(x),...,hT(x)}','Suara mayoritas pohon.'],
        ['Multi-output','Yi=[yi1,yi2,...,yim]','Output label per aspek/mapel siswa.'],
        ['SHAP','f(x)=φ0+Σφi','Prediksi dijelaskan sebagai kontribusi fitur.']
    ], columns=['Nama','Rumus','Keterangan'])
    summary = pd.DataFrame([
        ['Jumlah data',len(data)],['Jumlah training',len(X_train)],['Jumlah testing',len(X_test)],['Output model','Label: Baik, Cukup, Perlu Bimbingan'],['Aspek/Mapel','Konteks/input, bukan output prediksi'],['TF-IDF','Manual mengikuti sklearn: smooth_idf=True dan L2 normalization'],['Jumlah fitur TF-IDF',len(tfidf_cols)],['Jumlah fitur aspek/mapel',len(aspek_cols)],['Total fitur',len(feature_names)],['Akurasi testing',round(accuracy_score(y_test, rf.predict(X_test)),9)],['Best HPT',str(grid.best_params_)],['Best CV Accuracy',round(float(grid.best_score_),9)]
    ], columns=['Keterangan','Nilai'])
    return locals()

def add_explanation_sheet(wb):
    ws = wb.create_sheet('BACA DULU - URUTAN')
    rows = [
        ['Urutan', 'Tahap', 'Yang dihitung', 'Buka sheet', 'Penjelasan singkat'],
        [1, 'Dataset awal', 'Data siswa, aspek/mapel, nilai, deskripsi, dan label asli.', 'DATASET KESELURUHAN', 'Ini sumber semua perhitungan. Kolom X1 adalah nilai angka, X2 adalah teks deskripsi capaian, Y adalah label target.'],
        [2, 'Pembersihan teks', 'Deskripsi Penilaian diubah menjadi teks bersih.', 'Transformasi Data', 'Huruf dibuat kecil, tanda baca dibuang, kata umum/stopword dibuang. Hasilnya dipakai untuk TF-IDF.'],
        [3, 'TF-IDF', 'Bobot setiap kata pada setiap dokumen.', 'TF-IDF Rumus Excel', 'Excel menghitung jumlah kata, df, idf, tf×idf, L2 norm, lalu TF-IDF akhir dengan rumus di kolom.'],
        [4, 'Random Forest - Gini', 'Kualitas split pada node pohon.', 'Gini Rumus Excel', 'Excel menghitung Gini parent, Gini kiri, Gini kanan, Gini split, dan gain dengan rumus.'],
        [5, 'Random Forest - Jalur pohon', 'Arah kiri/kanan setiap data di setiap node.', 'Jalur Semua Data', 'Jika nilai fitur <= threshold maka ke kiri, selain itu ke kanan, sampai leaf.'],
        [6, 'Voting', 'Suara dari pohon-pohon Random Forest.', 'Voting Rumus Excel', 'Excel menghitung jumlah suara per label dan mengambil suara terbanyak.'],
        [7, 'Hyperparameter tuning', 'Mencoba kombinasi parameter RF.', 'Hyperparameter Tuning', 'Kombinasi dengan ranking 1 menjadi parameter terbaik.'],
        [8, 'SHAP/kontribusi fitur', 'Pengaruh fitur terhadap probabilitas prediksi.', 'SHAP Rumus Excel', 'Excel menunjukkan rumus φ0 + Σφi dan selisih ke probabilitas model.'],
    ]
    for r, row in enumerate(rows, 1):
        for c, val in enumerate(row, 1):
            ws.cell(r, c, val)
    style_ws(ws)
    return ws


def add_tfidf_formula_sheet(wb, obj):
    ws = wb.create_sheet('TF-IDF Rumus Excel')
    headers = [
        'ID_Data', 'Siswa', 'Aspek / Mapel', 'Kata', 'Teks Bersih',
        'tf raw = jumlah kata', 'N total dokumen', 'df(w)',
        'idf = LN((1+N)/(1+df))+1', 'tf × idf', 'L2 norm dokumen',
        'TF-IDF Excel = (tf×idf)/L2', 'TF-IDF Python sklearn', 'Selisih Excel-Python',
        'Penjelasan'
    ]
    for c, h in enumerate(headers, 1):
        ws.cell(1, c, h)

    tfidf_manual = obj['tfidf_manual'].copy()
    text_by_id = obj['transformed'].set_index('ID_Data')['Teks Bersih'].to_dict()
    first_row_by_id = {}
    last_row = len(tfidf_manual) + 1
    for idx, (_, row) in enumerate(tfidf_manual.iterrows(), 2):
        id_data = int(row['ID_Data'])
        first_row_by_id.setdefault(id_data, idx)
        ws.cell(idx, 1, id_data)
        ws.cell(idx, 2, row['Siswa'])
        ws.cell(idx, 3, row['Aspek / Mapel'])
        ws.cell(idx, 4, row['Kata'])
        ws.cell(idx, 5, text_by_id.get(id_data, ''))
        ws.cell(idx, 6, f'=SUMPRODUCT(--(TEXTSPLIT(E{idx}," ")=D{idx}))')
        ws.cell(idx, 7, int(row['N']))
        ws.cell(idx, 8, row['df(w)'])
        ws.cell(idx, 9, f'=LN((1+G{idx})/(1+H{idx}))+1')
        ws.cell(idx, 10, f'=F{idx}*I{idx}')
        ws.cell(idx, 11, 0)  # filled after all rows so each document can use its own range
        ws.cell(idx, 12, f'=IF(K{idx}=0,0,J{idx}/K{idx})')
        ws.cell(idx, 13, row['TF-IDF Python sklearn'])
        ws.cell(idx, 14, f'=L{idx}-M{idx}')
        ws.cell(idx, 15, 'Urutan: hitung jumlah kata → hitung IDF → kalikan tf×idf → normalisasi L2. Kolom F, I, J, K, L, N memakai rumus Excel.')

    id_to_rows = {}
    for r in range(2, last_row + 1):
        id_to_rows.setdefault(ws.cell(r, 1).value, []).append(r)
    for rows in id_to_rows.values():
        start, end = rows[0], rows[-1]
        for r in rows:
            ws.cell(r, 11, f'=SQRT(SUMSQ($J${start}:$J${end}))')
    style_ws(ws)
    return ws


def _parse_distribution(text):
    try:
        return ast.literal_eval(str(text))
    except Exception:
        return {}


def add_gini_formula_sheet(wb, obj):
    ws = wb.create_sheet('Gini Rumus Excel')
    labels = list(obj['labels'])
    headers = ['Pohon ke-', 'Node', 'Fitur', 'Threshold', 'n Node']
    headers += [f'Node {label}' for label in labels] + ['Gini Node']
    headers += ['n Kiri'] + [f'Kiri {label}' for label in labels] + ['Gini Kiri']
    headers += ['n Kanan'] + [f'Kanan {label}' for label in labels] + ['Gini Kanan', 'Gini Split', 'Gain Gini', 'Penjelasan']
    for c, h in enumerate(headers, 1):
        ws.cell(1, c, h)
    gini_df = obj['gini_all']
    for r, (_, row) in enumerate(gini_df.iterrows(), 2):
        node_dist = _parse_distribution(row['Distribusi Node'])
        left_dist = _parse_distribution(row['Distribusi Kiri'])
        right_dist = _parse_distribution(row['Distribusi Kanan'])
        base = [row['Pohon ke-'], row['Node'], row['Fitur'], row['Threshold'], row['n Node']]
        for c, val in enumerate(base, 1): ws.cell(r, c, val)
        c = 6
        for label in labels:
            ws.cell(r, c, int(node_dist.get(label, 0))); c += 1
        node_count_range = f'{get_column_letter(6)}{r}:{get_column_letter(5+len(labels))}{r}'
        ws.cell(r, c, f'=1-SUMPRODUCT(({node_count_range}/E{r})^2)'); c += 1
        left_n_col = c; ws.cell(r, c, row['n Kiri']); c += 1
        left_start = c
        for label in labels:
            ws.cell(r, c, int(left_dist.get(label, 0))); c += 1
        left_range = f'{get_column_letter(left_start)}{r}:{get_column_letter(c-1)}{r}'
        ws.cell(r, c, f'=IF({get_column_letter(left_n_col)}{r}=0,0,1-SUMPRODUCT(({left_range}/{get_column_letter(left_n_col)}{r})^2))'); c += 1
        right_n_col = c; ws.cell(r, c, row['n Kanan']); c += 1
        right_start = c
        for label in labels:
            ws.cell(r, c, int(right_dist.get(label, 0))); c += 1
        right_range = f'{get_column_letter(right_start)}{r}:{get_column_letter(c-1)}{r}'
        ws.cell(r, c, f'=IF({get_column_letter(right_n_col)}{r}=0,0,1-SUMPRODUCT(({right_range}/{get_column_letter(right_n_col)}{r})^2))'); c += 1
        gini_node_col = 6 + len(labels)
        gini_left_col = left_start + len(labels)
        gini_right_col = right_start + len(labels)
        ws.cell(r, c, f'=({get_column_letter(left_n_col)}{r}/E{r})*{get_column_letter(gini_left_col)}{r}+({get_column_letter(right_n_col)}{r}/E{r})*{get_column_letter(gini_right_col)}{r}'); c += 1
        split_col = c - 1
        ws.cell(r, c, f'={get_column_letter(gini_node_col)}{r}-{get_column_letter(split_col)}{r}'); c += 1
        ws.cell(r, c, 'Gini kecil berarti data makin murni. Gain = Gini node sebelum split - Gini split sesudah dipisah.')
    style_ws(ws)
    return ws


def add_voting_formula_sheet(wb, obj):
    ws = wb.create_sheet('Voting Rumus Excel')
    labels = list(obj['labels'])
    headers = ['ID_Data', 'Siswa', 'Aspek / Mapel'] + [f'Pohon {i}' for i in range(1, 11)] + [f'Jumlah {label}' for label in labels] + ['Hasil Voting Excel', 'Label Aktual', 'Benar/Salah', 'Penjelasan']
    for c, h in enumerate(headers, 1): ws.cell(1, c, h)
    vote_pivot = obj['votes'].pivot_table(index=['ID_Data','Siswa','Aspek / Mapel'], columns='Pohon ke-', values='Prediksi Pohon', aggfunc='first').reset_index()
    actual = obj['transformed'].set_index('ID_Data')['Label'].to_dict()
    for r, (_, row) in enumerate(vote_pivot.iterrows(), 2):
        id_data = int(row['ID_Data'])
        ws.cell(r, 1, id_data); ws.cell(r, 2, row['Siswa']); ws.cell(r, 3, row['Aspek / Mapel'])
        for i in range(1, 11):
            ws.cell(r, 3+i, row.get(i, ''))
        count_start = 14
        for i, label in enumerate(labels):
            ws.cell(r, count_start+i, f'=COUNTIF($D{r}:$M{r},"{label}")')
        result_col = count_start + len(labels)
        count_range = f'{get_column_letter(count_start)}{r}:{get_column_letter(result_col-1)}{r}'
        label_header_range = f'{get_column_letter(count_start)}$1:{get_column_letter(result_col-1)}$1'
        ws.cell(r, result_col, f'=SUBSTITUTE(INDEX({label_header_range},MATCH(MAX({count_range}),{count_range},0)),"Jumlah ","")')
        ws.cell(r, result_col+1, actual.get(id_data, ''))
        ws.cell(r, result_col+2, f'=IF({get_column_letter(result_col)}{r}={get_column_letter(result_col+1)}{r},"Benar","Salah")')
        ws.cell(r, result_col+3, 'Setiap pohon memberi 1 suara. Label dengan jumlah suara paling banyak menjadi hasil Random Forest.')
    style_ws(ws)
    return ws


def add_shap_formula_sheet(wb, obj):
    ws = wb.create_sheet('SHAP Rumus Excel')
    headers = ['ID_Data', 'Siswa', 'Aspek / Mapel', 'Output Prediksi', 'φ0 Base Value', 'Σφi dari detail', 'f(x)=φ0+Σφi Excel', 'Probabilitas Model', 'Selisih', 'Penjelasan']
    for c, h in enumerate(headers, 1): ws.cell(1, c, h)
    detail_ranges = {}
    detail = obj['shap_rows'].reset_index(drop=True)
    for i, row in enumerate(detail.itertuples(index=False), 2):
        detail_ranges.setdefault(int(getattr(row, 'ID_Data')), []).append(i)
    summary = obj['shap_summary']
    for r, (_, row) in enumerate(summary.iterrows(), 2):
        id_data = int(row['ID_Data'])
        ws.cell(r, 1, id_data); ws.cell(r, 2, row['Siswa']); ws.cell(r, 3, row['Aspek / Mapel'])
        ws.cell(r, 4, row['Output Prediksi']); ws.cell(r, 5, row['φ0 Base Value'])
        rows = detail_ranges.get(id_data, [])
        if rows:
            ws.cell(r, 6, f'=SUMIFS(\'SHAP Per Fitur\'!$J:$J,\'SHAP Per Fitur\'!$A:$A,A{r})')
        else:
            ws.cell(r, 6, row['Σφi'])
        ws.cell(r, 7, f'=E{r}+F{r}')
        ws.cell(r, 8, row['Probabilitas Model'])
        ws.cell(r, 9, f'=G{r}-H{r}')
        ws.cell(r, 10, 'Rumus utama SHAP adalah f(x)=φ0+Σφi. φ0 adalah nilai dasar, φi adalah kontribusi fitur.')
    style_ws(ws)
    return ws


def make_xlsx(obj):
    wb=Workbook(); wb.remove(wb.active)
    add_explanation_sheet(wb)
    add_sheet(wb,'DATASET KESELURUHAN',obj['transformed'])
    add_sheet(wb,'Rumus dan Ringkasan',pd.concat([obj['summary'], pd.DataFrame([['','']], columns=obj['summary'].columns)], ignore_index=True))
    add_sheet(wb,'Rumus Detail',obj['formula'])
    add_sheet(wb,'Transformasi Data',obj['transformed'][['ID_Data','Sumber Data','Aspek / Mapel','Set Data','Nilai','Deskripsi Penilaian','Teks Bersih','Label','Y_Prediksi']])
    add_sheet(wb,'TF-IDF Matrix',obj['matrix'])
    add_sheet(wb,'TF-IDF Manual=Python',obj['tfidf_manual'])
    add_tfidf_formula_sheet(wb, obj)
    add_sheet(wb,'Struktur Semua Pohon',obj['tree_structures'])
    add_sheet(wb,'Gini Semua Pohon',obj['gini_all'])
    add_gini_formula_sheet(wb, obj)
    add_sheet(wb,'Jalur Semua Data',obj['tree_paths_all'])
    add_sheet(wb,'Voting Per Pohon',obj['votes'])
    add_voting_formula_sheet(wb, obj)
    add_sheet(wb,'Hasil Voting',obj['final_vote'])
    add_sheet(wb,'Multi Output Long',obj['multi_long'])
    add_sheet(wb,'Multi Output Per Siswa',obj['multi_wide'])
    add_sheet(wb,'Hyperparameter Tuning',obj['hpt'])
    add_sheet(wb,'SHAP Ringkasan',obj['shap_summary'])
    add_sheet(wb,'SHAP Per Fitur',obj['shap_rows'])
    add_shap_formula_sheet(wb, obj)
    # Sheets like the example: pohon 1, pohon 2, ... with dataset + gini + structure + paths.
    data_small = obj['transformed'][['ID_Data','Sumber Data','Aspek / Mapel','Nilai','Teks Bersih','Label','Y_Prediksi']]
    for t in range(1, 11):
        ws=wb.create_sheet(f'pohon {t}')
        r=write_df(ws, data_small, 1, f'DATASET KESELURUHAN - POHON {t}')
        r=write_df(ws, obj['tree_structures'][obj['tree_structures']['Pohon ke-'].eq(t)], r, f'STRUKTUR POHON {t}')
        r=write_df(ws, obj['gini_all'][obj['gini_all']['Pohon ke-'].eq(t)], r, f'PERHITUNGAN GINI / TABEL KONTINGENSI POHON {t}')
        sample_paths=obj['tree_paths_all'][obj['tree_paths_all']['Pohon ke-'].eq(t)]
        r=write_df(ws, sample_paths, r, f'JALUR KEPUTUSAN SELURUH DATA POHON {t}')
        style_ws(ws)
    wb.save(OUT_XLSX)

def esc(t): return escape(str(t)).replace('\n','<w:br/>')
def p(text='', style=None, bold=False):
    st=f'<w:pPr><w:pStyle w:val="{style}"/></w:pPr>' if style else ''
    b='<w:b/>' if bold else ''
    return f'<w:p>{st}<w:r><w:rPr>{b}</w:rPr><w:t xml:space="preserve">{esc(text)}</w:t></w:r></w:p>'
def eq(text):
    return f'<w:p><m:oMathPara><m:oMath><m:r><m:t>{esc(text)}</m:t></m:r></m:oMath></m:oMathPara></w:p>'
def tbl(headers, rows, max_rows=10):
    rows=list(rows)[:max_rows]
    out=['<w:tbl><w:tblPr><w:tblBorders><w:top w:val="single" w:sz="4"/><w:left w:val="single" w:sz="4"/><w:bottom w:val="single" w:sz="4"/><w:right w:val="single" w:sz="4"/><w:insideH w:val="single" w:sz="4"/><w:insideV w:val="single" w:sz="4"/></w:tblBorders></w:tblPr>']
    def cell(v,b=False):
        bd='<w:b/>' if b else ''
        return f'<w:tc><w:p><w:r><w:rPr>{bd}</w:rPr><w:t xml:space="preserve">{esc(v)}</w:t></w:r></w:p></w:tc>'
    out.append('<w:tr>'+''.join(cell(h,True) for h in headers)+'</w:tr>')
    for r in rows: out.append('<w:tr>'+''.join(cell(v) for v in r)+'</w:tr>')
    out.append('</w:tbl>')
    return ''.join(out)

def make_docx(obj):
    # numeric examples from first available rows
    tfrow = obj['tfidf_manual'].iloc[0]
    grow = obj['gini_all'].iloc[0]
    vrow = obj['final_vote'].iloc[0]
    srow = obj['shap_summary'].iloc[0]
    body=[]
    body.append(p('DOKUMEN PERHITUNGAN MANUAL RANDOM FOREST, TF-IDF, MULTI-OUTPUT, DAN SHAP', 'Title', True))
    body.append(p('Dokumen ini dibuat ulang agar rumus TF-IDF manual sama dengan hasil Python sklearn dan agar rumus di Word ditulis menggunakan Equation. Excel pendamping memuat perhitungan seluruh data dan sheet pohon 1 sampai pohon 10 seperti contoh workbook decision tree/random forest.'))
    body.append(p('1. Penjelasan Variabel', 'Heading1', True))
    body.append(p('Output penelitian adalah label perkembangan untuk setiap aspek/mapel siswa, yaitu Baik, Cukup, dan Perlu Bimbingan. Aspek/mapel bukan output prediksi, melainkan konteks/input yang menunjukkan bagian penilaian siswa.'))
    body.append(tbl(['Variabel','Simbol','Peran','Keterangan'], [['Nilai','Nilai','Input','Nilai kuantitatif aspek/mapel.'],['Deskripsi Penilaian','Deskripsi Penilaian','Input','Teks penilaian guru.'],['Aspek/Mapel','A','Konteks/Input','Menentukan aspek yang sedang dinilai.'],['Label','Label','Output','Baik, Cukup, Perlu Bimbingan.']]))
    body.append(p('2. Transformasi Data', 'Heading1', True))
    body.append(p('Transformasi data dilakukan melalui case folding, cleansing, tokenizing, stopword removal, dan pembentukan teks bersih.'))
    body.append(tbl(['ID_Data','Sumber Data','Aspek / Mapel','X1','Teks Bersih','Label'], obj['transformed'][['ID_Data','Sumber Data','Aspek / Mapel','Nilai','Teks Bersih','Label']].values, 5))
    body.append(p('3. Perhitungan TF-IDF Sesuai Python sklearn', 'Heading1', True))
    body.append(p('Perbedaan nilai manual sebelumnya terjadi karena rumus manual memakai TF = n/Nd dan IDF = ln(N/df), sedangkan Python TfidfVectorizer secara default memakai raw count, smooth IDF, dan normalisasi L2. Karena itu rumus manual harus mengikuti sklearn sebagai berikut.'))
    body.append(eq('tf(w,d)=n(w,d)'))
    body.append(eq('idf(w)=ln((1+N)/(1+df(w)))+1'))
    body.append(eq('v(w,d)=tf(w,d)×idf(w)'))
    body.append(eq('||v_d||_2=sqrt(Σ v(w,d)^2)'))
    body.append(eq('tfidf(w,d)=v(w,d)/||v_d||_2'))
    body.append(p('Contoh substitusi angka dari data:'))
    body.append(eq(f"idf({tfrow['Kata']})=ln((1+{int(tfrow['N'])})/(1+{int(tfrow['df(w)'])}))+1={tfrow['idf sklearn = ln((1+N)/(1+df))+1']}"))
    body.append(eq(f"v({tfrow['Kata']},d)={int(tfrow['tf raw (jumlah kata)'])}×{tfrow['idf sklearn = ln((1+N)/(1+df))+1']}={tfrow['tf × idf']}"))
    body.append(eq(f"tfidf({tfrow['Kata']},d)={tfrow['tf × idf']}/{tfrow['L2 norm dokumen']}={tfrow['TF-IDF Manual Setelah L2']}"))
    body.append(p('Nilai tersebut sama dengan kolom TF-IDF Python sklearn pada Excel.'))
    body.append(p('4. Perhitungan Pohon Random Forest', 'Heading1', True))
    body.append(p('Setiap pohon memiliki struktur node, threshold, tabel distribusi kelas, dan perhitungan Gini. Pada Excel disediakan sheet pohon 1 sampai pohon 10 yang berisi dataset, struktur pohon, perhitungan Gini/tabel kontingensi, dan jalur keputusan seluruh data.'))
    body.append(eq('Gini(D)=1-Σp_i^2'))
    body.append(eq('Gini_split=(n_kiri/n)Gini(D_kiri)+(n_kanan/n)Gini(D_kanan)'))
    body.append(eq(f"Gini_split=({int(grow['n Kiri'])}/{int(grow['n Node'])})×{grow['Gini Kiri']}+({int(grow['n Kanan'])}/{int(grow['n Node'])})×{grow['Gini Kanan']}={grow['Gini Split']}"))
    body.append(tbl(list(obj['gini_all'].columns), obj['gini_all'].values, 5))
    body.append(p('5. Perhitungan Voting', 'Heading1', True))
    body.append(eq('ŷ=mode{h_1(x),h_2(x),h_3(x),...,h_T(x)}'))
    body.append(p(f"Contoh data ID {int(vrow['ID_Data'])}: hasil voting adalah {vrow['Hasil Voting']} dengan jumlah suara {int(vrow['Jumlah Suara'])}. Label aktual adalah {vrow['Label']}."))
    body.append(tbl(list(obj['final_vote'].columns), obj['final_vote'].values, 8))
    body.append(p('6. Multi-Output Classification', 'Heading1', True))
    body.append(p('Multi-output classification digunakan untuk menghasilkan label perkembangan pada setiap aspek/mapel siswa. Bentuk output siswa ke-i adalah vektor label.'))
    body.append(eq('Label_i=[label_i1,label_i2,label_i3,...,label_im]'))
    body.append(eq('label_ij ∈ {Baik, Cukup, Perlu Bimbingan}'))
    body.append(tbl(list(obj['multi_long'].columns), obj['multi_long'].values, 8))
    body.append(p('7. Hyperparameter Tuning', 'Heading1', True))
    body.append(eq('Jumlah Kombinasi=|n_estimators|×|max_depth|×|min_samples_split|'))
    body.append(p(f"Parameter terbaik berdasarkan RandomizedSearchCV adalah {obj['grid'].best_params_} dengan skor CV {round(float(obj['grid'].best_score_),9)}."))
    body.append(tbl(list(obj['hpt'].columns), obj['hpt'].values, 8))
    body.append(p('8. Perhitungan SHAP', 'Heading1', True))
    body.append(p('SHAP digunakan untuk menjelaskan kontribusi fitur terhadap output klasifikasi. Rumus umum SHAP adalah:'))
    body.append(eq('f(x)=φ_0+Σφ_i'))
    body.append(eq('φ_i=Σ_{S⊆F\\{i}} (|S|!(M-|S|-1)!/M!) [f(S∪{i})-f(S)]'))
    body.append(p('Pada Excel, perhitungan SHAP manual ditampilkan menggunakan pendekatan ablasi fitur: fitur dihilangkan/diganti baseline, lalu perubahan probabilitas dihitung sebagai kontribusi fitur.'))
    body.append(eq(f"f(x)=φ_0+Σφ_i={srow['φ0 Base Value']}+{srow['Σφi']}={srow['f(x)=φ0+Σφi']}"))
    body.append(tbl(list(obj['shap_summary'].columns), obj['shap_summary'].values, 6))
    body.append(tbl(list(obj['shap_rows'].columns), obj['shap_rows'].values, 8))
    body.append(p('9. Kesimpulan', 'Heading1', True))
    body.append(p('File Excel memuat perhitungan manual seluruh data, sedangkan file Word memuat penjelasan dan rumus menggunakan Equation. Perhitungan TF-IDF manual telah disamakan dengan hasil Python sklearn sehingga nilai manual dan Python tidak berbeda.'))
    tmp=Path(tempfile.mkdtemp())
    try:
        with zipfile.ZipFile(TEMPLATE_DOCX,'r') as zin: zin.extractall(tmp)
        xml=f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:wpc="http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas" xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:wp14="http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing" xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" xmlns:w10="urn:schemas-microsoft-com:office:word" xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml" xmlns:wpg="http://schemas.microsoft.com/office/word/2010/wordprocessingGroup" xmlns:wpi="http://schemas.microsoft.com/office/word/2010/wordprocessingInk" xmlns:wne="http://schemas.microsoft.com/office/word/2006/wordml" xmlns:wps="http://schemas.microsoft.com/office/word/2010/wordprocessingShape" mc:Ignorable="w14 wp14"><w:body>{''.join(body)}<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="720" w:footer="720" w:gutter="0"/></w:sectPr></w:body></w:document>'''
        (tmp/'word'/'document.xml').write_text(xml, encoding='utf-8')
        if OUT_DOCX.exists(): OUT_DOCX.unlink()
        with zipfile.ZipFile(OUT_DOCX,'w',zipfile.ZIP_DEFLATED) as zout:
            for path in tmp.rglob('*'):
                if path.is_file(): zout.write(path, path.relative_to(tmp).as_posix())
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

def main():
    obj=build()
    make_xlsx(obj)
    make_docx(obj)
    print('Created', OUT_XLSX)
    print('Created', OUT_DOCX)
    print('Rows TFIDF manual', len(obj['tfidf_manual']), 'max abs diff', obj['tfidf_manual']['Selisih'].abs().max())

if __name__=='__main__':
    main()
