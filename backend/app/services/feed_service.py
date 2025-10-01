import asyncio
from asyncio.log import logger
import concurrent
import asyncio
import concurrent.futures
import aiohttp
import concurrent.futures
from datetime import datetime
from typing import Generator, List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.core.config import settings
from ..models.models import CVE, IPThreat, OTXThreat, ThreatIntel
from ..db.redis_client import redis_client
from .cache_service import CacheService

class FeedService:
    def __init__(self, db: Session, cache_service: CacheService):
        self.db = db
        self.cache_service = cache_service
        self.semaphore = asyncio.Semaphore(5)  # Limit concurrent requests to 5
 
    @staticmethod
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
    
    
    @staticmethod 
    def _yield_vuls_from_data(data: List[Dict[str, Any]], page_size: int = 100) -> Generator[List[Dict[str, Any]], None, None]:
        """Yield chunks of vulnerabilities from data."""
        data = [] 
        idx = 0 
        for vuln in data:
            data.append(vuln)
            idx += 1
            if idx % page_size == 0:
                yield data
                data = []
                idx = 0 
        if data:
            yield data

    async def process_abuseipdb_feed(self, callback) -> List[IPThreat]:
        """Process AbuseIPDB feed data."""
        async with aiohttp.ClientSession() as session:
            url = f"{settings.ABUSEIPDB_API_URL}/blacklist"
            headers = {"Key": settings.ABUSEIPDB_API_KEY}

            data = await self.fetch_with_rate_limit(session, url, headers)

            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                futures = [] 
                for vuln_chunk in self._yield_vuls_from_data(data, page_size=100):
                    future = executor.submit(callback, vuln_chunk)

                # Wait for all futures to complete
                results = await asyncio.gather(*futures)
                # Flatten results
                threats = []
                for chunk_result in results:
                    threats.extend(chunk_result)
        return threats

                    

    
    async def callback(data: Dict[str, Any]) -> List[IPThreat]: 
        """Callback to process each chunk of vulnerabilities."""

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
        
    async def ingest_feeds(self) -> Dict[str, int]:
        """Ingest data from all feeds."""
        try:
            # Process feeds concurrently
            ip_threats  = await asyncio.gather(
              
                self.process_abuseipdb_feed(self.callback),
        
            )

            # Save to database
         
            self.db.add_all(ip_threats)
        
            self.db.commit()

            # Update cache
            await self.cache_service.refresh_cache()

            return {
               
                "ip_threats_ingested": len(ip_threats)
            }
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Feed ingestion failed: {str(e)}")

    a

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
      
        if isinstance(item, IPThreat):
            score = item.confidence_score
            if score >= 90:
                return "critical"
            elif score >= 70:
                return "high"
            elif score >= 50:
                return "medium"
            return "low"
       

    def _determine_confidence(self, item: Any) -> int:
        """Determine confidence score based on the item."""
        if isinstance(item, CVE):
            return 100  # NVD data is considered highly reliable
        elif isinstance(item, IPThreat):
            return item.confidence_score
        elif isinstance(item, OTXThreat):
            return 70  # Default confidence for OTX data
        return 50  # Default confidence
