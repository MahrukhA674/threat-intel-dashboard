
import asyncio
import os
from datetime import datetime
from typing import Any, Dict, Optional

import httpx
from fastapi import HTTPException, status

from app.core.config import settings

from .db.redis_client import redis_client




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


async def fetch_cve_search(keyword: str, severity: Optional[str] = None, start_date: Optional[str] = None,
                           end_date: Optional[str] = None, cvss_min: Optional[float] = None,
                           cvss_max: Optional[float] = None, start: int = 0, limit: int = 20) -> Any:
    """Search CVEs via the NVD API and cache results."""
    cache_key = f"cve_search:{keyword}:{severity}:{start_date}:{end_date}:{cvss_min}:{cvss_max}:{start}:{limit}"
    cached = await  redis_client.get_cached(cache_key)
    if cached:
        return cached

    base_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    params: Dict[str, Any] = {
        "keywordSearch": keyword,
        "startIndex": start,
        "resultsPerPage": limit,
    }
    # NVD requires date range queries to include both start and end dates and to be <=120 days【294896989524977†L500-L508】.
    if start_date and end_date:
        params["pubStartDate"] = f"{start_date}T00:00:00.000Z"
        params["pubEndDate"] = f"{end_date}T23:59:59.999Z"
    if severity:
        params["cvssV3Severity"] = severity
    if cvss_min is not None:
        params["cvssV3Metrics"] = f"{cvss_min}-{cvss_max if cvss_max is not None else ''}"
    if settings.nvd_api_key:
        params["apiKey"] = settings.nvd_api_key

    data = await _http_get(base_url, params=params)
    await  redis_client.set_cached(cache_key, data, ttl=3600)
    return data


async def fetch_cve_details(cve_id: str) -> Any:
    """Fetch a single CVE's details from the NVD API."""
    cache_key = f"cve_details:{cve_id}"
    cached = await get_cached(cache_key)
    if cached:
        return cached
    url = f"https://services.nvd.nist.gov/rest/json/cves/2.0?cveId={cve_id}"
    if settings.nvd_api_key:
        url += f"&apiKey={settings.nvd_api_key}"
    data = await _http_get(url)
    await  redis_client.set_cached(cache_key, data, ttl=3600)
    return data


async def fetch_ip_reputation(ip_address: str) -> Any:
    """Query IP reputation from AbuseIPDB (or similar provider)."""
    cache_key = f"ip_rep:{ip_address}"
    cached = await  redis_client.get_cached(cache_key)
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
    await  redis_client.set_cached(cache_key, data, ttl=3600)
    return data