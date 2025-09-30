cat > README.md << 'EOF'
# Threat Intelligence Dashboard

A comprehensive threat intelligence platform for security operations.

## Features
- CVE vulnerability tracking
- Malicious IP monitoring
- AlienVault OTX pulse integration
- Real-time threat analytics
- Redis caching with session management
- JWT authentication

## Tech Stack
- **Backend**: FastAPI, PostgreSQL, Redis
- **Frontend**: React, Recharts, Tailwind CSS
- **Deployment**: Docker, Docker Compose

## Setup Instructions

### Quick Start with Docker
```bash
docker-compose up -d