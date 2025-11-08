# 🔗 Backend-Frontend Integration Guide

## Overview

This guide explains how the ExamSensei backend and frontend are integrated and how to ensure they work together seamlessly.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                    │
│                   http://localhost:3000                  │
│  ┌──────────────────────────────────────────────────┐  │
│  │         API Client (lib/api.ts)                  │  │
│  │  - Token Management                              │  │
│  │  - Error Handling                                │  │
│  │  - Type Safety                                   │  │
│  └────────────────┬─────────────────────────────────┘  │
└────────────────────┼────────────────────────────────────┘
                     │
                     │ HTTP/REST API
                     │ JWT Authentication
                     │
┌────────────────────┴────────────────────────────────────┐
│                  Backend (FastAPI)                       │
│                http://localhost:8000                     │
│  ┌──────────────────────────────────────────────────┐  │
│  │         API Endpoints (/api/v1/*)                │  │
│  │  - Authentication                                │  │
│  │  - Exam Management                               │  │
│  │  - AI Features                                   │  │
│  │  - User Management                               │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## Configuration

### Frontend Environment Variables

**File**: `frontend/.env.local`
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

**Usage in Code**:
```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
```

### Backend Environment Variables

**File**: `backend/.env`
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/examsensei

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis
REDIS_URL=redis://localhost:6379/0

# Ollama
OLLAMA_URL=http://localhost:11434

# CORS
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Environment
ENVIRONMENT=development
```

---

## API Client Integration

### Location
`frontend/src/lib/api.ts`

### Key Features

#### 1. **Automatic Token Management**
```typescript
class APIClient {
  private getHeaders(): Record<string, string> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    const token = localStorage.getItem('access_token');
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    return headers;
  }
}
```

#### 2. **Error Handling**
```typescript
private async handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || error.message || 'Request failed');
  }
  return response.json();
}
```

#### 3. **Type Safety**
```typescript
export interface User {
  id: number;
  email: string;
  name: string;
  current_stage: string;
}

async getUser(userId: number): Promise<User> {
  return this.get<User>(`/users/${userId}`);
}
```

---

## Authentication Flow

### 1. **Registration**

**Frontend** (`auth/register/page.tsx`):
```typescript
const { register } = useAuth();
await register({
  email: 'user@example.com',
  password: 'password123',
  name: 'John Doe',
  education_level: 'class_12',
  state: 'Tamil Nadu'
});
```

**API Call**:
```
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "name": "John Doe",
  "education_level": "class_12",
  "state": "Tamil Nadu"
}
```

**Backend** (`backend/app_v2.py`):
```python
@app.post("/auth/register", status_code=201)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # Hash password
    hashed_password = get_password_hash(user_data.password)
    
    # Create user
    user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        name=user_data.name,
        ...
    )
    
    db.add(user)
    db.commit()
    return user
```

### 2. **Login**

**Frontend**:
```typescript
const { login } = useAuth();
await login('user@example.com', 'password123');
```

**API Call**:
```
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=password123
```

**Backend**:
```python
@app.post("/auth/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
```

**Token Storage**:
```typescript
localStorage.setItem('access_token', tokens.access_token);
localStorage.setItem('refresh_token', tokens.refresh_token);
```

### 3. **Protected Requests**

**Frontend**:
```typescript
const exams = await api.getExams();
```

**API Call**:
```
GET /api/v1/exams
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

**Backend**:
```python
@app.get("/exams")
async def get_exams(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    exams = db.query(Exam).all()
    return exams
```

---

## Data Flow Examples

### Example 1: Loading Dashboard

**1. Frontend Component** (`dashboard/page.tsx`):
```typescript
useEffect(() => {
  loadDashboardData();
}, [user]);

const loadDashboardData = async () => {
  const [examsData, recsData, gamData] = await Promise.all([
    api.getExams(),
    api.getRecommendations(user.id),
    api.getGamificationStatus(user.id),
  ]);
  
  setExams(examsData);
  setRecommendations(recsData);
  setGamification(gamData);
};
```

**2. API Client** (`lib/api.ts`):
```typescript
async getExams(): Promise<Exam[]> {
  return this.get<Exam[]>('/exams');
}

async getRecommendations(userId: number): Promise<any> {
  return this.get(`/users/${userId}/recommendations`);
}

async getGamificationStatus(userId: number): Promise<GamificationStatus> {
  return this.get<GamificationStatus>(`/users/${userId}/gamification`);
}
```

**3. Backend Endpoints** (`app_v2.py`):
```python
@app.get("/exams")
async def get_exams(db: Session = Depends(get_db)):
    return db.query(Exam).all()

@app.get("/users/{user_id}/recommendations")
async def get_recommendations(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    mentor = AdaptiveMentor(db)
    return mentor.get_personalized_recommendations(user_id)

@app.get("/users/{user_id}/gamification")
async def get_gamification(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(Gamification).filter_by(user_id=user_id).first()
```

### Example 2: AI Chat

**1. Frontend**:
```typescript
const handleChat = async (message: string) => {
  const response = await api.chat(user.id, message);
  setChatResponse(response.response);
};
```

**2. API Client**:
```typescript
async chat(userId: number, message: string): Promise<ChatResponse> {
  return this.post<ChatResponse>(`/users/${userId}/chat`, { message });
}
```

**3. Backend**:
```python
@app.post("/users/{user_id}/chat")
async def chat(
    user_id: int,
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    chatbot = ExamSenseiChatbot(db)
    response = await chatbot.process_message(user_id, chat_request.message)
    return response
```

---

## CORS Configuration

### Backend CORS Setup

**File**: `backend/app_v2.py`
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Production CORS

For production, update to specific domains:
```python
allow_origins=[
    "https://examsensei.com",
    "https://www.examsensei.com",
]
```

---

## Testing Integration

### 1. **Health Check**

```bash
# Run health check script
health_check.bat

# Or manually
curl http://localhost:8000/api/v1/health
curl http://localhost:3000
```

### 2. **API Testing**

```bash
# Test registration
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123","name":"Test User","education_level":"class_12","state":"Tamil Nadu"}'

# Test login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=test123"

# Test protected endpoint
curl http://localhost:8000/api/v1/exams \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 3. **Integration Test**

```bash
# Run integration test script
test_integration.bat
```

---

## Common Issues & Solutions

### Issue 1: CORS Errors

**Symptom**: "Access to fetch blocked by CORS policy"

**Solution**:
1. Check backend CORS configuration
2. Ensure frontend URL is in `allow_origins`
3. Restart backend server

### Issue 2: 401 Unauthorized

**Symptom**: API returns 401 for protected endpoints

**Solution**:
1. Check if token is stored: `localStorage.getItem('access_token')`
2. Verify token is being sent in headers
3. Check token expiration (30 minutes by default)
4. Re-login if token expired

### Issue 3: Connection Refused

**Symptom**: "Failed to fetch" or "Connection refused"

**Solution**:
1. Verify backend is running: `curl http://localhost:8000/api/v1/health`
2. Check correct port (8000 for backend, 3000 for frontend)
3. Ensure no firewall blocking

### Issue 4: Environment Variables Not Loading

**Symptom**: API calls go to wrong URL

**Solution**:
1. Create `frontend/.env.local` file
2. Add `NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1`
3. Restart frontend server

---

## Deployment Integration

### Docker Compose

All services are integrated in `docker-compose.yml`:

```yaml
services:
  backend:
    environment:
      DATABASE_URL: postgresql://...
      REDIS_URL: redis://redis:6379/0
    depends_on:
      - postgres
      - redis

  frontend:
    environment:
      NEXT_PUBLIC_API_URL: http://backend:8000/api/v1
    depends_on:
      - backend
```

### Production

For production deployment:

1. **Update Environment Variables**:
   - Backend: Use production database URL
   - Frontend: Use production API URL

2. **Enable HTTPS**:
   - Configure SSL certificates
   - Update CORS origins

3. **Use Nginx Reverse Proxy**:
   - Route `/api` to backend
   - Route `/` to frontend

---

## Monitoring Integration

### Health Endpoints

**Backend Health**:
```
GET /api/v1/health

Response:
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "production"
}
```

**Frontend Health**:
```
GET /

Response: 200 OK (renders page)
```

### Logging

**Backend Logs**:
- Location: `backend/logs/`
- Format: JSON structured logs
- Includes: Request/response, errors, user activity

**Frontend Logs**:
- Browser console
- Network tab for API calls

---

## Best Practices

### 1. **Error Handling**

Always handle API errors gracefully:
```typescript
try {
  const data = await api.getExams();
  setExams(data);
} catch (error) {
  console.error('Failed to load exams:', error);
  setError('Failed to load exams. Please try again.');
}
```

### 2. **Loading States**

Show loading indicators during API calls:
```typescript
const [loading, setLoading] = useState(false);

const loadData = async () => {
  setLoading(true);
  try {
    const data = await api.getData();
    setData(data);
  } finally {
    setLoading(false);
  }
};
```

### 3. **Token Refresh**

Implement token refresh for better UX:
```typescript
async refreshToken() {
  const refreshToken = localStorage.getItem('refresh_token');
  const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${refreshToken}` }
  });
  const { access_token } = await response.json();
  localStorage.setItem('access_token', access_token);
}
```

### 4. **Type Safety**

Always use TypeScript interfaces:
```typescript
interface Exam {
  id: number;
  name: string;
  code: string;
}

const exams: Exam[] = await api.getExams();
```

---

## Quick Reference

### Startup Commands

```bash
# Full stack (Docker)
docker-compose up -d

# Backend only
cd backend && uvicorn app_v2:app --reload

# Frontend only
cd frontend && npm run dev

# One-click start
start.bat
```

### Access URLs

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/api/v1/docs
- Health Check: http://localhost:8000/api/v1/health

### Environment Files

- Backend: `backend/.env`
- Frontend: `frontend/.env.local`

---

**Last Updated**: January 9, 2025  
**Version**: 1.0.0
