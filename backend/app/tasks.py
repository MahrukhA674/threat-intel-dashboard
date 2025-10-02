"""Background tasks for threat monitoring.

This module defines periodic tasks that query external threat
intelligence sources and publish new alerts to Redis. The tasks can be
scheduled using FastAPI's ``add_event_handler`` on startup.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Any

from .external_clients import fetch_cve_search
from .db.redis_client import redis_client
from app.services.feed_service import FeedService 


async def monitor_new_threats() -> None:
    """Poll external APIs for new threats and publish alerts."""
    # This simple implementation polls every hour for the latest CVEs and OTX pulses.
    last_run = datetime.utcnow() - timedelta(hours=1)
    while True:
        now = datetime.utcnow()
        start_date = last_run.strftime("%Y-%m-%d")
        end_date = now.strftime("%Y-%m-%d")
        # Fetch recent CVEs
        try:
            cve_data = await fetch_cve_search(keyword="*", start_date=start_date, end_date=end_date, limit=5)
            for item in cve_data.get("vulnerabilities", []):
                cve = item.get("cve") or item
                alert = {
                    "id": cve.get("id"),
                    "timestamp": now.isoformat(),
                    "category": "CVE",
                    "summary": cve.get("descriptions", [{}])[0].get("value", "") if isinstance(cve.get("descriptions"), list) else cve.get("description", ""),
                    "data": cve,
                }
                await redis_client.publish("threat_alerts", alert)
        except Exception:
            pass  # ignore errors
     
        last_run = now
        await asyncio.sleep(3600)


async def ingest_feeds() -> None:
    """Ingest data from various threat feeds periodically."""
    while True:
        # Placeholder for feed ingestion logic
        # e.g., await feed_service.ingest_feeds()
        feed_service = FeedService()
        feed_service.ingest_feeds()
        await asyncio.sleep(3600)
      