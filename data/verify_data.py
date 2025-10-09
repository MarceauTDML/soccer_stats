import pandas as pd
import numpy as np

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
# ------------------| Colonnes numériques à forcer |------------------
    numeric_cols = [
        'MP','Starts','Min','90s','Gls','Ast','G+A','G-PK','PK','PKatt','CrdY','CrdR',
        'xG','npxG','xAG','npxG+xAG','PrgC','PrgP','PrgR','Gls_90','Ast_90','G+A_90',
        'G-PK_90','G+A-PK_90','xG_90','xAG_90','xG+xAG_90','npxG_90','npxG+xAG_90','Age'
    ]

    for col in [c for c in numeric_cols if c in df.columns]:
        df[col] = pd.to_numeric(
            df[col].astype(str).str.extract(r"(\d+\.?\d*)")[0],
            errors="coerce"
        )

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
    record_limits = {
        "Age": 40,
        "Gls": 73,
        "Ast": 21,
        "G+A": 80,
        "CrdY": 17,
        "xG": 34,
    }

    for col, vmax in record_limits.items():
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            nb_out = (df[col] > vmax).sum()
            if nb_out:
                print(f"Outliers (>{vmax}) pour {col} :", int(nb_out))
            df[col] = df[col].clip(upper=vmax)

# ------------------| Corrections évidentes |------------------
    for c in ["Gls", "Ast", "MP", "Min"]:
        if c in df.columns:
            df[c] = df[c].clip(lower=0)

    if "Age" in df.columns:
        df.loc[(df["Age"] < 15) | (df["Age"] > 50), "Age"] = np.nan

    return df

# ----------------------| Sauvegarde |------------------
def clean_csv(input_path: str, output_path: str) -> None:
    df = pd.read_csv(input_path)
    df = clean_dataframe(df)
    df.to_csv(output_path, index=False)
    print("Fichier nettoyé :", output_path)