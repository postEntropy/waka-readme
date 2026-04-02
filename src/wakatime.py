"""
WakaTime API client.
"""
from __future__ import annotations

import base64
import httpx
from src import config as C


class WakaTimeClient:
    def __init__(self) -> None:
        key_b64 = base64.b64encode(C.WAKATIME_API_KEY.encode()).decode()
        self._headers = {"Authorization": f"Basic {key_b64}"}
        self._base = C.WAKATIME_API_URL.rstrip("/")

    async def _get(self, path: str) -> dict | None:
        url = f"{self._base}/{path.lstrip('/')}"
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                resp = await client.get(url, headers=self._headers)
                resp.raise_for_status()
                return resp.json()
            except Exception as exc:
                print(f"[WakaTime] request failed for {url}: {exc}")
                return None

    async def get_stats_last_7_days(self) -> dict | None:
        """Returns WakaTime stats for the last 7 days."""
        data = await self._get("users/current/stats/last_7_days")
        if data and "data" in data:
            return data["data"]
        return None

    async def get_all_time(self) -> dict | None:
        """Returns all-time WakaTime summary."""
        data = await self._get("users/current/all_time_since_today")
        if data and "data" in data:
            return data["data"]
        return None
