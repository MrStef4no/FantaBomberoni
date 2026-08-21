import pandas as pd

file = "../data/Rose_bomberoni 2025-26.xlsx"

df = pd.read_excel(file)

print(df.head(30))
print()
print("COLONNE:")
print(df.columns.tolist())