from ast import Dict
from typing import Optional
from fastapi import HTTPException
import httpx
from app.core.config import settings
from ..models.models import CVE, IPThreat, OTXThreat, ThreatIntel
from ..db.redis_client import redis_client
from .cache_service import CacheService
import asyncio
import os
from datetime import datetime
from typing import Any, Dict, Optional


async def _http_get(url: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None) -> Any:
    """Internal helper for making HTTP GET requests with httpx."""
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            response = await client.get(url, headers=headers, params=params)
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()


async def fetch_ip_reputation(ip_address: str) -> Any:
    """Query IP reputation from AbuseIPDB (or similar provider)."""
    cache_key = f"ip_rep:{ip_address}"
    cached = await redis_client.get_cache(cache_key)
    if cached:
        return cached
    base_url = "https://api.abuseipdb.com/api/v2/check"
    params = {
        "ipAddress": ip_address,
        "maxAgeInDays": 90,
        "verbose": True,
    }
    headers = {
        "Key": settings.abuseipdb_api_key,
        "Accept": "application/json",
    } if settings.abuseipdb_api_key else {}
    data = await _http_get(base_url, headers=headers, params=params)
    await redis_client.set_cached(cache_key, data, ttl=3600)
    return data