# 🏗️ ExamSensei Architecture Guide

## System Overview

ExamSensei is built as a modern, scalable, microservices-inspired architecture with clear separation of concerns.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Client Layer                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Browser │  │  Mobile  │  │   PWA    │  │  Desktop │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼─────────────┼─────────────┼──────────┘
        │             │             │             │
        └─────────────┴─────────────┴─────────────┘
                          │
┌─────────────────────────┴────────────────────────────────────┐
│                   Presentation Layer                          │
│                   Next.js 14 Frontend                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   Auth   │  │Dashboard │  │   Chat   │  │  Profile │   │
│  │  Pages   │  │   Page   │  │Interface │  │   Page   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         TypeScript API Client (lib/api.ts)           │   │
│  │  - Token Management  - Error Handling  - Types      │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────────┬─────────────────────────────────────┘
                         │ REST API (JSON)
                         │ JWT Authentication
┌────────────────────────┴─────────────────────────────────────┐
│                    Application Layer                          │
│                   FastAPI Backend (Python)                    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              API Gateway (app_v2.py)                 │   │
│  │  - Authentication  - Rate Limiting  - CORS          │   │
│  │  - Request Logging  - Error Handling                │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   Auth   │  │    AI    │  │ Chatbot  │  │Lifecycle │   │
│  │  Module  │  │  Models  │  │  Module  │  │ Machine  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                                                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Scrapers │  │  Cache   │  │  Logger  │  │Exceptions│   │
│  │  Module  │  │  Module  │  │  Module  │  │  Module  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└────────────────────────┬─────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────┴───────┐ ┌──────┴──────┐ ┌──────┴──────┐
│  PostgreSQL   │ │    Redis    │ │   Ollama    │
│   Database    │ │    Cache    │ │  Local LLM  │
│               │ │             │ │             │
│ - Users       │ │ - Sessions  │ │ - Chat      │
│ - Exams       │ │ - Cache     │ │ - NLP       │
│ - Topics      │ │ - Rate Lim  │ │ - Intent    │
└───────────────┘ └─────────────┘ └─────────────┘
```

## Component Details

### 1. Frontend Layer (Next.js 14)

**Technology Stack:**
- Next.js 14 with App Router
- React 19
- TypeScript
- Tailwind CSS
- PWA Support

**Key Components:**

#### Authentication Context (`contexts/AuthContext.tsx`)
- Manages user authentication state
- Handles login/logout/register
- Provides protected route wrapper
- Token management via localStorage

#### Pages
- `/` - Landing page with features
- `/auth/login` - Login page
- `/auth/register` - Registration page
- `/dashboard` - Main dashboard (protected)

#### API Client (`lib/api.ts`)
- Type-safe API calls
- Automatic JWT token injection
- Error handling
- Request/response interceptors

### 2. Backend Layer (FastAPI)

**Technology Stack:**
- FastAPI (Python 3.11)
- SQLAlchemy ORM
- Pydantic for validation
- Alembic for migrations

**Core Modules:**

#### API Gateway (`app_v2.py`)
```python
- Lifespan management
- Middleware configuration
- Route definitions
- Global exception handling
- Request logging
```

#### Authentication Module (`auth.py`)
```python
- JWT token generation/validation
- Password hashing (bcrypt)
- User registration/login
- OAuth2 password flow
- Role-based access control
```

#### AI Models Module (`ai_models.py`)
```python
- CareerRecommender: Career path suggestions
- TopicPrioritizer: Study plan generation
- ExamClashDetector: Date conflict detection
- AdaptiveMentor: Orchestrates AI features
```

#### Chatbot Module (`chatbot.py`)
```python
- ExamSenseiChatbot: Main chatbot class
- Intent analysis
- Entity extraction
- Ollama integration
- Conversation history
```

#### Lifecycle Module (`lifecycle.py`)
```python
- LifecycleStateMachine: Stage management
- Automatic progression logic
- Milestone generation
- Exam recommendations
- Daily checks
```

#### Scraper Module (`multi_scraper.py`)
```python
- MultiSourceScraper: Orchestrator
- NTASpider: JEE, NEET scraping
- UPSCSpider: UPSC exam scraping
- SSCSpider: SSC exam scraping
- IBPSSpider: Banking exam scraping
```

#### Cache Module (`cache.py`)
```python
- CacheManager: Redis wrapper
- @cached decorator
- Rate limiting
- Cache invalidation
```

#### Logger Module (`logger.py`)
```python
- Structured logging
- JSON formatting
- Log rotation
- Error tracking
```

### 3. Data Layer

#### PostgreSQL Database

**Schema:**
```sql
Users
- id, email, hashed_password
- name, education_level, state
- current_stage, career_paths
- preparation_profile
- gamification data

Exams
- id, name, code, body
- exam_type, important_dates
- eligibility, fees
- syllabus, exam_pattern

Topics
- id, exam_id, subject, name
- weightage_history (JSON)
- difficulty_distribution
- marks_per_hour
- avg_questions

Bookmarks, Notifications, UserActivity
Recommendations, StudyPlans
Conversations, Gamification
```

#### Redis Cache

**Usage:**
```
- Session storage
- API response caching
- Rate limiting counters
- Temporary data
```

#### Ollama (Local LLM)

**Purpose:**
- Natural language understanding
- Intent classification
- Entity extraction
- Response generation
- Privacy-focused (runs locally)

## Data Flow

### 1. User Registration Flow

```
User → Frontend → API Client → Backend
                                  ↓
                          Validate Input
                                  ↓
                          Hash Password
                                  ↓
                          Save to DB
                                  ↓
                          Generate JWT
                                  ↓
Frontend ← API Client ← Backend
```

### 2. AI Chat Flow

```
User Message → Frontend → API Client → Backend
                                         ↓
                                   Auth Check
                                         ↓
                                   Get User Context
                                         ↓
                                   Analyze Intent
                                         ↓
                                   Query Ollama
                                         ↓
                                   Generate Response
                                         ↓
                                   Save Conversation
                                         ↓
Frontend ← API Client ← Backend
```

### 3. Study Plan Generation Flow

```
User Request → Frontend → API Client → Backend
                                         ↓
                                   Auth Check
                                         ↓
                                   Get Exam Topics
                                         ↓
                                   Get User Profile
                                         ↓
                                   Calculate Priorities
                                         ↓
                                   Generate Timeline
                                         ↓
                                   Save Study Plan
                                         ↓
Frontend ← API Client ← Backend
```

### 4. Scraping Flow

```
Cron Job → Scraper Module → Target Website
                ↓
          Parse HTML
                ↓
          Extract Data
                ↓
          Validate Data
                ↓
          Update Database
                ↓
          Invalidate Cache
                ↓
          Generate Notifications
```

## Security Architecture

### Authentication Flow

```
1. User Login
   ↓
2. Verify Credentials
   ↓
3. Generate Access Token (30 min)
   ↓
4. Generate Refresh Token (7 days)
   ↓
5. Return Tokens
   ↓
6. Store in LocalStorage
   ↓
7. Include in API Requests
   ↓
8. Validate on Backend
```

### Security Layers

1. **Transport Layer**: HTTPS/TLS
2. **Authentication**: JWT tokens
3. **Authorization**: Role-based access
4. **Input Validation**: Pydantic models
5. **Rate Limiting**: Redis-based
6. **CORS**: Configured origins
7. **SQL Injection**: ORM prevents
8. **XSS**: Content Security Policy

## Scalability Considerations

### Horizontal Scaling

```
Load Balancer (Nginx)
        ↓
┌───────┼───────┐
│       │       │
Backend Backend Backend
│       │       │
└───────┼───────┘
        ↓
   PostgreSQL
   (Read Replicas)
```

### Caching Strategy

1. **L1 Cache**: Redis (frequently accessed data)
2. **L2 Cache**: CDN (static assets)
3. **Database**: Query optimization, indexing

### Performance Optimizations

- **Database**: Connection pooling, indexes
- **API**: Response compression, pagination
- **Frontend**: Code splitting, lazy loading
- **Caching**: Redis for hot data
- **CDN**: Static asset delivery

## Monitoring & Observability

### Logging

```
Application Logs → Logger Module → Log Files
                                      ↓
                                   Rotation
                                      ↓
                                   Sentry
```

### Metrics

- API response times
- Error rates
- Cache hit rates
- Database query times
- User activity

### Health Checks

```
/api/v1/health
- Database connection
- Redis connection
- Ollama availability
- System resources
```

## Deployment Architecture

### Development

```
Docker Compose
├── Backend (FastAPI)
├── Frontend (Next.js)
├── PostgreSQL
├── Redis
├── Ollama
└── Nginx
```

### Production

```
Cloud Provider
├── Container Service (Backend)
├── Static Hosting (Frontend)
├── Managed PostgreSQL
├── Managed Redis
├── CDN
└── Load Balancer
```

## Technology Choices Rationale

### Why FastAPI?
- Modern async support
- Automatic API documentation
- Type hints and validation
- High performance
- Easy to test

### Why Next.js?
- Server-side rendering
- App Router for better UX
- Built-in optimization
- TypeScript support
- PWA capabilities

### Why PostgreSQL?
- ACID compliance
- JSON support
- Mature and reliable
- Excellent performance
- Rich ecosystem

### Why Redis?
- In-memory speed
- Simple key-value store
- Built-in expiration
- Pub/sub support
- Rate limiting

### Why Ollama?
- Privacy-focused (local)
- No API costs
- Fast inference
- Easy integration
- Multiple models

## Future Architecture Enhancements

### Phase 2
- [ ] Microservices separation
- [ ] Message queue (RabbitMQ/Kafka)
- [ ] Elasticsearch for search
- [ ] GraphQL API option
- [ ] WebSocket for real-time

### Phase 3
- [ ] Kubernetes orchestration
- [ ] Service mesh (Istio)
- [ ] Distributed tracing
- [ ] Advanced monitoring
- [ ] Multi-region deployment

---

**Last Updated**: January 8, 2025  
**Version**: 1.0.0
