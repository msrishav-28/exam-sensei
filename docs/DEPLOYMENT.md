# ExamSensei Deployment Guide

> **Quick Deploy**: Frontend on Vercel, Backend on Render

## 🚀 Frontend Deployment (Vercel)

### Step 1: Connect Repository
1. Go to [vercel.com](https://vercel.com) and sign in with GitHub
2. Click **"Add New Project"**
3. Import `msrishav-28/exam-sensei` repository

### Step 2: Configure Project
Vercel will auto-detect the configuration from `vercel.json`.

**Environment Variables** (Set in Vercel Dashboard → Settings → Environment Variables):

| Variable | Value |
|----------|-------|
| `NEXT_PUBLIC_API_URL` | `https://examsensei-api.onrender.com/api/v1` |

### Step 3: Deploy
Click **Deploy** - Vercel handles the rest!

---

## 🔧 Backend Deployment (Render)

### Option A: One-Click Blueprint Deploy (Recommended)

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New"** → **"Blueprint"**
3. Connect your GitHub repository
4. Render will detect `render.yaml` and create all services automatically

### Option B: Manual Setup

1. Create a new **Web Service**
   - **Name**: `examsensei-api`
   - **Runtime**: Docker
   - **Dockerfile Path**: `./backend/Dockerfile`
   - **Docker Context**: `./backend`

2. Add a **PostgreSQL** database
   - **Name**: `examsensei-db`
   - Copy the connection string

3. Add **Redis** cache
   - **Name**: `examsensei-redis`
   - Copy the connection string

4. Set **Environment Variables**:

| Variable | Value |
|----------|-------|
| `DATABASE_URL` | `(from PostgreSQL)` |
| `REDIS_URL` | `(from Redis)` |
| `SECRET_KEY` | `(generate: openssl rand -hex 32)` |
| `ALLOWED_ORIGINS` | `https://your-vercel-app.vercel.app` |
| `ENVIRONMENT` | `production` |

---

## 📋 Post-Deployment Checklist

- [ ] Frontend loads at Vercel URL
- [ ] Backend health check: `https://your-api.onrender.com/api/v1/health`
- [ ] API docs accessible: `https://your-api.onrender.com/api/v1/docs`
- [ ] CORS allows frontend origin
- [ ] Database migrations run successfully
- [ ] User registration/login works

---

## 🔗 Update CORS After Deployment

Once you have your Vercel URL, update the backend's `ALLOWED_ORIGINS`:

```bash
# In Render Dashboard → examsensei-api → Environment
ALLOWED_ORIGINS=https://examsensei.vercel.app,https://www.examsensei.com
```

---

## 💰 Cost Estimate

| Service | Free Tier | Production |
|---------|-----------|------------|
| **Vercel** (Frontend) | ✅ Free | $20/mo (Pro) |
| **Render** (Backend) | ✅ Free (cold starts) | $7/mo (Starter) |
| **Render** PostgreSQL | ✅ Free (90 days) | $7/mo |
| **Render** Redis | ✅ Free | $5/mo |
| **Total** | **$0/mo** | **~$39/mo** |

---

## 🐛 Troubleshooting

### Frontend 404 Error
- Check `vercel.json` exists in repository root
- Verify `outputDirectory` is `frontend/.next`

### Backend Cold Start Delays
- Render free tier sleeps after 15 min inactivity
- First request takes 30-60 seconds to wake up
- Upgrade to Starter ($7/mo) for always-on

### CORS Errors
- Add exact Vercel URL to `ALLOWED_ORIGINS`
- Include both with and without `www.`

### Database Connection Failed
- Ensure `DATABASE_URL` is set correctly
- Check PostgreSQL service is running
- Verify IP allowlist includes Render IPs
