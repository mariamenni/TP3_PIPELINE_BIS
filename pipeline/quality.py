"""Module d'analyse et scoring de la qualité des données GEO."""

import pandas as pd
from datetime import datetime
from pathlib import Path

from .config import QUALITY_THRESHOLDS, REPORTS_DIR
from .models import QualityMetrics


class QualityAnalyzer:
    """Analyse la qualité d'un dataset GEO."""

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.metrics: QualityMetrics | None = None

    # ==========================================================
    # Métriques
    # ==========================================================

    def calculate_completeness(self) -> float:
        """Calcule le pourcentage de cellules non-null."""
        total_cells = self.df.size
        non_null = self.df.notna().sum().sum()
        return non_null / total_cells if total_cells else 0

    def count_duplicates(self) -> tuple[int, float]:
        """Compte les doublons par adresse."""
        if "address" not in self.df.columns:
            return 0, 0.0

        duplicates = self.df.duplicated(subset=["address"]).sum()
        pct = duplicates / len(self.df) * 100 if len(self.df) else 0
        return duplicates, pct

    def calculate_geocoding_stats(self) -> tuple[float, float]:
        """Calcule le taux de géocodage et score moyen."""
        if "score" not in self.df.columns:
            return 0.0, 0.0

        valid = self.df["score"] >= QUALITY_THRESHOLDS["geocoding_score_min"]
        success_rate = valid.sum() / len(self.df) * 100 if len(self.df) else 0
        avg_score = self.df.loc[valid, "score"].mean() if valid.any() else 0

        return success_rate, avg_score

    def calculate_null_counts(self) -> dict:
        """Compte les valeurs nulles par colonne."""
        return self.df.isnull().sum().to_dict()

    # ==========================================================
    # Scoring
    # ==========================================================

    def determine_grade(self, completeness, duplicates_pct, geo_rate) -> str:
        """Détermine la note finale selon les seuils définis."""
        score = 0

        score += min(completeness * 40, 40)

        if duplicates_pct <= 1:
            score += 30
        elif duplicates_pct <= 5:
            score += 20
        elif duplicates_pct <= 10:
            score += 10

        score += min(geo_rate / 100 * 30, 30)

        if score >= 90:
            return "A"
        elif score >= 75:
            return "B"
        elif score >= 60:
            return "C"
        elif score >= 40:
            return "D"
        else:
            return "F"

    # ==========================================================
    # Analyse complète
    # ==========================================================

    def analyze(self) -> QualityMetrics:
        """Analyse et retourne un objet QualityMetrics."""
        completeness = self.calculate_completeness()
        duplicates, duplicates_pct = self.count_duplicates()
        geo_rate, geo_avg = self.calculate_geocoding_stats()
        null_counts = self.calculate_null_counts()

        grade = self.determine_grade(completeness, duplicates_pct, geo_rate)

        self.metrics = QualityMetrics(
            total_records=len(self.df),
            valid_records=len(self.df) - duplicates,
            completeness_score=round(completeness, 3),
            duplicates_count=duplicates,
            duplicates_pct=round(duplicates_pct, 2),
            geocoding_success_rate=round(geo_rate, 2),
            avg_geocoding_score=round(geo_avg, 3),
            null_counts=null_counts,
            quality_grade=grade,
        )

        return self.metrics

    # ==========================================================
    # Rapport Markdown
    # ==========================================================

    def generate_report(self, name: str = "geo_quality_report") -> Path:
        """Génère un rapport Markdown de qualité."""
        if not self.metrics:
            self.analyze()

        report = f"""# Rapport de Qualité des Données GEO

**Date** : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Résumé
- Total lignes : {self.metrics.total_records}
- Complétude : {self.metrics.completeness_score * 100:.1f}%
- Doublons : {self.metrics.duplicates_pct:.1f}%
- Succès géocodage : {self.metrics.geocoding_success_rate:.1f}%
- Note globale : **{self.metrics.quality_grade}**

## Valeurs nulles
"""

        for col, cnt in self.metrics.null_counts.items():
            report += f"- {col}: {cnt}\n"

        path = REPORTS_DIR / f"{name}_{datetime.now():%Y%m%d_%H%M%S}.md"
        path.write_text(report, encoding="utf-8")

        return path
