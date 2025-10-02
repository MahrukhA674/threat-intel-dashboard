"""IP reputation endpoints.

This router exposes a single endpoint to check the reputation of an IP
address using AbuseIPDB or another configured service. Results are
cached for 1 hour. Rate limiting is applied to prevent abuse.
"""

from fastapi import APIRouter, Depends

from ...external_clients import fetch_ip_reputation

router = APIRouter(prefix="/ip", tags=["ip"])


@router.get("/check/{ip_address}")
async def check_ip(ip_address: str) -> dict:
    data = await fetch_ip_reputation(ip_address)
    return {"data": data}