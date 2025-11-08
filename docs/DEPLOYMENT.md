# ExamSensei Deployment Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Docker Deployment](#docker-deployment)
4. [Production Deployment](#production-deployment)
5. [Environment Configuration](#environment-configuration)
6. [Database Migrations](#database-migrations)
7. [Monitoring & Logging](#monitoring--logging)

## Prerequisites

### Required Software
- **Docker** & **Docker Compose** (v2.0+)
- **Python** 3.11+
- **Node.js** 20+
- **PostgreSQL** 15+ (for production)
- **Redis** 7+ (for caching)
- **Ollama** (for AI features)

### System Requirements
- **RAM**: Minimum 4GB (8GB recommended)
- **Storage**: 20GB free space
- **CPU**: 2+ cores recommended

## Local Development Setup

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/ExamSensei.git
cd ExamSensei
```

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
alembic upgrade head

# Seed initial data
python seed_data.py

# Start development server
uvicorn app_v2:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Create .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1" > .env.local

# Start development server
npm run dev
```

### 4. Install Ollama (for AI features)
```bash
# Linux/Mac
curl -fsSL https://ollama.com/install.sh | sh

# Windows: Download from https://ollama.com/download

# Pull required model
ollama pull llama2
```

## Docker Deployment

### Quick Start (All Services)
```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Individual Services
```bash
# Start only backend
docker-compose up -d backend postgres redis

# Start only frontend
docker-compose up -d frontend

# Rebuild specific service
docker-compose up -d --build backend
```

### Database Initialization
```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Seed data
docker-compose exec backend python seed_data.py
```

## Production Deployment

### 1. Server Setup (Ubuntu 22.04)

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose-plugin

# Create application directory
sudo mkdir -p /opt/examsensei
sudo chown $USER:$USER /opt/examsensei
cd /opt/examsensei
```

### 2. Clone and Configure

```bash
# Clone repository
git clone https://github.com/yourusername/ExamSensei.git .

# Create production .env
cp backend/.env.example backend/.env

# IMPORTANT: Update these values
nano backend/.env
```

**Critical Production Settings:**
```env
# Generate secure secret key
SECRET_KEY=$(openssl rand -hex 32)

# Use PostgreSQL
DATABASE_URL=postgresql://user:password@postgres:5432/examsensei

# Set production environment
ENVIRONMENT=production

# Configure email
SMTP_HOST=smtp.gmail.com
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Add Sentry for monitoring
SENTRY_DSN=your-sentry-dsn
```

### 3. SSL/TLS Setup (Let's Encrypt)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d examsensei.com -d www.examsensei.com

# Auto-renewal (already configured)
sudo systemctl status certbot.timer
```

### 4. Nginx Configuration

Create `/opt/examsensei/nginx/nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:3000;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

    server {
        listen 80;
        server_name examsensei.com www.examsensei.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name examsensei.com www.examsensei.com;

        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;

        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;

        # API routes
        location /api/ {
            limit_req zone=api_limit burst=20 nodelay;
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Frontend routes
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_cache_bypass $http_upgrade;
        }
    }
}
```

### 5. Start Production Services

```bash
# Start all services
docker-compose -f docker-compose.yml up -d

# Run migrations
docker-compose exec backend alembic upgrade head

# Seed initial data
docker-compose exec backend python seed_data.py

# Check status
docker-compose ps
```

## Environment Configuration

### Backend Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DATABASE_URL` | PostgreSQL connection string | sqlite:///./examsensei.db | Yes |
| `SECRET_KEY` | JWT secret key | - | Yes |
| `OLLAMA_URL` | Ollama API URL | http://localhost:11434 | Yes |
| `REDIS_URL` | Redis connection string | redis://localhost:6379/0 | Yes |
| `ENVIRONMENT` | Environment (development/production) | development | Yes |
| `SENTRY_DSN` | Sentry monitoring DSN | - | No |

### Frontend Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | http://localhost:8000/api/v1 | Yes |

## Database Migrations

### Create Migration
```bash
# Auto-generate migration
alembic revision --autogenerate -m "description"

# Manual migration
alembic revision -m "description"
```

### Apply Migrations
```bash
# Upgrade to latest
alembic upgrade head

# Upgrade to specific version
alembic upgrade <revision>

# Downgrade
alembic downgrade -1
```

### Migration History
```bash
# Show current version
alembic current

# Show history
alembic history

# Show pending migrations
alembic show <revision>
```

## Monitoring & Logging

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Health Checks
```bash
# API health
curl http://localhost:8000/api/v1/health

# Database connection
docker-compose exec postgres pg_isready

# Redis connection
docker-compose exec redis redis-cli ping
```

### Performance Monitoring

**Sentry Integration** (Recommended):
1. Sign up at https://sentry.io
2. Create new project
3. Add DSN to `.env`:
   ```env
   SENTRY_DSN=https://your-dsn@sentry.io/project-id
   ```

### Backup & Restore

```bash
# Backup database
docker-compose exec postgres pg_dump -U examsensei examsensei > backup.sql

# Restore database
docker-compose exec -T postgres psql -U examsensei examsensei < backup.sql

# Backup with Docker volume
docker run --rm -v examsensei_postgres_data:/data -v $(pwd):/backup \
  ubuntu tar czf /backup/postgres_backup.tar.gz /data
```

## Troubleshooting

### Common Issues

**1. Ollama not responding**
```bash
# Check Ollama status
docker-compose logs ollama

# Restart Ollama
docker-compose restart ollama

# Pull model again
docker-compose exec ollama ollama pull llama2
```

**2. Database connection errors**
```bash
# Check PostgreSQL status
docker-compose exec postgres pg_isready

# Reset database
docker-compose down -v
docker-compose up -d postgres
docker-compose exec backend alembic upgrade head
```

**3. Frontend can't connect to backend**
- Check `NEXT_PUBLIC_API_URL` in frontend `.env.local`
- Verify CORS settings in backend `config.py`
- Check network connectivity: `docker-compose exec frontend ping backend`

## Security Checklist

- [ ] Change default `SECRET_KEY`
- [ ] Use strong database passwords
- [ ] Enable SSL/TLS certificates
- [ ] Configure firewall (UFW)
- [ ] Set up fail2ban
- [ ] Enable rate limiting
- [ ] Configure Sentry monitoring
- [ ] Regular security updates
- [ ] Backup strategy in place
- [ ] Environment variables secured

## Scaling

### Horizontal Scaling
```yaml
# docker-compose.yml
services:
  backend:
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1'
          memory: 1G
```

### Load Balancing
Use Nginx upstream with multiple backend instances:
```nginx
upstream backend {
    least_conn;
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}
```

## Support

For issues and questions:
- GitHub Issues: https://github.com/yourusername/ExamSensei/issues
- Documentation: https://docs.examsensei.com
- Email: support@examsensei.com
