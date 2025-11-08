# ⚡ ExamSensei Quick Start Guide

Get ExamSensei running in **under 10 minutes**.

## 🎯 Prerequisites

Install these first:

### Required
- **Python 3.11+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** - [Download](https://nodejs.org/) (Recommended: 20.11.0 LTS)
- **Git** - [Download](https://git-scm.com/downloads/)

### Optional (for full features)
- **Docker** - [Download](https://docs.docker.com/get-docker/) (for containerized deployment)
- **Ollama** - [Download](https://ollama.com/download) (for AI features)
- **PostgreSQL 15+** - [Download](https://www.postgresql.org/download/) (for production)
- **Redis 7+** - [Download](https://redis.io/download) (for caching)

## 🚀 Installation

### 1. Clone & Navigate
```bash
git clone https://github.com/yourusername/ExamSensei.git
cd ExamSensei
```

### 2. Quick Start (Recommended)
```bash
# Use the automated startup script
start.bat  # Windows
# OR
./start.sh  # Linux/Mac

# Choose option 2 (Local Development)
```

### 3. Manual Setup (Alternative)

#### Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies (single command!)
pip install -r requirements.txt

# Initialize database
alembic upgrade head
python seed_data.py

# Start backend
uvicorn app_v2:app --reload
```

#### Frontend Setup (New Terminal)
```bash
cd frontend

# Install dependencies (single command!)
npm install --legacy-peer-deps

# Start frontend
npm run dev
```

### 4. Docker Setup (Alternative)
```bash
# From project root
docker-compose up -d

# Initialize database
docker-compose exec backend alembic upgrade head
docker-compose exec backend python seed_data.py
```

## ✅ Verify Installation

### Check Services
```bash
# All services should be "Up"
docker-compose ps

# Check logs
docker-compose logs -f
```

### Test Endpoints
```bash
# Health check
curl http://localhost:8000/api/v1/health

# Get exams (public endpoint)
curl http://localhost:8000/api/v1/exams

# API documentation
open http://localhost:8000/api/v1/docs
```

### Access Applications
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/api/v1/docs
- **Ollama**: http://localhost:11434

## 🧪 Test Authentication

### 1. Register User
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123",
    "name": "Test User",
    "education_level": "class_12",
    "state": "Tamil Nadu",
    "category": "general",
    "budget": "medium"
  }'
```

### 2. Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=testpass123"

# Save the access_token from response
```

### 3. Access Protected Endpoint
```bash
# Replace YOUR_TOKEN with the access_token from step 2
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🛠️ Development Mode

### Backend Development
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app_v2:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development
```bash
cd frontend

# Install dependencies
npm install

# Create .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1" > .env.local

# Run development server
npm run dev
```

### Run Tests
```bash
# Backend tests
cd backend
pytest --cov

# Frontend tests
cd frontend
npm test
```

## 🐛 Troubleshooting

### Ollama Not Responding
```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama
# Windows/Mac: Restart Ollama app
# Linux: systemctl restart ollama

# Pull model again
ollama pull llama2
```

### Database Connection Error
```bash
# Reset database
docker-compose down -v
docker-compose up -d postgres
sleep 5
docker-compose exec backend alembic upgrade head
docker-compose exec backend python seed_data.py
```

### Port Already in Use
```bash
# Find process using port 8000
# Windows: netstat -ano | findstr :8000
# Mac/Linux: lsof -i :8000

# Kill the process or change port in docker-compose.yml
```

### Docker Build Fails
```bash
# Clean Docker cache
docker system prune -a

# Rebuild from scratch
docker-compose build --no-cache
docker-compose up -d
```

### Frontend Can't Connect to Backend
```bash
# Check NEXT_PUBLIC_API_URL in frontend/.env.local
# Should be: http://localhost:8000/api/v1

# Check CORS settings in backend/config.py
# allowed_origins should include: http://localhost:3000

# Restart frontend
cd frontend && npm run dev
```

## 📚 Next Steps

### For Users
1. Register an account at http://localhost:3000
2. Explore the dashboard
3. Chat with AI mentor
4. Generate study plan
5. Track your progress

### For Developers
1. Read [DEPLOYMENT.md](DEPLOYMENT.md) for detailed setup
2. Check [PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md) for tasks
3. Review [API documentation](http://localhost:8000/api/v1/docs)
4. Explore codebase structure
5. Run tests: `pytest --cov`

### For Contributors
1. Read [CONTRIBUTING.md](CONTRIBUTING.md)
2. Set up development environment
3. Create feature branch
4. Write tests
5. Submit pull request

## 🔧 Useful Commands

### Docker
```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f [service_name]

# Restart service
docker-compose restart [service_name]

# Rebuild service
docker-compose up -d --build [service_name]

# Execute command in container
docker-compose exec [service_name] [command]
```

### Database
```bash
# Create migration
docker-compose exec backend alembic revision --autogenerate -m "description"

# Apply migrations
docker-compose exec backend alembic upgrade head

# Rollback migration
docker-compose exec backend alembic downgrade -1

# View migration history
docker-compose exec backend alembic history
```

### Testing
```bash
# Run all tests
docker-compose exec backend pytest

# Run specific test file
docker-compose exec backend pytest tests/test_auth.py

# Run with coverage
docker-compose exec backend pytest --cov --cov-report=html

# View coverage report
open backend/htmlcov/index.html
```

## 📊 Default Credentials

### Test User (After Seeding)
- **Email**: test@example.com
- **Password**: testpass123

### Database (Docker)
- **Host**: localhost
- **Port**: 5432
- **Database**: examsensei
- **User**: examsensei
- **Password**: examsensei_password

### Redis (Docker)
- **Host**: localhost
- **Port**: 6379
- **Database**: 0

## 🎯 Quick Feature Test

### Test AI Chat
```bash
# Get user ID (from registration response or database)
USER_ID=1

# Chat with AI
curl -X POST http://localhost:8000/api/v1/users/$USER_ID/chat \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "How should I prepare for JEE Main?"}'
```

### Test Study Plan Generation
```bash
curl -X POST http://localhost:8000/api/v1/users/$USER_ID/study-plan \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "exam_code": "jee_main_2025",
    "days_available": 90
  }'
```

### Test Recommendations
```bash
curl http://localhost:8000/api/v1/users/$USER_ID/recommendations \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🆘 Getting Help

### Documentation
- **Full Deployment Guide**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **API Documentation**: http://localhost:8000/api/v1/docs
- **Production Checklist**: [PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md)

### Support Channels
- **GitHub Issues**: Report bugs and request features
- **Discord**: Join our community (link in README)
- **Email**: support@examsensei.com

### Common Issues
- Check [DEPLOYMENT.md#troubleshooting](DEPLOYMENT.md#troubleshooting)
- Search existing GitHub issues
- Ask in Discord community

## ✨ Success!

If you see:
- ✅ All Docker services running
- ✅ Health check returns 200 OK
- ✅ Can register and login
- ✅ Frontend loads at localhost:3000
- ✅ API docs at localhost:8000/api/v1/docs

**You're ready to start developing!** 🎉

---

**Need more details?** Check out:
- [README_PRODUCTION.md](README_PRODUCTION.md) - Full project overview
- [DEPLOYMENT.md](DEPLOYMENT.md) - Comprehensive deployment guide
- [PRODUCTION_TRANSFORMATION_SUMMARY.md](PRODUCTION_TRANSFORMATION_SUMMARY.md) - What was built

**Happy coding!** 🚀
