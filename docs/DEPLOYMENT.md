# ExamSensei Deployment Guide

> **Quick Deploy**: Frontend on Vercel, Backend on Railway

---

## 🚀 Frontend Deployment (Vercel)

### Step 1: Connect Repository
1. Go to [vercel.com](https://vercel.com) and sign in with GitHub
2. Click **"Add New Project"**
3. Import `msrishav-28/exam-sensei` repository

### Step 2: Configure Environment Variables
In Vercel Dashboard → Settings → Environment Variables:

| Variable | Value |
|----------|-------|
| `NEXT_PUBLIC_API_URL` | `https://your-app.up.railway.app/api/v1` |

### Step 3: Deploy
Click **Deploy** - Vercel auto-detects `vercel.json` and builds!

---

## 🔧 Backend Deployment (Railway)

### Step 1: Create New Project
1. Go to [railway.app](https://railway.app) and sign in with GitHub
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Select `msrishav-28/exam-sensei`

### Step 2: Configure Build
Railway auto-detects `railway.toml`. Verify settings:
- **Root Directory**: `/` (default)
- **Build Command**: Uses Dockerfile
- **Start Command**: Auto-configured

### Step 3: Add PostgreSQL Database
1. Click **"+ New"** → **"Database"** → **"PostgreSQL"**
2. Railway auto-injects `DATABASE_URL`

### Step 4: Add Redis (Optional)
1. Click **"+ New"** → **"Database"** → **"Redis"**
2. Railway auto-injects `REDIS_URL`

### Step 5: Set Environment Variables
In Railway Dashboard → Variables:

| Variable | Value |
|----------|-------|
| `SECRET_KEY` | `openssl rand -hex 32` (generate this) |
| `ALLOWED_ORIGINS` | `https://your-app.vercel.app` |
| `ENVIRONMENT` | `production` |
| `LOG_LEVEL` | `INFO` |

### Step 6: Deploy
Railway auto-deploys on push to main branch!

---

## 📋 Post-Deployment Checklist

- [ ] Frontend loads at Vercel URL
- [ ] Backend health: `https://your-app.up.railway.app/api/v1/health`
- [ ] API docs: `https://your-app.up.railway.app/api/v1/docs`
- [ ] User registration works
- [ ] Login returns JWT token

---

## 🔗 Connect Frontend to Backend

After both are deployed:

1. **Get Railway URL**: Railway Dashboard → your service → Settings → Domains
2. **Update Vercel**: Add `NEXT_PUBLIC_API_URL=https://your-railway-url/api/v1`
3. **Update Railway CORS**: Add `ALLOWED_ORIGINS=https://your-vercel-url`

---

## 💰 Cost Estimate

| Service | Free Tier | Production |
|---------|-----------|------------|
| **Vercel** (Frontend) | ✅ Free | $20/mo (Pro) |
| **Railway** (Backend) | $5 credit/mo | ~$5-10/mo |
| **Railway** PostgreSQL | Included | ~$5/mo |
| **Railway** Redis | Included | ~$3/mo |
| **Total** | **~$5/mo** | **~$33/mo** |

---

## 🐛 Troubleshooting

### Frontend 404 Error
- Verify `vercel.json` exists and is valid

### Backend Not Starting
- Check Railway logs for errors
- Verify `DATABASE_URL` is set (add PostgreSQL addon)

### CORS Errors
- Add exact Vercel URL to `ALLOWED_ORIGINS`
- Include both with/without `www.`

### API Connection Failed
- Check `NEXT_PUBLIC_API_URL` in Vercel
- Ensure Railway service is running
- Verify health endpoint responds
