# AFEAF Auth Service Setup Guide

This guide explains how to set up and run the AFEAF authentication service and its database.

## Prerequisites

- Docker and Docker Compose installed
- Git repository cloned

## Quick Start

1. Navigate to the auth directory:
```bash
cd auth
```

2. Create a `.env` file with the following variables:
```bash
MYSQL_ROOT_PASSWORD=rootpassword
MYSQL_DATABASE=auth_db
MYSQL_USER=auth_user
MYSQL_PASSWORD=auth_password
```

3. Start all services:
```bash
docker-compose up -d
```

## Docker Commands Reference

### Start Services
```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up auth-service -d  # For auth service only
docker-compose up auth-db -d       # For database only
```

### Stop Services
```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clean state)
docker-compose down -v
```

### Build/Rebuild Services
```bash
# Build all services
docker-compose build

# Build specific service
docker-compose build auth-service
```

### View Logs
```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs auth-service
docker-compose logs auth-db
```

## Database Access

Connect to the database:
```bash
docker exec -it auth-db mysql -u auth_user -p -D auth_db
```

### Database Details
- **Host**: 127.0.0.1 (localhost)
- **Port**: 3306
- **Database**: auth_db
- **Default User**: auth_user
- **Root Password**: rootpassword

## Troubleshooting

1. Check service status:
```bash
docker-compose ps
```

2. View service logs:
```bash
docker-compose logs -f
```

3. Restart services:
```bash
docker-compose restart
```

4. Clean restart:
```bash
docker-compose down -v
docker-compose up -d
```

## Development Setup (without Docker)

If you prefer to run the service locally:

1. Create and activate virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app/main.py
```