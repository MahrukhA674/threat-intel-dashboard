# Use official Python image
FROM python:3.12-slim

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    unixodbc \
    unixodbc-dev \
    gpg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Microsoft ODBC Driver for SQL Server
# Install Microsoft ODBC Driver for SQL Server (Debian 12/Ubuntu 22.04+)
# Install Microsoft ODBC Driver for SQL Server (Debian 12)
RUN set -ex \
    && apt-get update \
    && apt-get install -y --no-install-recommends curl gnupg2 \
    && curl -sSL https://packages.microsoft.com/config/debian/12/packages-microsoft-prod.deb -o packages-microsoft-prod.deb \
    && dpkg -i packages-microsoft-prod.deb \
    && rm packages-microsoft-prod.deb \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18 mssql-tools18 libgssapi-krb5-2 \
    && rm -rf /var/lib/apt/lists/*


# Copy requirements
COPY requirements.txt ./
COPY backend/requirements.txt ./backend-requirements.txt

# Install Python dependencies
RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
    && pip install -r backend-requirements.txt

# Copy backend code
COPY backend/app ./app
COPY backend/tests ./tests

# Expose port
EXPOSE 8000

# Start FastAPI app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
