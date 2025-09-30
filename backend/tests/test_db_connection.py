import pytest
import pytest_asyncio
import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.pyodbc_manager import PyODBCConnectionManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest_asyncio.fixture
async def db_manager():
    """Fixture that provides a PyODBCConnectionManager instance."""
    # Create manager
    manager = PyODBCConnectionManager(
        pool_size=3,
        max_pool_size=5,
        timeout=30,
        autocommit=True
    )
    
    # Initialize pool
    await manager.initialize_pool()
    await asyncio.sleep(1)
    
    logger.info(f"✅ Fixture: Manager initialized with {manager.pool.qsize()} connections")
    
    # Yield manager to test
    yield manager
    
    # Cleanup
    logger.info("🧹 Fixture: Cleaning up")
    await manager.close_all()


@pytest.mark.asyncio
async def test_database_connection(db_manager):
    """Test 1: Basic database connectivity."""
    logger.info("=" * 70)
    logger.info("TEST 1: Database Connection")
    logger.info("=" * 70)
    
    result = await db_manager.query("SELECT 1 as test")
    
    assert result is not None
    assert len(result) == 1
    assert result[0]['test'] == 1
    
    logger.info("✅ TEST 1 PASSED\n")


@pytest.mark.asyncio
async def test_connection_pool(db_manager):
    """Test 2: Connection pool functionality."""
    logger.info("=" * 70)
    logger.info("TEST 2: Connection Pool")
    logger.info("=" * 70)
    
    # Execute concurrent queries
    queries = [db_manager.query("SELECT 1 as test") for _ in range(3)]
    results = await asyncio.gather(*queries)
    
    assert len(results) == 3
    for result in results:
        assert result[0]['test'] == 1
    
    logger.info("✅ TEST 2 PASSED\n")


@pytest.mark.asyncio
async def test_query_with_params(db_manager):
    """Test 3: Parameterized queries."""
    logger.info("=" * 70)
    logger.info("TEST 3: Query with Parameters")
    logger.info("=" * 70)
    
    # Simple parameterized query
    query = "SELECT %s::text as name, %s::int as age"
    result = await db_manager.query(query, ("Alice", 30))
    
    assert result is not None
    assert len(result) == 1
    assert result[0]['name'] == "Alice"
    assert result[0]['age'] == 30
    
    logger.info("✅ TEST 3 PASSED\n")


@pytest.mark.asyncio
async def test_query_users_table(db_manager):
    """Test 4: Query actual database table."""
    logger.info("=" * 70)
    logger.info("TEST 4: Query Users Table")
    logger.info("=" * 70)
    
    result = await db_manager.query("SELECT * FROM users LIMIT 5")
    
    assert result is not None
    logger.info(f"✅ Found {len(result)} users")
    
    if result:
        logger.info(f"✅ User columns: {list(result[0].keys())}")
    
    logger.info("✅ TEST 4 PASSED\n")


@pytest.mark.asyncio
async def test_count_all_tables(db_manager):
    """Test 5: Count records in all tables."""
    logger.info("=" * 70)
    logger.info("TEST 5: Count All Tables")
    logger.info("=" * 70)
    
    tables = ["users", "cve_data", "ip_threats", "otx_pulses", "feed_status"]
    
    for table in tables:
        result = await db_manager.query(f"SELECT COUNT(*) as count FROM {table}")
        count = result[0]['count']
        logger.info(f"  ✅ {table}: {count} records")
    
    logger.info("✅ TEST 5 PASSED\n")


@pytest.mark.asyncio
async def test_error_handling(db_manager):
    """Test 6: Error handling."""
    logger.info("=" * 70)
    logger.info("TEST 6: Error Handling")
    logger.info("=" * 70)
    
    # Try invalid query
    try:
        await db_manager.query("SELECT * FROM non_existent_table")
        pytest.fail("Should have raised exception")
    except Exception as e:
        logger.info(f"✅ Caught error: {type(e).__name__}")
    
    # Verify pool still works
    result = await db_manager.query("SELECT 1 as test")
    assert result[0]['test'] == 1
    
    logger.info("✅ TEST 6 PASSED\n")


@pytest.mark.asyncio
async def test_concurrent_queries(db_manager):
    """Test 7: Concurrent query execution."""
    logger.info("=" * 70)
    logger.info("TEST 7: Concurrent Queries")
    logger.info("=" * 70)
    
    import time
    
    async def query_task(i):
        return await db_manager.query("SELECT 1 as test")
    
    start = time.perf_counter()
    tasks = [query_task(i) for i in range(10)]
    results = await asyncio.gather(*tasks)
    end = time.perf_counter()
    
    assert len(results) == 10
    logger.info(f"✅ 10 queries in {end - start:.4f} seconds")
    logger.info("✅ TEST 7 PASSED\n")


@pytest.mark.asyncio  
async def test_connection_validation(db_manager):
    """Test 8: Connection validation."""
    logger.info("=" * 70)
    logger.info("TEST 8: Connection Validation")
    logger.info("=" * 70)
    
    conn = await db_manager._get_connection()
    assert conn is not None
    
    is_valid = await db_manager._is_connection_valid(conn)
    assert is_valid
    
    await db_manager._release_connection(conn)
    logger.info("✅ TEST 8 PASSED\n")


@pytest.mark.asyncio
async def test_database_version(db_manager):
    """Test 9: Get database version."""
    logger.info("=" * 70)
    logger.info("TEST 9: Database Version")
    logger.info("=" * 70)
    
    result = await db_manager.query("SELECT version() as version")
    version = result[0]['version']
    
    logger.info(f"✅ Version: {version}")
    assert "PostgreSQL" in version
    logger.info("✅ TEST 9 PASSED\n")


@pytest.mark.asyncio
async def test_pool_exhaustion(db_manager):
    """Test 10: Pool exhaustion handling."""
    logger.info("=" * 70)
    logger.info("TEST 10: Pool Exhaustion")
    logger.info("=" * 70)
    
    initial = db_manager.pool.qsize()
    logger.info(f"Initial pool size: {initial}")
    
    # Get all connections
    conns = []
    for i in range(initial):
        conn = await db_manager._get_connection()
        conns.append(conn)
    
    assert db_manager.pool.qsize() == 0
    logger.info("✅ Pool exhausted")
    
    # Release all
    for conn in conns:
        await db_manager._release_connection(conn)
    
    logger.info(f"✅ Pool restored: {db_manager.pool.qsize()}")
    logger.info("✅ TEST 10 PASSED\n")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])