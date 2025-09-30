from typing import Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..db.redis_client import redis_client
from ..models.models import CVE, IPThreat, OTXThreat, ThreatIntel

class CacheService:
    def __init__(self, db: Session):
        self.db = db

    async def refresh_cache(self) -> None:
        """Refresh all cached data."""
        await self._cache_dashboard_stats()
        await self._cache_recent_threats()
        await self._cache_severity_stats()
        await self._cache_threat_type_stats()

    async def _cache_dashboard_stats(self) -> None:
        """Cache dashboard statistics."""
        stats = {
            "total_cves": self.db.query(CVE).count(),
            "total_ip_threats": self.db.query(IPThreat).count(),
            "total_otx_threats": self.db.query(OTXThreat).count(),
            "last_updated": datetime.utcnow().isoformat()
        }
        await redis_client.set_cache("dashboard_stats", stats, expire=3600)

    async def _cache_recent_threats(self) -> None:
        """Cache recent threats."""
        recent_threats = (
            self.db.query(ThreatIntel)
            .order_by(ThreatIntel.created_at.desc())
            .limit(10)
            .all()
        )
        threats_data = [threat.__dict__ for threat in recent_threats]
        await redis_client.set_cache("recent_threats", threats_data, expire=3600)

    async def _cache_severity_stats(self) -> None:
        """Cache severity distribution statistics."""
        severity_stats = (
            self.db.query(
                ThreatIntel.severity,
                func.count(ThreatIntel.id).label('count')
            )
            .group_by(ThreatIntel.severity)
            .all()
        )
        stats = {severity: count for severity, count in severity_stats}
        await redis_client.set_cache("severity_stats", stats, expire=3600)

    async def _cache_threat_type_stats(self) -> None:
        """Cache threat type distribution statistics."""
        type_stats = (
            self.db.query(
                ThreatIntel.threat_type,
                func.count(ThreatIntel.id).label('count')
            )
            .group_by(ThreatIntel.threat_type)
            .all()
        )
        stats = {threat_type: count for threat_type, count in type_stats}
        await redis_client.set_cache("threat_type_stats", stats, expire=3600)

    async def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get dashboard statistics from cache or compute if not available."""
        stats = await redis_client.get_cache("dashboard_stats")
        if not stats:
            await self._cache_dashboard_stats()
            stats = await redis_client.get_cache("dashboard_stats")
        return stats

    async def get_recent_threats(self) -> List[Dict[str, Any]]:
        """Get recent threats from cache or compute if not available."""
        threats = await redis_client.get_cache("recent_threats")
        if not threats:
            await self._cache_recent_threats()
            threats = await redis_client.get_cache("recent_threats")
        return threats

    async def get_severity_stats(self) -> Dict[str, int]:
        """Get severity distribution from cache or compute if not available."""
        stats = await redis_client.get_cache("severity_stats")
        if not stats:
            await self._cache_severity_stats()
            stats = await redis_client.get_cache("severity_stats")
        return stats

    async def get_threat_type_stats(self) -> Dict[str, int]:
        """Get threat type distribution from cache or compute if not available."""
        stats = await redis_client.get_cache("threat_type_stats")
        if not stats:
            await self._cache_threat_type_stats()
            stats = await redis_client.get_cache("threat_type_stats")
        return stats

    async def invalidate_cache(self, pattern: str = None) -> None:
        """Invalidate cache by pattern."""
        if pattern:
            await redis_client.clear_cache(f"cache:{pattern}")
        else:
            await redis_client.clear_cache()

    async def get_cache_info(self) -> Dict[str, Any]:
        """Get cache statistics and information."""
        return await redis_client.get_cache_stats()
