import pandas as pd
import numpy as np

INPUT = "top5-players.csv"
OUTPUT = "top5-players-cleaned.csv"

df = pd.read_csv(INPUT)

# ------------------| Doublons |------------------

dup_exact = df.duplicated().sum()
print("Doublons exacts :", dup_exact)

df = df.drop_duplicates().reset_index(drop=True)

for col in ["Min", "MP"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")
if all(c in df.columns for c in ["Player", "Min", "MP"]):
    df = (
        df.sort_values(["Player", "Min", "MP"], ascending=[True, False, False])
          .drop_duplicates(subset=["Player"], keep="first")
          .reset_index(drop=True)
    )
    print("Après déduplication par joueur :", df.shape)

# ------------------| Valeurs manquantes |------------------

for c in df.select_dtypes(include=["object"]).columns:
    df[c] = df[c].replace({"": np.nan, "-": np.nan}).astype(object)

empty_cols = df.columns[df.isna().all()].tolist()
if empty_cols:
    print("Colonnes entièrement vides supprimées :", empty_cols)
    df = df.drop(columns=empty_cols)

for c in ["Gls", "Ast", "MP", "Min"]:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")
        df[c] = df[c].fillna(0)

# ------------------| Valeurs aberrantes |------------------

num_cols = df.select_dtypes(include=["number"]).columns
for c in num_cols:
    q1 = df[c].quantile(0.25)
    q3 = df[c].quantile(0.75)
    iqr = q3 - q1
    if pd.notna(iqr) and iqr != 0:
        lower, upper = q1 - 1.5*iqr, q3 + 1.5*iqr
        outliers = ((df[c] < lower) | (df[c] > upper)).sum()
        if outliers:
            print(f"Outliers possibles pour {c} :", int(outliers))

for c in ["Gls", "Ast", "MP", "Min"]:
    if c in df.columns:
        df[c] = df[c].clip(lower=0)

if "Age" in df.columns:
    df["Age"] = pd.to_numeric(df["Age"], errors="coerce")
    df.loc[(df["Age"] < 15) | (df["Age"] > 50), "Age"] = np.nan

# ------------------| Sauvegarde |------------------

df.to_csv(OUTPUT, index=False)
print("Fichier nettoyé :", OUTPUT)