"""Fetcher pour l'API Adresse (Base Adresse Nationale)."""

from typing import Generator
from tqdm import tqdm

from .base import BaseFetcher
from ..config import ADRESSE_CONFIG
from ..models import GeocodingResult


class AdresseFetcher(BaseFetcher):
    """Fetcher pour le géocodage des adresses via l'API Adresse."""

    def __init__(self):
        super().__init__(ADRESSE_CONFIG)

    # ==========================================================
    # Adresse unique
    # ==========================================================

    def fetch_one(self, item: str) -> GeocodingResult:
        """
        Récupère le géocodage d'une seule adresse.
        Retourne un objet GeocodingResult.
        """
        if not item or not item.strip():
            return GeocodingResult(query=item or "", score=0)

        # Requête API    
        data = self._make_request(
            endpoint="/search/",
            params={"q": item, "limit": 1}
        )

        if not data.get("features"):
            # Aucun résultat trouvé
            return GeocodingResult(query=item, score=0)

        f = data["features"][0]
        props = f.get("properties", {})
        lon, lat = f.get("geometry", {}).get("coordinates", [None, None])
        # Mise à jour des statistiques
        self.stats["items_fetched"] += 1

        # Retourne l'objet GeocodingResult
        return GeocodingResult(
            query=item,
            label=props.get("label"),
            latitude=lat,
            longitude=lon,
            score=props.get("score", 0),
            postcode=props.get("postcode"),
            city=props.get("city"),
            citycode=props.get("citycode"),
        )

    # ==========================================================
    #  Lot d'adresses
    # ==========================================================

    def fetch_batch(self, addresses: list[str]) -> list[GeocodingResult]:
        """Récupère un lot d'adresses en respectant le rate limit."""
        results = []

        for addr in addresses:
            self._rate_limit()
            result = self.fetch_one(addr)
            results.append(result)

        return results

    # ==========================================================
    # Toutes les adresses
    # ==========================================================

    def fetch_all(
        
        self,
        addresses: list[str],
        verbose: bool = True
    ) -> Generator[GeocodingResult, None, None]:

        from datetime import datetime

        self.stats["start_time"] = datetime.now()
        iterator = tqdm(addresses, desc="Géocodage", disable=not verbose)

        for addr in iterator:
            self._rate_limit()
            yield self.fetch_one(addr)

        self.stats["end_time"] = datetime.now()
