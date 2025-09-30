import asyncio
import aiohttp
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from ..core.config import settings
from ..models.models import CVE, IPThreat, OTXThreat, ThreatIntel
from ..db.redis_client import redis_client
from .cache_service import CacheService

class FeedService:
    def __init__(self, db: Session, cache_service: CacheService):
        self.db = db
        self.cache_service = cache_service
        self.semaphore = asyncio.Semaphore(5)  # Limit concurrent requests to 5

    async def fetch_with_rate_limit(self, session: aiohttp.ClientSession, url: str, headers: Dict[str, str] = None) -> Optional[Dict]:
        """Fetch data from URL with rate limiting and error handling."""
        async with self.semaphore:
            try:
                async with session.get(url, headers=headers) as response:
                    if response.status == 429:  # Too Many Requests
                        retry_after = int(response.headers.get('Retry-After', '60'))
                        await asyncio.sleep(retry_after)
                        return await self.fetch_with_rate_limit(session, url, headers)
                    
                    response.raise_for_status()
                    return await response.json()
            except aiohttp.ClientError as e:
                print(f"Error fetching {url}: {str(e)}")
                return None

    async def process_cve_feed(self) -> List[CVE]:
        """Process CVE feed data."""
        async with aiohttp.ClientSession() as session:
            url = f"{settings.NVD_API_URL}/cves/recent"
            headers = {"API-Key": settings.NVD_API_KEY}
            
            data = await self.fetch_with_rate_limit(session, url, headers)
            if not data:
                return []

            cves = []
            for item in data.get('vulnerabilities', []):
                cve_data = item.get('cve', {})
                cve = CVE(
                    cve_id=cve_data.get('id'),
                    description=cve_data.get('description', {}).get('description', [])[0],
                    severity=cve_data.get('metrics', {}).get('severity', 'UNKNOWN'),
                    cvss_score=str(cve_data.get('metrics', {}).get('cvssMetricV31', [{}])[0].get('cvssData', {}).get('baseScore', 0)),
                    published_date=datetime.fromisoformat(cve_data.get('published')),
                    last_modified_date=datetime.fromisoformat(cve_data.get('lastModified')),
                    references=cve_data.get('references', [])
                )
                cves.append(cve)
                
            return cves

    async def process_abuseipdb_feed(self) -> List[IPThreat]:
        """Process AbuseIPDB feed data."""
        async with aiohttp.ClientSession() as session:
            url = f"{settings.ABUSEIPDB_API_URL}/blacklist"
            headers = {"Key": settings.ABUSEIPDB_API_KEY}
            
            data = await self.fetch_with_rate_limit(session, url, headers)
            if not data:
                return []

            threats = []
            for item in data.get('data', []):
                threat = IPThreat(
                    ip_address=item.get('ipAddress'),
                    confidence_score=item.get('abuseConfidenceScore'),
                    is_public=item.get('isPublic', True),
                    abuse_types=item.get('categories', []),
                    total_reports=item.get('totalReports', 0),
                    last_reported_at=datetime.fromisoformat(item.get('lastReportedAt')),
                    country_code=item.get('countryCode')
                )
                threats.append(threat)
                
            return threats

    async def process_otx_feed(self) -> List[OTXThreat]:
        """Process OTX feed data."""
        async with aiohttp.ClientSession() as session:
            url = f"{settings.OTX_API_URL}/pulses/subscribed"
            headers = {"X-OTX-API-KEY": settings.OTX_API_KEY}
            
            data = await self.fetch_with_rate_limit(session, url, headers)
            if not data:
                return []

            threats = []
            for item in data.get('results', []):
                threat = OTXThreat(
                    pulse_id=item.get('id'),
                    name=item.get('name'),
                    description=item.get('description'),
                    author_name=item.get('author_name'),
                    tlp=item.get('TLP', 'white'),
                    tags=item.get('tags', []),
                    indicators=item.get('indicators', []),
                    references=item.get('references', [])
                )
                threats.append(threat)
                
            return threats

    async def ingest_feeds(self) -> Dict[str, int]:
        """Ingest data from all feeds."""
        try:
            # Process feeds concurrently
            cves, ip_threats, otx_threats = await asyncio.gather(
                self.process_cve_feed(),
                self.process_abuseipdb_feed(),
                self.process_otx_feed()
            )

            # Save to database
            self.db.add_all(cves)
            self.db.add_all(ip_threats)
            self.db.add_all(otx_threats)
            self.db.commit()

            # Update cache
            await self.cache_service.refresh_cache()

            return {
                "cves_ingested": len(cves),
                "ip_threats_ingested": len(ip_threats),
                "otx_threats_ingested": len(otx_threats)
            }
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Feed ingestion failed: {str(e)}")

    async def transform_and_store(self, source: str, data: List[Any]) -> None:
        """Transform and store threat data."""
        threats = []
        for item in data:
            threat = ThreatIntel(
                source=source,
                source_id=str(item.id),
                threat_type=self._determine_threat_type(item),
                severity=self._determine_severity(item),
                confidence=self._determine_confidence(item),
                raw_data=item.__dict__
            )
            threats.append(threat)

        self.db.add_all(threats)
        self.db.commit()

    def _determine_threat_type(self, item: Any) -> str:
        """Determine threat type based on the item."""
        if isinstance(item, CVE):
            return "vulnerability"
        elif isinstance(item, IPThreat):
            return "malicious_ip"
        elif isinstance(item, OTXThreat):
            return "indicator"
        return "unknown"

    def _determine_severity(self, item: Any) -> str:
        """Determine severity based on the item."""
        if isinstance(item, CVE):
            return item.severity
        elif isinstance(item, IPThreat):
            score = item.confidence_score
            if score >= 90:
                return "critical"
            elif score >= 70:
                return "high"
            elif score >= 50:
                return "medium"
            return "low"
        elif isinstance(item, OTXThreat):
            return "medium"  # Default for OTX
        return "unknown"

    def _determine_confidence(self, item: Any) -> int:
        """Determine confidence score based on the item."""
        if isinstance(item, CVE):
            return 100  # NVD data is considered highly reliable
        elif isinstance(item, IPThreat):
            return item.confidence_score
        elif isinstance(item, OTXThreat):
            return 70  # Default confidence for OTX data
        return 50  # Default confidence
