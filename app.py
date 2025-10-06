import streamlit as st
import pandas as pd
from data.verify_data import clean_dataframe

st.set_page_config(page_title="Soccer Stat", layout="centered")
st.title("Soccer Stat")

file = st.file_uploader("Choisir un fichier CSV", type=["csv"])

if file:
    try:
        df = pd.read_csv(file)
        cleaned = clean_dataframe(df)
    except Exception as e:
        st.error(f"Erreur : {e}")
    else:
        st.success("Nettoyage terminé.")
        st.download_button(
            "Télécharger le CSV nettoyé",
            cleaned.to_csv(index=False).encode("utf-8"),
            "cleaned.csv",
            "text/csv",
        )
else:
    st.info("Importez un fichier CSV pour commencer.")