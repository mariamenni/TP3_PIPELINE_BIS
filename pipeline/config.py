"""Configuration centralisée du pipeline GEO."""

from pathlib import Path
from dataclasses import dataclass

# ==========================================================
#  Chemins du projet
# ==========================================================

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"

RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
REPORTS_DIR = DATA_DIR / "reports"

for dir_path in [RAW_DIR, PROCESSED_DIR, REPORTS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)


# ==========================================================
#  Configuration générique d'une API
# ==========================================================

@dataclass
class APIConfig:
    """Configuration d'une API REST."""
    name: str
    base_url: str
    timeout: int
    rate_limit: float  # secondes entre requêtes
    headers: dict | None = None

    def __post_init__(self):
        self.headers = self.headers or {}


# ==========================================================
#  APIs utilisées dans le TP
# ==========================================================

# API Adresse — Base Adresse Nationale (géocodage)
ADRESSE_CONFIG = APIConfig(
    name="API Adresse (BAN)",
    base_url="https://api-adresse.data.gouv.fr",
    timeout=10,
    rate_limit=0.1
)

# API geo.api.gouv.fr — données communes
COMMUNE_CONFIG = APIConfig(
    name="Geo API Gouv - Communes",
    base_url="https://geo.api.gouv.fr",
    timeout=10,
    rate_limit=0.1
)

# API Hub'Eau — Qualité de l'eau potable
EAU_CONFIG = APIConfig(
    name="HubEau - Qualité Eau Potable",
    base_url="https://hubeau.eaufrance.fr/api/v1",
    timeout=15,
    rate_limit=0.2
)

# ==========================================================
#  Paramètres d'acquisition
# ==========================================================

MAX_ITEMS = 200          # Nombre max d'adresses 
BATCH_SIZE = 20          # Taille des lots si besoin


# ==========================================================
#  Seuils de qualité
# ==========================================================

QUALITY_THRESHOLDS = {
    "completeness_min": 0.7,        # 70% champs non nuls
    "geocoding_score_min": 0.5,     # score BAN minimal acceptable
    "duplicates_max_pct": 5.0,      # max 5% doublons
}
