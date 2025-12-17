"""Modèles de données avec validation pour le pipeline GEO."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ==========================================================
# Résultat brut de géocodage (API Adresse)
# ==========================================================

class GeocodingResult(BaseModel):
    """Résultat du géocodage via l'API Adresse (BAN)."""
    
    query: str                           # adresse d'entrée
    label: Optional[str] = None          # adresse normalisée
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    score: float = 0.0
    city: Optional[str] = None
    postcode: Optional[str] = None
    citycode: Optional[str] = None       # code INSEE
    fetched_at: datetime = Field(default_factory=datetime.now)

    @property
    def is_valid(self) -> bool:
        """Vérifie si le résultat est valide pour l'analyse."""
        return (
            self.score >= 0.5
            and self.latitude is not None
            and self.longitude is not None
            and self.citycode is not None
        )


# ==========================================================
# Données commune (geo.api.gouv.fr)
# ==========================================================

class CommuneInfo(BaseModel):
    """Informations administratives d'une commune."""
    
    citycode: str
    nom: str
    population: int
    code_departement: str
    code_region: str


# ==========================================================
#  Donnée enrichie finale (fusion des APIs)
# ==========================================================

class EnrichedAddress(BaseModel):
    """Adresse géocodée et enrichie."""
    
    address: str                         
    latitude: float
    longitude: float
    score: float
    city: str
    postcode: str
    citycode: str
    commune: str
    population: int
    fetched_at: datetime = Field(default_factory=datetime.now)


# ==========================================================
#  Métriques de qualité du dataset
# ==========================================================

class QualityMetrics(BaseModel):
    """Métriques de qualité des données produites."""
    
    total_records: int
    valid_records: int
    completeness_score: float
    duplicates_count: int
    duplicates_pct: float
    geocoding_success_rate: float
    avg_geocoding_score: float
    null_counts: dict
    quality_grade: str  # A, B, C, D, F

    @property
    def is_acceptable(self) -> bool:
        """Vérifie si la note est acceptable (A, B, C)."""
        return self.quality_grade in {"A", "B", "C"}


class WaterQualityResult(BaseModel):
    """Résultat d'analyse de la qualité de l'eau potable."""

    code_commune: str
    nom_commune: str
    code_parametre: str
    libelle_parametre: str
    resultat_numerique: float | None = None
    libelle_unite: str | None = None
    date_prelevement: datetime
    conclusion_conformite_prelevement: str

    conformite_limites_pc_prelevement: str | None = None
    conformite_references_pc_prelevement: str | None = None