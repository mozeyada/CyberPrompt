# CyberCQBench Quick Setup

## One-Command Start

```bash
./start.sh
```

## Manual Setup

### 1. Prerequisites
- Docker & Docker Compose
- Git

### 2. Clone & Setup
```bash
git clone <repository-url>
cd CyberCQBench
cp .env.example .env
# Edit .env with your API keys
```

### 3. Start Application
```bash
# Option 1: Use startup script
./start.sh

# Option 2: Manual Docker commands
docker compose build
docker compose up -d
```

### 4. Access Application
- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000/docs
- **Database Admin**: http://localhost:8081

### 5. Import Sample Data
```bash
docker compose exec api python scripts/import_cysecbench.py 50
```

## Troubleshooting

### Port Conflicts
If ports are in use, modify `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Change 8000 to 8001
```

### Permission Issues
```bash
sudo chown -R $USER:$USER .
```

### Clean Restart
```bash
docker compose down -v
docker system prune -f
./start.sh
```

## Production Deployment
```bash
docker compose -f docker-compose.prod.yml up -d
```