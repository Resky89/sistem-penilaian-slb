import pandas as pd

file_path = "../DATA MENTAH.xlsx"
xl = pd.ExcelFile(file_path)
for sheet in xl.sheet_names:
    df = pd.read_excel(xl, sheet_name=sheet)
    print(f"Sheet: {sheet}")
    print(f"Columns: {df.columns.tolist()}")
    print("-" * 20)
    break # Just peek at the first sheet
