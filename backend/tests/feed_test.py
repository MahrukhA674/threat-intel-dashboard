# Mock models for testing (replace with your actual models)
from asyncio.log import logger
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from backend.app.services.feed_service import FeedService

class MockDB:
    def __init__(self):
        self.items = []
    
    def add_all(self, items):
        self.items.extend(items)
        logger.info(f"Added {len(items)} items to database")
    
    def commit(self):
        logger.info("Database committed")
    
    def rollback(self):
        logger.info("Database rolled back")
@dataclass
class IPThreat:
    ip_address: str
    confidence_score: int
    is_public: bool
    abuse_types: List[int]
    total_reports: int
    last_reported_at: Optional[datetime]
    country_code: str

# Mock settings for testing
class Settings:
    ABUSEIPDB_API_URL = "https://api.abuseipdb.com/api/v2"
    ABUSEIPDB_API_KEY = "YOUR_API_KEY_HERE"  # Replace with actual key

settings = Settings()

# Mock cache service for testing
class MockCacheService:
    async def refresh_cache(self):
        logger.info("Cache refreshed")
        
async def test_with_mock_data():
    """Test the service with mock data (no actual API calls)"""
    
    class MockFeedService(FeedService):
        """Override fetch to return mock data"""
        
        async def fetch_with_rate_limit(self, session, url, headers=None):
            """Return mock data instead of making API call"""
            logger.info("Using mock data instead of API call")
            
            # Mock AbuseIPDB response
            return {
                "data": [
                    {
                        "ipAddress": "192.168.1.1",
                        "abuseConfidenceScore": 95,
                        "isWhitelisted": False,
                        "categories": [1, 2, 3, 4],
                        "totalReports": 25,
                        "lastReportedAt": "2024-01-15T10:30:00Z",
                        "countryCode": "US"
                    },
                    {
                        "ipAddress": "10.0.0.1",
                        "abuseConfidenceScore": 75,
                        "isWhitelisted": False,
                        "categories": [2, 5],
                        "totalReports": 10,
                        "lastReportedAt": "2024-01-14T08:20:00Z",
                        "countryCode": "UK"
                    },
                    {
                        "ipAddress": "172.16.0.1",
                        "abuseConfidenceScore": 60,
                        "isWhitelisted": False,
                        "categories": [1],
                        "totalReports": 5,
                        "lastReportedAt": "2024-01-13T15:45:00Z",
                        "countryCode": "CA"
                    }
                ] * 50  # Multiply to test chunking
            }
    
    # Create mock dependencies
    db = MockDB()
    cache_service = MockCacheService()
    
    # Create service and run ingestion
    service = MockFeedService(db, cache_service)
    results = await service.ingest_feeds()
    
    print("\n" + "="*60)
    print("MOCK TEST RESULTS:")
    print("="*60)
    print(f"Ingested: {results['ip_threats_ingested']} IP threats")
    
    # Show some sample data
    if db.items:
        print(f"\nSample threats:")
        for threat in db.items[:3]:
            print(f"  - IP: {threat.ip_address}, Score: {threat.confidence_score}, Country: {threat.country_code}")
            print(f"    Severity: {service._determine_severity(threat)}")
    print("="*60 + "\n")


async def test_with_real_api():
    """Test with real API (requires valid API key)"""
    
    if settings.ABUSEIPDB_API_KEY == "YOUR_API_KEY_HERE":
        print("\n⚠️  Please set a valid ABUSEIPDB_API_KEY to test with real API")
        return
    
    # Create real dependencies
    db = MockDB()  # Still using mock DB for testing
    cache_service = MockCacheService()
    
    # Create service and run ingestion
    service = FeedService(db, cache_service)
    
    try:
        results = await service.ingest_feeds()
        
        print("\n" + "="*60)
        print("REAL API TEST RESULTS:")
        print("="*60)
        print(f"Ingested: {results['ip_threats_ingested']} IP threats")
        
        # Show some sample data
        if db.items:
            print(f"\nSample threats (first 5):")
            for threat in db.items[:5]:
                print(f"  - IP: {threat.ip_address}, Score: {threat.confidence_score}, Country: {threat.country_code}")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error with real API: {e}")


async def main():
    """Main test function"""
    print("\n" + "="*60)
    print("FEED SERVICE TEST")
    print("="*60)
    
    # Test 1: With mock data
    print("\n📝 Running test with mock data...")
    await test_with_mock_data()
    
    # Test 2: With real API (if configured)
    print("\n🌐 Running test with real API...")
    await test_with_real_api()
    
    print("\n✅ All tests completed!")


if __name__ == "__main__":
    # Run the tests
    asyncio.run(main())