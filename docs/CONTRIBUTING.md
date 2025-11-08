# 🤝 Contributing to ExamSensei

Thank you for your interest in contributing to ExamSensei! This document provides guidelines and instructions for contributing.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Setup](#development-setup)
4. [Making Changes](#making-changes)
5. [Testing](#testing)
6. [Submitting Changes](#submitting-changes)
7. [Code Style](#code-style)
8. [Project Structure](#project-structure)

## Code of Conduct

### Our Pledge

We pledge to make participation in our project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards

**Positive behavior includes:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what is best for the community

**Unacceptable behavior includes:**
- Trolling, insulting/derogatory comments, and personal attacks
- Public or private harassment
- Publishing others' private information without permission
- Other conduct which could reasonably be considered inappropriate

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose
- Git
- Ollama (for AI features)

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
```bash
git clone https://github.com/YOUR_USERNAME/ExamSensei.git
cd ExamSensei
```

3. Add upstream remote:
```bash
git remote add upstream https://github.com/ORIGINAL_OWNER/ExamSensei.git
```

## Development Setup

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install ALL dependencies (single command - 40 packages!)
pip install -r requirements.txt

# Note: requirements.txt now includes ALL packages:
# - Core framework (FastAPI, Uvicorn, Pydantic)
# - Database (SQLAlchemy, Alembic)
# - Auth (python-jose, passlib)
# - Testing (pytest, pytest-cov)
# - Code quality (Pygments)
# - All transitive dependencies

# Create .env file
cp .env.example .env
# Edit .env with your configuration

# Run migrations
alembic upgrade head

# Seed data
python seed_data.py

# Start development server
uvicorn app_v2:app --reload
```

### Frontend Setup

```bash
cd frontend

# Install ALL dependencies (single command with React 19 support!)
npm install --legacy-peer-deps

# Note: package.json now includes ALL packages:
# - Core (Next.js, React 19)
# - UI (framer-motion, lucide-react, tailwindcss)
# - Charts (recharts)
# - Calendar (@fullcalendar/*)
# - Validation (zod)
# - All TypeScript types

# Important: Always use --legacy-peer-deps flag for React 19 compatibility

# Create .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1" > .env.local

# Start development server
npm run dev
```

### Docker Setup (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Making Changes

### Branch Naming Convention

- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `test/` - Test additions/changes
- `chore/` - Maintenance tasks

Examples:
- `feature/add-mock-test-module`
- `fix/authentication-token-expiry`
- `docs/update-api-documentation`

### Workflow

1. **Create a branch**:
```bash
git checkout -b feature/your-feature-name
```

2. **Make your changes**:
   - Write clean, readable code
   - Follow existing code style
   - Add comments for complex logic
   - Update documentation if needed

3. **Test your changes**:
```bash
# Backend tests
cd backend
pytest --cov

# Frontend tests
cd frontend
npm test
```

4. **Commit your changes**:
```bash
git add .
git commit -m "feat: add new feature"
```

### Commit Message Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Test additions/changes
- `chore`: Maintenance tasks
- `perf`: Performance improvements

**Examples:**
```
feat(auth): add password reset functionality

Implemented password reset flow with email verification.
Users can now request password reset links via email.

Closes #123
```

```
fix(api): resolve race condition in cache invalidation

Fixed issue where concurrent requests could cause stale cache data.
Added proper locking mechanism using Redis.

Fixes #456
```

## Testing

### Backend Testing

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov --cov-report=html

# Run specific test file
pytest tests/test_auth.py -v

# Run specific test
pytest tests/test_auth.py::test_login_success -v
```

### Frontend Testing

```bash
cd frontend

# Run tests
npm test

# Run with coverage
npm test -- --coverage

# Run in watch mode
npm test -- --watch
```

### Writing Tests

**Backend (pytest):**
```python
def test_user_registration(client):
    """Test user registration endpoint"""
    response = client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "password": "securepass123",
        "name": "Test User",
        "education_level": "class_12",
        "state": "Tamil Nadu"
    })
    
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"
```

**Frontend (Jest/React Testing Library):**
```typescript
test('renders login form', () => {
  render(<LoginPage />);
  expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
  expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
});
```

## Submitting Changes

### Pull Request Process

1. **Update your branch**:
```bash
git fetch upstream
git rebase upstream/main
```

2. **Push to your fork**:
```bash
git push origin feature/your-feature-name
```

3. **Create Pull Request**:
   - Go to GitHub and create a PR
   - Fill in the PR template
   - Link related issues
   - Request review

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] New tests added
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings generated
```

### Review Process

1. **Automated Checks**:
   - CI/CD pipeline runs tests
   - Code coverage checked
   - Linting verified

2. **Code Review**:
   - At least one maintainer review required
   - Address feedback promptly
   - Make requested changes

3. **Merge**:
   - Squash and merge (default)
   - Maintainer merges after approval

## Code Style

### Python (Backend)

**Formatting:**
```bash
# Format code with Black
black .

# Check with Flake8
flake8 .

# Type checking with MyPy
mypy .
```

**Style Guidelines:**
- Follow PEP 8
- Use type hints
- Maximum line length: 100 characters
- Use docstrings for functions/classes
- Prefer f-strings for formatting

**Example:**
```python
def calculate_priority_score(
    topic: Topic,
    user_strengths: List[str],
    user_weaknesses: List[str],
    days_available: int
) -> float:
    """
    Calculate priority score for a topic.
    
    Args:
        topic: Topic object with weightage data
        user_strengths: List of user's strong topics
        user_weaknesses: List of user's weak topics
        days_available: Days available for preparation
    
    Returns:
        Priority score between 0 and 1
    """
    # Implementation
    pass
```

### TypeScript (Frontend)

**Formatting:**
```bash
# Format with Prettier
npm run format

# Lint with ESLint
npm run lint
```

**Style Guidelines:**
- Use TypeScript strict mode
- Prefer functional components
- Use hooks for state management
- Export types/interfaces
- Use meaningful variable names

**Example:**
```typescript
interface User {
  id: number;
  email: string;
  name: string;
  currentStage: string;
}

export function UserProfile({ user }: { user: User }) {
  const [isEditing, setIsEditing] = useState(false);
  
  return (
    <div className="user-profile">
      {/* Component JSX */}
    </div>
  );
}
```

## Project Structure

```
ExamSensei/
├── backend/
│   ├── app_v2.py          # Main API application
│   ├── auth.py            # Authentication module
│   ├── ai_models.py       # AI algorithms
│   ├── chatbot.py         # Chatbot module
│   ├── lifecycle.py       # Lifecycle state machine
│   ├── multi_scraper.py   # Web scrapers
│   ├── cache.py           # Redis caching
│   ├── logger.py          # Logging configuration
│   ├── models.py          # Database models
│   ├── config.py          # Configuration
│   ├── tests/             # Test files
│   └── alembic/           # Database migrations
├── frontend/
│   ├── src/
│   │   ├── app/           # Next.js pages
│   │   ├── contexts/      # React contexts
│   │   ├── lib/           # Utilities
│   │   └── components/    # React components
│   └── public/            # Static files
├── docs/                  # Documentation
└── docker-compose.yml     # Docker configuration
```

## Areas for Contribution

### High Priority
- [ ] Additional exam scrapers (state boards)
- [ ] Mobile app (React Native)
- [ ] Video lecture integration
- [ ] Mock test platform
- [ ] Advanced analytics dashboard

### Medium Priority
- [ ] Email notifications
- [ ] SMS alerts
- [ ] Telegram bot
- [ ] Performance optimizations
- [ ] UI/UX improvements

### Good First Issues
- [ ] Documentation improvements
- [ ] Test coverage increase
- [ ] Bug fixes
- [ ] Code refactoring
- [ ] Translation support

## Getting Help

- **Documentation**: Check [docs/](../docs/)
- **Issues**: Search existing issues
- **Discussions**: Use GitHub Discussions
- **Email**: support@examsensei.com

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in documentation

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to ExamSensei!** 🎓

Together, we're helping millions of students succeed in their competitive exams.
