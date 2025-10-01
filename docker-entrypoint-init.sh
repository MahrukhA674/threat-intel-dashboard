#!/bin/bash
set -e

echo "Waiting for SQL Server service to be healthy..."
until /opt/mssql-tools18/bin/sqlcmd -S db -U sa -P "${DB_PASSWORD}" -d master -Q "SELECT 1" -C &>/dev/null; do
  echo "SQL Server is unavailable - sleeping"
  sleep 5
done

echo "SQL Server engine is up. Executing initialization script..."
/opt/mssql-tools18/bin/sqlcmd -S db -U sa -P "${DB_PASSWORD}" -d master -i /scripts/init.sql -C

echo "Initialization complete."

# Now wait for the specific application database to be ready
echo "Waiting for specific database '${DB_NAME}' to be ready..."
until /opt/mssql-tools18/bin/sqlcmd -S db -U sa -P "${DB_PASSWORD}" -d "${DB_NAME}" -Q "SELECT 1" -C &>/dev/null; do
  echo "Database '${DB_NAME}' not yet available. Sleeping..."
  sleep 5
done

echo "Database '${DB_NAME}' is ready. Starting backend application."

# Run the main container process
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload