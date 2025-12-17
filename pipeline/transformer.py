"""Module de transformation et nettoyage pour le pipeline GEO."""
import pandas as pd
import numpy as np
from typing import Callable
from litellm import completion
from dotenv import load_dotenv

load_dotenv()


class DataTransformer:
    """Transforme et nettoie les données GEO."""

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.transformations_applied = []

    def remove_duplicates(self, subset: list[str] = None) -> 'DataTransformer':
        """Supprime les doublons."""
        initial = len(self.df)

        if subset is None:
            subset = ['address'] if 'address' in self.df.columns else [self.df.columns[0]]

        self.df = self.df.drop_duplicates(subset=subset, keep='first')
        removed = initial - len(self.df)
        self.transformations_applied.append(f"Doublons supprimés: {removed}")
        return self

    def handle_missing_values(
        
        self,
        numeric_strategy: str = 'median',
        text_strategy: str = 'unknown'
    ) -> 'DataTransformer':
        

        # Colonnes numériques
        num_cols = self.df.select_dtypes(include=[np.number]).columns
        for col in num_cols:
            if numeric_strategy == 'median':
                fill_value = self.df[col].median()
            elif numeric_strategy == 'mean':
                fill_value = self.df[col].mean()
            elif numeric_strategy == 'zero':
                fill_value = 0
            else:
                fill_value = None

            if fill_value is not None:
                null_count = self.df[col].isnull().sum()
                if null_count > 0:
                    self.df[col] = self.df[col].fillna(fill_value)
                    self.transformations_applied.append(f"{col}: {null_count} nulls → {fill_value:.2f}")

        # Colonnes texte
        text_cols = self.df.select_dtypes(include=['object']).columns
        for col in text_cols:
            null_count = self.df[col].isnull().sum()
            if null_count > 0:
                self.df[col] = self.df[col].fillna(text_strategy)
                self.transformations_applied.append(f"{col}: {null_count} nulls → '{text_strategy}'")

        return self

    def normalize_text_columns(self, columns: list[str] = None) -> 'DataTransformer':
        """Normalise les colonnes texte (strip, lower)."""
        if columns is None:
            columns = self.df.select_dtypes(include=['object']).columns.tolist()

        for col in columns:
            if col in self.df.columns:
                self.df[col] = self.df[col].astype(str).str.strip().str.lower()

        self.transformations_applied.append(f"Normalisation texte: {columns}")
        return self

    def add_derived_columns(self) -> 'DataTransformer':
        """Ajoute des colonnes dérivées GEO."""

        # Flag géocodé
        if 'score' in self.df.columns:
            self.df['is_geocoded'] = self.df['score'] >= 0.5
            self.transformations_applied.append("Ajout: is_geocoded")

        # Flag population non nulle
        if 'population' in self.df.columns:
            self.df['has_population'] = self.df['population'] > 0
            self.transformations_applied.append("Ajout: has_population")

        return self

    def generate_ai_transformations(self) -> str:
        """Demande à l'IA des transformations supplémentaires."""
        context = f"""
        Dataset GEO avec {len(self.df)} lignes.
        Colonnes: {list(self.df.columns)}
        Types: {self.df.dtypes.to_dict()}
        Transformations déjà appliquées: {self.transformations_applied}
        """
        response = completion(
            model="ollama/llama3.2",
            messages=[
                {
                    "role": "system",
                    "content": "Tu es un expert en data engineering. Génère du code Python pandas exécutable."
                },
                {
                    "role": "user",
                    "content": f"{context}\n\nQuelles transformations supplémentaires recommandes-tu ? Génère le code."
                }
            ],
            api_base="http://localhost:11434"
        )
        return response
    def apply_custom(self, func: Callable[[pd.DataFrame], pd.DataFrame], name: str) -> 'DataTransformer':
        """Applique une transformation personnalisée."""
        self.df = func(self.df)
        self.transformations_applied.append(f"Custom: {name}")
        return self

    def get_result(self) -> pd.DataFrame:
        """Retourne le DataFrame transformé."""
        return self.df

    def get_summary(self) -> str:
        """Retourne un résumé des transformations."""
        return "\n".join([f"• {t}" for t in self.transformations_applied])
