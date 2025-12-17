"""
Module de chargement et préparation des données GEO.
Consomme les Parquet produits par le pipeline TP2.
"""

from pathlib import Path
import duckdb
import pandas as pd

# ==========================================================
# Chargement des Parquet d'un dossier
# ==========================================================
def load_all_parquets(folder: str | Path) -> pd.DataFrame:
    folder = Path(folder)

    if not folder.exists():
        raise FileNotFoundError(f"Dossier introuvable : {folder}")

    parquet_files = list(folder.glob("*.parquet"))
    if not parquet_files:
        raise FileNotFoundError(f"Aucun fichier Parquet dans : {folder}")

    con = duckdb.connect()
    df = con.execute(
        f"SELECT * FROM read_parquet('{folder.as_posix()}/*.parquet')"
    ).df()
    con.close()

    return df
# ==========================================================
# Chargement Parquet 
# ==========================================================
def load_data(filepath: str | Path) -> pd.DataFrame:
    
    filepath = Path(filepath)

    if not filepath.exists():
        raise FileNotFoundError(f"Parquet introuvable : {filepath}")

    con = duckdb.connect()
    df = con.execute(
        f"SELECT * FROM read_parquet('{filepath.as_posix()}')"
    ).df()
    con.close()

    return df


# ==========================================================
# Résumé dataset (pour chatbot / debug)
# ==========================================================
def get_data_summary(df: pd.DataFrame) -> dict:
    """
    Résumé léger du DataFrame.
    Utilisé pour le contexte du chatbot.
    """
    return {
        "rows": len(df),
        "columns": list(df.columns),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "sample": df.head(5).to_dict(),
    }


# ==========================================================
# Filtres simples (UI / chatbot)
# ==========================================================
def filter_data(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """
    Applique des filtres simples au DataFrame.

    Exemple:
    filters = {
        "city": ["paris", "lyon"],
        "population_bucket": "grande"
    }
    """
    df_filtered = df.copy()

    for col, value in filters.items():
        if col not in df_filtered.columns:
            continue

        if isinstance(value, list):
            df_filtered = df_filtered[df_filtered[col].isin(value)]
        else:
            df_filtered = df_filtered[df_filtered[col] == value]

    return df_filtered
