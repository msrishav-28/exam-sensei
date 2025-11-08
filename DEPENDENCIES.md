# 📦 ExamSensei Dependencies

## Overview

This document details all dependencies used in ExamSensei, their versions, purposes, and update procedures.

---

## 🐍 Backend Dependencies (Python)

### Core Framework
| Package | Version | Purpose |
|---------|---------|---------|
| **fastapi** | 0.109.0 | Modern web framework for building APIs |
| **uvicorn** | 0.27.0 | ASGI server for FastAPI |
| **pydantic** | 2.6.0 | Data validation using Python type hints |
| **pydantic-settings** | 2.1.0 | Settings management with Pydantic |
| **python-multipart** | 0.0.6 | Form data parsing |

### Database
| Package | Version | Purpose |
|---------|---------|---------|
| **sqlalchemy** | 2.0.25 | SQL toolkit and ORM |
| **alembic** | 1.13.1 | Database migration tool |
| **psycopg2-binary** | 2.9.9 | PostgreSQL adapter |

### Authentication & Security
| Package | Version | Purpose |
|---------|---------|---------|
| **python-jose** | 3.3.0 | JWT token creation and validation |
| **passlib** | 1.7.4 | Password hashing (bcrypt) |
| **python-dotenv** | 1.0.1 | Environment variable management |

### HTTP & API
| Package | Version | Purpose |
|---------|---------|---------|
| **httpx** | 0.26.0 | Async HTTP client |
| **requests** | 2.31.0 | HTTP library |

### Web Scraping
| Package | Version | Purpose |
|---------|---------|---------|
| **scrapy** | 2.11.0 | Web scraping framework |
| **beautifulsoup4** | 4.12.3 | HTML/XML parsing |
| **lxml** | 5.1.0 | XML/HTML processing |

### Caching & Rate Limiting
| Package | Version | Purpose |
|---------|---------|---------|
| **redis** | 5.0.1 | Redis client for caching |
| **slowapi** | 0.1.9 | Rate limiting for FastAPI |

### Monitoring & Logging
| Package | Version | Purpose |
|---------|---------|---------|
| **sentry-sdk** | 1.40.0 | Error tracking and monitoring |

### Email
| Package | Version | Purpose |
|---------|---------|---------|
| **aiosmtplib** | 3.0.1 | Async SMTP client |
| **email-validator** | 2.1.0.post1 | Email validation |

### Testing
| Package | Version | Purpose |
|---------|---------|---------|
| **pytest** | 7.4.4 | Testing framework |
| **pytest-asyncio** | 0.23.3 | Async test support |
| **pytest-cov** | 4.1.0 | Code coverage |
| **faker** | 22.6.0 | Fake data generation |

### Code Quality
| Package | Version | Purpose |
|---------|---------|---------|
| **black** | 24.1.1 | Code formatter |
| **flake8** | 7.0.0 | Linting |
| **mypy** | 1.8.0 | Type checking |
| **pylint** | 3.0.3 | Code analysis |

### Utilities
| Package | Version | Purpose |
|---------|---------|---------|
| **python-dateutil** | 2.8.2 | Date/time utilities |
| **pytz** | 2024.1 | Timezone support |

---

## ⚛️ Frontend Dependencies (Node.js)

### Core Framework
| Package | Version | Purpose |
|---------|---------|---------|
| **next** | 15.1.3 | React framework for production |
| **react** | 19.0.0 | UI library |
| **react-dom** | 19.0.0 | React DOM rendering |

### UI Components & Styling
| Package | Version | Purpose |
|---------|---------|---------|
| **tailwindcss** | 4.0.0 | Utility-first CSS framework |
| **framer-motion** | 11.0.3 | Animation library |
| **lucide-react** | 0.344.0 | Icon library |

### Calendar & Charts
| Package | Version | Purpose |
|---------|---------|---------|
| **@fullcalendar/core** | 6.1.15 | Calendar core |
| **@fullcalendar/daygrid** | 6.1.15 | Day grid view |
| **@fullcalendar/react** | 6.1.15 | React integration |
| **@fullcalendar/timegrid** | 6.1.15 | Time grid view |
| **recharts** | 2.12.0 | Chart library |

### Validation
| Package | Version | Purpose |
|---------|---------|---------|
| **zod** | 3.22.4 | TypeScript-first schema validation |

### Development Tools
| Package | Version | Purpose |
|---------|---------|---------|
| **typescript** | 5.3.3 | TypeScript compiler |
| **@types/node** | 20.11.16 | Node.js type definitions |
| **@types/react** | 19.0.0 | React type definitions |
| **@types/react-dom** | 19.0.0 | React DOM type definitions |
| **eslint** | 9.0.0 | JavaScript linter |
| **eslint-config-next** | 15.1.3 | Next.js ESLint config |
| **postcss** | 8.4.35 | CSS transformations |
| **autoprefixer** | 10.4.17 | CSS vendor prefixing |

---

## 🔄 Update Procedures

### Quick Update (Recommended)
```bash
# Run the update script
update_dependencies.bat

# Choose option:
# 1. Backend Only
# 2. Frontend Only
# 3. Both (Recommended)
```

### Manual Backend Update
```bash
cd backend

# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Upgrade pip
python -m pip install --upgrade pip

# Update all packages
pip install -r requirements.txt --upgrade

# Verify
pip list
```

### Manual Frontend Update
```bash
cd frontend

# Remove old dependencies
rm -rf node_modules package-lock.json

# Install fresh
npm install

# Verify
npm list --depth=0
```

---

## 🔍 Version Compatibility

### Python Version
- **Required**: Python 3.11+
- **Recommended**: Python 3.11.7
- **Tested**: Python 3.11.7, 3.12.1

### Node.js Version
- **Required**: Node.js 18+
- **Recommended**: Node.js 20.11.0 LTS
- **Tested**: Node.js 20.11.0, 21.6.0

### Database Versions
- **PostgreSQL**: 15+
- **Redis**: 7+

---

## 📊 Dependency Updates

### Recent Updates (January 2025)

#### Backend (40 packages total)
**Core Updates:**
- ✅ FastAPI: 0.104.1 (Production stable)
- ✅ Uvicorn: 0.24.0 (ASGI server)
- ✅ Pydantic: 2.5.0 (Data validation)
- ✅ SQLAlchemy: 2.0.25 (ORM)
- ✅ Alembic: 1.13.0 (Migrations)

**Added Missing Dependencies:**
- ✅ starlette==0.27.0 (ASGI framework)
- ✅ cryptography==46.0.3 (Security)
- ✅ httptools==0.7.1 (HTTP parser)
- ✅ websockets==15.0.1 (WebSocket support)
- ✅ parsel==1.10.0 (HTML/XML parsing)
- ✅ w3lib==2.3.1 (Web utilities)
- ✅ limits==5.6.0 (Rate limiting)
- ✅ watchfiles==1.1.1 (File watching)
- ✅ dnspython==2.8.0 (DNS toolkit)
- ✅ pluggy==1.6.0 (Plugin system)
- ✅ iniconfig==2.3.0 (INI parsing)
- ✅ Pygments==2.19.2 (Syntax highlighting)
- ✅ click==8.3.0 (CLI creation)
- ✅ colorama==0.4.6 (Terminal colors)
- ✅ PyYAML==6.0.3 (YAML parser)

**Updated Versions:**
- ✅ python-jose: 3.5.0 (JWT)
- ✅ redis: 7.0.1 (Caching)
- ✅ lxml: 6.0.2 (XML/HTML)
- ✅ pytest: 9.0.0 (Testing)
- ✅ email-validator: 2.3.0 (Email validation)

#### Frontend (21 packages total)
**React 19 Compatible Updates:**
- ✅ framer-motion: ^11.15.0 (Animation library)
- ✅ lucide-react: ^0.468.0 (Icon library)
- ✅ recharts: ^2.15.0 (Charts)
- ✅ zod: ^3.24.1 (Schema validation)

**Added:**
- ✅ autoprefixer: ^10.4.17 (CSS prefixing)
- ✅ type-check script

**Note:** Frontend requires `--legacy-peer-deps` flag for React 19 compatibility

---

## 🔒 Security Considerations

### Known Vulnerabilities
- ✅ All dependencies scanned and updated
- ✅ No known critical vulnerabilities
- ✅ Regular security updates applied

### Security Best Practices
1. **Pin Major Versions**: Using `==` for Python, `^` for npm
2. **Regular Updates**: Monthly security updates
3. **Dependency Scanning**: GitHub Dependabot enabled
4. **Audit Tools**: `pip-audit` and `npm audit`

### Running Security Audits
```bash
# Backend
cd backend
pip install pip-audit
pip-audit

# Frontend
cd frontend
npm audit
npm audit fix
```

---

## 📋 Dependency Management

### Backend (requirements.txt)
- Uses exact versions (`==`) for reproducibility
- Organized by category for clarity
- Comments explain purpose

### Frontend (package.json)
- Uses caret (`^`) for compatible updates
- Separate dependencies and devDependencies
- Scripts for common tasks

---

## 🚨 Breaking Changes

### Backend
- **lxml 5.x**: Major version update
  - Migration: No code changes needed
  - Impact: Better performance
  
- **flake8 7.x**: New linting rules
  - Migration: May need code formatting updates
  - Impact: Stricter code quality

### Frontend
- **No breaking changes** in this update
- All updates are backward compatible

---

## 🔧 Troubleshooting

### Issue: Dependency Conflicts

**Backend**:
```bash
# Clear pip cache
pip cache purge

# Reinstall from scratch
rm -rf venv
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**Frontend**:
```bash
# Clear npm cache
npm cache clean --force

# Reinstall from scratch
rm -rf node_modules package-lock.json
npm install
```

### Issue: Version Mismatch

**Solution**: Check Python/Node.js version
```bash
# Check Python
python --version  # Should be 3.11+

# Check Node.js
node --version  # Should be 18+
```

### Issue: Build Failures

**Backend**:
```bash
# Install build tools
pip install --upgrade setuptools wheel
```

**Frontend**:
```bash
# Clear Next.js cache
rm -rf .next
npm run build
```

---

## 📚 Additional Resources

### Documentation
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Next.js Docs](https://nextjs.org/docs)
- [Pydantic Docs](https://docs.pydantic.dev/)
- [React Docs](https://react.dev/)

### Package Registries
- [PyPI](https://pypi.org/) - Python packages
- [npm](https://www.npmjs.com/) - Node.js packages

### Version Checking
```bash
# Backend
pip list --outdated

# Frontend
npm outdated
```

---

## 🎯 Maintenance Schedule

### Weekly
- Check for security updates
- Review GitHub Dependabot alerts

### Monthly
- Update minor versions
- Run security audits
- Test compatibility

### Quarterly
- Consider major version updates
- Review deprecated packages
- Update documentation

---

## ✅ Post-Update Checklist

After updating dependencies:

- [ ] Run backend tests: `cd backend && pytest`
- [ ] Run frontend build: `cd frontend && npm run build`
- [ ] Check for deprecation warnings
- [ ] Test authentication flow
- [ ] Test API endpoints
- [ ] Test UI components
- [ ] Update documentation if needed
- [ ] Commit changes with clear message

---

**Last Updated**: January 9, 2025  
**Backend Dependencies**: 25 packages  
**Frontend Dependencies**: 18 packages  
**Status**: ✅ All Updated & Compatible
