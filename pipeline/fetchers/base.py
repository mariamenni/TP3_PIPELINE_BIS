"""Classe de base pour les fetchers d'API GEO."""
import time
from abc import ABC, abstractmethod
from typing import Generator

import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)
import logging

from ..config import APIConfig

logger = logging.getLogger(__name__)


class BaseFetcher(ABC):
    """Classe abstraite pour les fetchers d'API REST."""

    def __init__(self, config: APIConfig):
        # Configuration de l'API (URL, timeout, rate limit)
        self.config = config
        # Statistiques d'utilisation
        self.stats = {
            "requests_made": 0,
            "requests_failed": 0,
            "items_fetched": 0,
            "start_time": None,
            "end_time": None,
        }

    # ==========================================================
    #  Requête HTTP avec retry automatique
    # ==========================================================

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=20),
        retry=retry_if_exception_type(
            (httpx.HTTPError, httpx.TimeoutException)
        ),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    def _make_request(self, endpoint: str, params: dict | None = None) -> dict | None:
        """
        Effectue une requête HTTP GET avec retry.
        Retourne le JSON ou None si 404.
        """
        url = f"{self.config.base_url}{endpoint}"

        try:
            with httpx.Client(
                timeout=self.config.timeout,
                headers=self.config.headers
            ) as client:
                response = client.get(url, params=params)

              
                self.stats["requests_made"] += 1

                try:
                    response.raise_for_status()
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 404:
                        
                        return None
                    
                    raise

                return response.json()

        except Exception:
            self.stats["requests_failed"] += 1
            raise

    # ==========================================================
    # Rate limiting
    # ==========================================================

    def _rate_limit(self):
        """Respecte le délai entre chaque requête pour éviter le blocage."""
        time.sleep(self.config.rate_limit)

    # ==========================================================
    # Méthodes à implémenter
    # ==========================================================

    @abstractmethod
    def fetch_one(self, **kwargs) -> dict | None:
        """Récupère une ressource unique (adresse ou commune)."""
        pass

    def fetch_batch(self, items: list, **kwargs) -> list[dict]:
        """Récupère un lot d'éléments (adresses)."""
        results = []

        for item in items:
            self._rate_limit()
            data = self.fetch_one(item=item, **kwargs)
            if data:
                results.append(data)
                self.stats["items_fetched"] += 1

        return results

    def fetch_all(self, items: list, **kwargs) -> Generator[dict, None, None]:
        """Itère sur tous les éléments fournis."""
        for item in items:
            self._rate_limit()
            data = self.fetch_one(item=item, **kwargs)
            if data:
                self.stats["items_fetched"] += 1
                yield data

    # ==========================================================
    # Statistiques
    # ==========================================================

    def get_stats(self) -> dict:
        return self.stats.copy()
