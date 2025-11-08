# 📚 ExamSensei API Documentation

## Base URL

```
Development: http://localhost:8000/api/v1
Production: https://api.examsensei.com/api/v1
```

## Authentication

All protected endpoints require JWT authentication.

### Headers
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

---

## Endpoints

### Authentication

#### POST /auth/register
Register a new user.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepass123",
  "name": "John Doe",
  "education_level": "class_12",
  "state": "Tamil Nadu",
  "category": "general",
  "budget": "medium"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "John Doe",
  "current_stage": "class_12",
  "is_verified": false
}
```

#### POST /auth/login
Login and get access tokens.

**Request:**
```
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=securepass123
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

#### GET /auth/me
Get current user information.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "John Doe",
  "current_stage": "class_12",
  "career_paths": ["engineering"],
  "active_exams": ["jee_main_2025"],
  "is_verified": false
}
```

---

### Exams

#### GET /exams
Get list of exams.

**Query Parameters:**
- `skip` (int): Offset for pagination (default: 0)
- `limit` (int): Number of results (default: 100)
- `exam_type` (string): Filter by type (optional)

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "name": "JEE Main 2025",
    "code": "jee_main_2025",
    "body": "NTA",
    "exam_type": "engineering_entrance",
    "important_dates": {
      "exam_dates": ["2025-01-24", "2025-01-25"],
      "application_start": "2024-12-01",
      "application_end": "2024-12-31",
      "result": "2025-02-12"
    }
  }
]
```

#### GET /exams/{exam_id}
Get specific exam details.

**Response:** `200 OK`
```json
{
  "id": 1,
  "name": "JEE Main 2025",
  "code": "jee_main_2025",
  "body": "NTA",
  "exam_type": "engineering_entrance",
  "important_dates": {...},
  "subjects": ["physics", "chemistry", "mathematics"],
  "eligibility": {...},
  "fees": {...},
  "syllabus": {...}
}
```

---

### AI Features (Protected)

#### POST /users/{user_id}/chat
Chat with AI mentor.

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "message": "How should I prepare for JEE Main Physics?",
  "session_id": "optional-session-id"
}
```

**Response:** `200 OK`
```json
{
  "response": "For JEE Main Physics, focus on...",
  "intent": "study_guidance",
  "confidence": 0.95,
  "suggested_actions": [
    "Generate study plan",
    "View topic priorities"
  ],
  "session_id": "abc123"
}
```

#### GET /users/{user_id}/recommendations
Get personalized recommendations.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "user_stage": "class_12",
  "career_paths": ["engineering"],
  "recommendations": [
    {
      "type": "exam",
      "exam": "JEE Main 2025",
      "score": 0.95,
      "reasoning": "Based on your profile and preparation stage"
    }
  ],
  "next_actions": [
    "Start JEE Main preparation",
    "Generate study plan"
  ]
}
```

#### POST /users/{user_id}/study-plan
Generate personalized study plan.

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "exam_code": "jee_main_2025",
  "days_available": 90
}
```

**Response:** `200 OK`
```json
{
  "exam_code": "jee_main_2025",
  "total_days": 90,
  "prioritized_topics": [
    {
      "topic": {
        "name": "Mechanics",
        "subject": "Physics"
      },
      "priority_score": 0.95,
      "estimated_days": 15,
      "difficulty": "medium",
      "weightage": 25
    }
  ],
  "weekly_plan": {...},
  "success_probability": 0.78
}
```

#### GET /users/{user_id}/gamification
Get gamification status.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "level": 5,
  "xp_points": 1250,
  "streak_days": 7,
  "achievements": [
    "first_login",
    "week_streak",
    "study_plan_completed"
  ]
}
```

---

### User Management (Protected)

#### GET /users/{user_id}
Get user profile.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "John Doe",
  "education_level": "class_12",
  "state": "Tamil Nadu",
  "current_stage": "class_12",
  "career_paths": ["engineering"],
  "active_exams": ["jee_main_2025"]
}
```

#### PUT /users/{user_id}/profile
Update user profile.

**Headers:** `Authorization: Bearer <token>`

**Request:**
```json
{
  "strengths": ["mathematics", "physics"],
  "weaknesses": ["chemistry"],
  "study_hours_per_day": 6
}
```

**Response:** `200 OK`
```json
{
  "message": "Profile updated successfully"
}
```

---

### Health & Status

#### GET /health
Health check endpoint (public).

**Response:** `200 OK`
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "production",
  "timestamp": "2025-01-08T18:30:00Z"
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "message": "Validation error",
  "details": {
    "field": "email",
    "error": "Invalid email format"
  }
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication required"
}
```

### 403 Forbidden
```json
{
  "message": "Access forbidden",
  "details": {}
}
```

### 404 Not Found
```json
{
  "message": "Resource not found",
  "details": {}
}
```

### 429 Too Many Requests
```json
{
  "detail": "Rate limit exceeded. Please try again later."
}
```

### 500 Internal Server Error
```json
{
  "message": "Internal server error",
  "details": {}
}
```

---

## Rate Limiting

- **Per Minute**: 60 requests
- **Per Hour**: 1000 requests

Rate limit headers:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1641234567
```

---

## Pagination

For list endpoints:
```
GET /exams?skip=0&limit=20
```

Response includes:
```json
{
  "items": [...],
  "total": 100,
  "skip": 0,
  "limit": 20
}
```

---

## Interactive Documentation

Visit the interactive API documentation:
- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc

---

**Last Updated**: January 8, 2025  
**Version**: 1.0.0
