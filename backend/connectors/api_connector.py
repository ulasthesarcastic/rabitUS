"""REST API connector — reads from and writes to REST APIs."""

from typing import Any

import httpx

from backend.models.connection import Connection


class APIConnector:
    def __init__(self, connection: Connection):
        self.base_url = (connection.base_url or "").rstrip("/")
        self.auth_type = connection.auth_type or "none"
        self.auth_config = connection.auth_config or {}
        self.extra_headers = connection.headers or {}

    def _build_headers(self) -> dict[str, str]:
        headers = dict(self.extra_headers)
        if self.auth_type == "bearer":
            headers["Authorization"] = f"Bearer {self.auth_config.get('token', '')}"
        elif self.auth_type == "api_key":
            key_name = self.auth_config.get("header_name", "X-API-Key")
            headers[key_name] = self.auth_config.get("key", "")
        return headers

    def _build_auth(self) -> httpx.BasicAuth | None:
        if self.auth_type == "basic":
            return httpx.BasicAuth(
                username=self.auth_config.get("username", ""),
                password=self.auth_config.get("password", ""),
            )
        return None

    async def fetch(self, path: str, params: dict | None = None) -> list[dict[str, Any]]:
        """GET data from source API. Returns list of records."""
        url = f"{self.base_url}/{path.lstrip('/')}"
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(url, headers=self._build_headers(), auth=self._build_auth(), params=params)
            resp.raise_for_status()
            data = resp.json()
            # Normalize: if response is a single object, wrap in list
            if isinstance(data, dict):
                # Check common pagination wrappers
                for key in ("results", "data", "items", "records", "content"):
                    if key in data and isinstance(data[key], list):
                        return data[key]
                return [data]
            return data

    async def push(self, path: str, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """POST records to target API. Returns responses."""
        url = f"{self.base_url}/{path.lstrip('/')}"
        results = []
        async with httpx.AsyncClient(timeout=30) as client:
            for record in records:
                resp = await client.post(url, headers=self._build_headers(), auth=self._build_auth(), json=record)
                resp.raise_for_status()
                results.append(resp.json())
        return results
