
import asyncio
import pyodbc
import threading
import queue
import time
import logging
from contextlib import contextmanager
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class PyODBCConnectionManager:
    """
    ODBC Connection Manager with connection pooling and queue management.
    
    Features:
    - Connection pooling with configurable pool size
    - Thread-safe queue for connection requests
    - Automatic connection health checks
    - Connection recycling after timeout
    - Graceful connection cleanup
    - Query execution helpers
    """
    
    def __init__(
        self,
        driver: Optional[str] = None,
        server: Optional[str] = None,
        database: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        pool_size: int = 10,
        max_pool_size: int = 20,
        timeout: int = 30,
        recycle_time: int = 3600,
        autocommit: bool = True
    ):
        """
        Initialize PyODBC Connection Manager.
        
        Args:
            driver: ODBC driver name (from env: ODBC_DRIVER)
            server: Database server (from env: DB_SERVER)
            database: Database name (from env: DB_NAME)
            username: Database username (from env: DB_USERNAME)
            password: Database password (from env: DB_PASSWORD)
            pool_size: Initial number of connections in pool
            max_pool_size: Maximum number of connections allowed
            timeout: Connection timeout in seconds
            recycle_time: Time before connection is recycled (seconds)
            autocommit: Enable autocommit mode (default: True)
        """
        # Load from environment variables if not provided
        self.driver = driver or os.getenv("ODBC_DRIVER", "ODBC Driver 17 for SQL Server")
        self.server = server or os.getenv("DB_SERVER", "localhost")
        self.database = database or os.getenv("DB_NAME", "threat_intel_db")
        self.username = username or os.getenv("DB_USERNAME", "threat_user")
        self.password = password or os.getenv("DB_PASSWORD", "threat_pass_2024")
        
        self.pool_size = pool_size
        self.max_pool_size = max_pool_size
        self.timeout = timeout
        self.recycle_time = recycle_time
        self.autocommit = autocommit
        
        # Build connection string
        self.connection_string = (
            f"DRIVER={{{self.driver}}};"
            f"SERVER={self.server};"
            f"DATABASE={self.database};"
            f"UID={self.username};"
            f"PWD={self.password};"
            f"TrustServerCertificate=yes;"
        )
        
        # queue of available connections
        self.pool = queue.Queue(maxsize=max_pool_size)
        

       
        
        # Initialize pool
        self.initialize_pool()
        
        logger.info(
            f"PyODBCConnectionManager initialized: "
            f"server={self.server}, database={self.database}, "
            f"pool_size={pool_size}, max_pool_size={max_pool_size}, "
            f"autocommit={autocommit}"
        )
    
   
           
    
    async def initialize_pool(self):
        """Initialize the connection pool with initial connections."""
        logger.info(f"Initializing connection pool with {self.pool_size} connections...")
        
        for _ in range(self.pool_size):
            try: 
                connection = await asyncio.to_thread(self._create_connection, autocommit=self.autocommit)
                self.pool.put(connection)
            except Exception as e:
                logger.error(f"Error creating initial connection: {e}") 
    
    async def _is_connection_valid(self, conn: pyodbc.Connection) -> bool:
        """Check if connection is still valid."""
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            return True
        except Exception as e:
            logger.warning(f"Connection validation failed: {e}")
            return False
    
    async def close_all(self):
        """Close all connections in the pool."""
        logger.info("Closing all connections in the pool...")
        while not self.pool.empty(): 
            connection = await self.pool.get()
            try:
                await asyncio.wait_for(asyncio.to_thread(connection.close), timeout=self.timeout)
            except Exception as e:
                logger.error(f"Error closing connection: {e}")
        logger.info("All connections closed.")

    async def _get_connection(self) -> pyodbc.Connection:
        """Get a connection from the pool, creating a new one if necessary."""
        try: 
            return await asyncio.wait_for(asyncio.to_thread(self.pool.get), timeout=self.timeout)
        except asyncio.TimeoutError: 
            logger.error("Timeout waiting for a connection from the pool.")
        except Exception as e:
            logger.error(f"Error getting connection from pool: {e}")

    async def _release_connection(self, conn: pyodbc.Connection):
        """Release a connection back to the pool."""
        try:
            if await self._is_connection_valid(conn):
                self.pool.put(conn)
            else:
                logger.info("Connection is invalid, creating a new one.")
                new_conn = await asyncio.to_thread(self._create_connection, autocommit=self.autocommit)
                self.pool.put(new_conn)
        except Exception as e:
            logger.error(f"Error releasing connection: {e}")


    async def query(self, query: str, params: Optional[Tuple[Any, ...]] = None) -> List[Tuple]:
        """Execute a query and return results."""
        conn = await self._get_connection()
        if not conn:
            raise Exception("No available connection.")
        try: 
            logger.debug(f"Executing query: {query} with params: {params}")
            logger.debug(f"Using connection: {conn}")
            
            
            def execute_query(conn, query, params):
                cursor = conn.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                if cursor.description:  # If the query returns rows
                    columns = [column[0] for column in cursor.description]
                    rows = cursor.fetchall()
                    cursor.close()
                    return [dict(zip(columns, row)) for row in rows] #pair columns with value and return as a dictionary
                cursor.close()
                return None
            
            start_time = time.perf_counter()
            result = await asyncio.to_thread(execute_query, conn, query, params)
            end_time = time.perf_counter()

            logger.debug(f"Query executed in {end_time - start_time:.4f} seconds.")
            return result or [] 
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            traceback.print_exc()
            raise
        finally:
            await self._release_connection(conn)
        