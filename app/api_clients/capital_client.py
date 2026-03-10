from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import settings

LOGGER = logging.getLogger(__name__)


class CapitalComClient:
    """Capital.com REST client with session authentication."""

    def __init__(self) -> None:
        self._client = httpx.Client(base_url=settings.capital_base_url, timeout=30)
        self._authenticated = False

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
    def authenticate(self) -> None:
        payload = {
            "identifier": settings.capital_identifier,
            "password": settings.capital_password,
        }
        headers = {"X-CAP-API-KEY": settings.capital_api_key}
        response = self._client.post("/session", json=payload, headers=headers)
        response.raise_for_status()
        cst = response.headers.get("CST")
        security = response.headers.get("X-SECURITY-TOKEN")
        if not cst or not security:
            raise RuntimeError("Authentication did not return session tokens")
        self._client.headers.update({"CST": cst, "X-SECURITY-TOKEN": security, "X-CAP-API-KEY": settings.capital_api_key})
        self._authenticated = True
        LOGGER.info("Authenticated with Capital.com")

    def _ensure_auth(self) -> None:
        if not self._authenticated:
            self.authenticate()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
    def fetch_candles(self, epic: str, resolution: str, max_points: int = 500, to: datetime | None = None) -> dict[str, Any]:
        self._ensure_auth()
        params: dict[str, Any] = {"resolution": resolution, "max": max_points}
        if to:
            params["to"] = to.isoformat()
        resp = self._client.get(f"/prices/{epic}", params=params)
        resp.raise_for_status()
        return resp.json()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
    def fetch_client_sentiment(self, market_ids: list[str]) -> dict[str, Any]:
        self._ensure_auth()
        resp = self._client.get("/clientsentiment", params={"marketIds": ",".join(market_ids)})
        resp.raise_for_status()
        return resp.json()

    def close(self) -> None:
        self._client.close()
