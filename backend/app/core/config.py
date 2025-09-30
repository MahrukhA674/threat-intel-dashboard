import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Database
    POSTGRES_USER = os.getenv("POSTGRES_USER", "threat_user")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "threat_pass_2024")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "threat_intel_db")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
    
    # ODBC
    ODBC_DRIVER = os.getenv("ODBC_DRIVER", "PostgreSQL Unicode")
    DB_SERVER = os.getenv("DB_SERVER", "localhost")
    DB_NAME = os.getenv("DB_NAME", "threat_intel_db")
    DB_USERNAME = os.getenv("DB_USERNAME", "threat_user")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "threat_pass_2024")

settings = Settings()