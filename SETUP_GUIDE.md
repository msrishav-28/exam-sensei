# 🚀 ExamSensei - Complete Setup Guide

## ⚡ Quick Start (5 Minutes)

### Step 1: Run the Setup Script
```bash
# Navigate to project directory
cd ExamSensei

# Run the all-in-one setup script
setup.bat

# Select: 1 (First Time Setup)
```

The script will automatically:
- ✅ Check Python and Node.js installation
- ✅ Create Python virtual environment
- ✅ Install all backend dependencies (40+ packages)
- ✅ Initialize database with seed data
- ✅ Install all frontend dependencies
- ✅ Create necessary configuration files
- ✅ Set up logging directories
- ✅ Verify installation

### Step 2: Start the Application
```bash
# In the same menu, after setup completes
# Press any key, then select: 2 (Start Application)

# Choose: 1 (Full Stack)
```

Two command windows will open:
- 🔵 Backend Server (Port 8000)
- 🟢 Frontend Server (Port 3000)

### Step 3: Access the Application
Open your browser:
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/api/v1/docs
- **Health Check**: http://localhost:8000/api/v1/health

---

## 📋 Prerequisites

### Required
- **Python 3.11+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** - [Download](https://nodejs.org/)
- **Git** - [Download](https://git-scm.com/)

### Optional (Recommended)
- **Redis** - For caching ([Download](https://redis.io/download))
- **Ollama** - For AI chatbot ([Download](https://ollama.ai/))
- **Docker** - For containerized deployment ([Download](https://www.docker.com/))

---

## 🎯 Setup Menu Options

The `setup.bat` script provides these options:

### 1️⃣ First Time Setup
- Installs all dependencies
- Initializes database
- Creates configuration files
- Sets up project structure

### 2️⃣ Start Application
Choose from:
- **Full Stack** (Backend + Frontend)
- **Backend Only**
- **Frontend Only**
- **Docker Compose**

### 3️⃣ Health Check
Verifies:
- Backend is running
- Frontend is accessible
- Database exists
- Optional services (Redis, Ollama)

### 4️⃣ Update Dependencies
Update:
- Backend Python packages
- Frontend Node packages
- Both at once

### 5️⃣ Run Tests
Executes the test suite with coverage report

### 6️⃣ Cleanup
Stops all running services and cleans up processes

### 7️⃣ Docker Setup
Builds and starts Docker containers

---

## 🛠️ Manual Setup (Alternative)

If you prefer manual setup:

### Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Initialize database
alembic upgrade head
python seed_data.py

# Create .env file
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac

# Start server
uvicorn app_v2:app --reload
```

### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install --legacy-peer-deps

# Create environment file
copy .env.example .env.local  # Windows
cp .env.example .env.local    # Linux/Mac

# Start development server
npm run dev
```

---

## 🔧 Configuration

### Backend Configuration (.env)
```env
# Database
DATABASE_URL=sqlite:///./examsensei.db

# Security
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Optional Services
REDIS_URL=redis://localhost:6379/0
OLLAMA_URL=http://localhost:11434

# Environment
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### Frontend Configuration (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

---

## 🐳 Docker Setup

### Option 1: Using Setup Script
```bash
setup.bat
# Select: 7 (Docker Setup)
```

### Option 2: Manual Docker
```bash
# Build and start containers
docker-compose up -d --build

# Initialize database
docker-compose exec backend alembic upgrade head
docker-compose exec backend python seed_data.py

# View logs
docker-compose logs -f

# Stop containers
docker-compose down
```

---

## ✅ Verification Steps

### 1. Check Backend
```bash
# Visit API documentation
http://localhost:8000/api/v1/docs

# Test health endpoint
curl http://localhost:8000/api/v1/health
```

Expected Response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development",
  "timestamp": "2025-01-09T..."
}
```

### 2. Check Frontend
- Visit http://localhost:3000
- You should see the landing page
- Try registering a new account
- Login and access dashboard

### 3. Check Database
```bash
cd backend
# SQLite browser or:
python
>>> from database import SessionLocal
>>> from models import Exam
>>> db = SessionLocal()
>>> exams = db.query(Exam).all()
>>> print(f"Found {len(exams)} exams")
>>> exit()
```

---

## 🐛 Troubleshooting

### Issue: Port Already in Use

**Error**: Address already in use: Port 8000/3000

**Solution**:
```bash
# Kill process on port 8000 (Backend)
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Kill process on port 3000 (Frontend)
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

### Issue: Module Not Found

**Error**: `ModuleNotFoundError: No module named 'xxx'`

**Solution**:
```bash
cd backend
venv\Scripts\activate
pip install -r requirements.txt --force-reinstall
```

### Issue: Database Locked

**Error**: `database is locked`

**Solution**:
```bash
# Close all running backend instances
# Delete database and recreate
cd backend
del examsensei.db
alembic upgrade head
python seed_data.py
```

### Issue: Frontend Dependencies Error

**Error**: Peer dependency conflicts

**Solution**:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps --force
```

### Issue: Permission Denied

**Error**: Permission errors during setup

**Solution**:
```bash
# Run command prompt as Administrator
# Right-click -> Run as Administrator
# Then run setup.bat
```

---

## 📊 Project Status Check

After setup, verify everything is working:

```bash
# Use the health check option
setup.bat
# Select: 3 (Health Check)
```

Expected Output:
```
✓ Backend is HEALTHY
✓ Frontend is HEALTHY
✓ Database file exists
⚠ Redis not running (optional)
⚠ Ollama not running (optional)
```

---

## 🔐 First Login

### Default Test User
After seeding the database, you can register a new user or use test data:

1. **Register**: http://localhost:3000/auth/register
2. Fill in the form:
   - Email: your@email.com
   - Name: Your Name
   - Education Level: Select your level
   - State: Select your state
   - Password: Create a secure password
3. **Login**: Redirected to dashboard automatically

---

## 🎓 Next Steps

Once setup is complete:

1. **Explore the Dashboard**
   - View available exams
   - Generate study plans
   - Chat with AI mentor

2. **Test API Features**
   - Visit http://localhost:8000/api/v1/docs
   - Try the interactive API documentation
   - Test endpoints with authentication

3. **Configure Scrapers**
   - Run `python multi_scraper.py` to fetch live data
   - Check logs in `backend/logs/`

4. **Optional Services**
   - Install Redis for caching
   - Install Ollama for AI features
   - Configure email for notifications

---

## 📚 Additional Resources

- **Full Documentation**: [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
- **API Guide**: http://localhost:8000/api/v1/docs
- **Architecture**: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **Deployment**: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)
- **Contributing**: [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)

---

## 🆘 Getting Help

### Common Commands Reference

```bash
# Start everything
setup.bat -> Option 2 -> Option 1

# Stop everything
setup.bat -> Option 6

# Update dependencies
setup.bat -> Option 4

# Run tests
setup.bat -> Option 5

# Health check
setup.bat -> Option 3
```

### Need More Help?

1. Check `backend/logs/examsensei.log` for errors
2. Review this guide carefully
3. Check `PROJECT_STRUCTURE.md` for architecture details
4. Open a GitHub issue with:
   - Error message
   - Steps to reproduce
   - Your environment (OS, Python version, Node version)

---

## ✨ Success Indicators

You're ready to go when:

- ✅ Backend responds at http://localhost:8000
- ✅ Frontend loads at http://localhost:3000
- ✅ You can register and login
- ✅ API docs are accessible
- ✅ Database has exam data
- ✅ No errors in console/logs

---

**🎉 Congratulations! ExamSensei is now running on your machine.**

**Ready to ace your exams? Let's get started! 🚀**

---

*Setup Time: ~5 minutes | Support: GitHub Issues | License: MIT*
