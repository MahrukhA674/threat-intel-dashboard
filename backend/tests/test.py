import pyodbc
import os

conn = pyodbc.connect(
    "DRIVER={ODBC Driver 18 for SQL Server};"
    f"SERVER={os.getenv('DB_SERVER', 'db')},{os.getenv('DB_PORT', '1433')};"
    f"DATABASE={os.getenv('DB_NAME', 'threat_intel_db')};"
    f"UID={os.getenv('DB_USERNAME', 'sa')};"
    f"PWD={os.getenv('DB_PASSWORD')};"
    "TrustServerCertificate=yes;"
)
cursor = conn.cursor()
cursor.execute("SELECT 1")
print(cursor.fetchone())
conn.close()
