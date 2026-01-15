# ExamSensei Deployment Guide

> **Production Stack**: Frontend on Vercel, Backend on Render

---

## 🚀 Frontend Deployment (Vercel)

### Step 1: Connect Repository
1. Go to [vercel.com](https://vercel.com) and sign in with GitHub
2. Click **"Add New Project"**
3. Import `msrishav-28/exam-sensei` repository

### Step 2: Configure Build
Vercel auto-detects `vercel.json`. Verify settings:
- **Framework Preset**: Next.js
- **Root Directory**: `/` (default)
- **Build Command**: Auto-detected from `vercel.json`

### Step 3: Environment Variables
In Vercel Dashboard → Settings → Environment Variables:

| Variable | Value |
|----------|-------|
| `NEXT_PUBLIC_API_URL` | `https://examsensei-api.onrender.com/api/v1` |

### Step 4: Deploy
Click **Deploy** - Vercel handles the rest!

---

## 🔧 Backend Deployment (Render)

### Option A: One-Click Blueprint Deploy (Recommended)

1. Go to [render.com](https://render.com)
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub repository
4. Render auto-detects `render.yaml` and creates:
   - Web Service (FastAPI backend)
   - PostgreSQL database
   - Redis cache

### Option B: Manual Setup

#### Step 1: Create Web Service
1. Click **"New +"** → **"Web Service"**
2. Connect GitHub repo

| Setting | Value |
|---------|-------|
| **Name** | `examsensei-api` |
| **Region** | `Singapore` (closest to India) |
| **Branch** | `main` |
| **Root Directory** | `backend` |
| **Runtime** | `Docker` |
| **Plan** | `Free` or `Starter ($7/mo)` |

#### Step 2: Add PostgreSQL Database
1. Click **"New +"** → **"PostgreSQL"**
2. Copy the **Internal Database URL**

#### Step 3: Add Redis (Optional)
1. Click **"New +"** → **"Redis"**
2. Copy the **Internal Redis URL**

#### Step 4: Set Environment Variables

| Variable | Value |
|----------|-------|
| `DATABASE_URL` | `(Internal PostgreSQL URL)` |
| `REDIS_URL` | `(Internal Redis URL)` |
| `SECRET_KEY` | Generate: `openssl rand -hex 32` |
| `ALLOWED_ORIGINS` | `https://your-app.vercel.app` |
| `ENVIRONMENT` | `production` |
| `LOG_LEVEL` | `INFO` |

---

## 📋 Post-Deployment Checklist

- [ ] Frontend loads at Vercel URL
- [ ] Backend health: `https://your-api.onrender.com/api/v1/health`
- [ ] API docs: `https://your-api.onrender.com/api/v1/docs`
- [ ] CORS configured for Vercel domain
- [ ] User registration works
- [ ] Login returns JWT token

---

## 🔗 Connect Frontend to Backend

After both are deployed:

1. **Copy Render URL**: Render Dashboard → Service → Copy URL
2. **Update Vercel**: Settings → Environment Variables → Add:
   - `NEXT_PUBLIC_API_URL` = `https://your-render-url/api/v1`
3. **Update Render CORS**: Environment → Add:
   - `ALLOWED_ORIGINS` = `https://your-vercel-url`

---

## 💰 Cost Estimate

| Service | Free Tier | Production |
|---------|-----------|------------|
| **Vercel** Frontend | ✅ Free | $20/mo (Pro) |
| **Render** Backend | ✅ Free (cold starts) | $7/mo |
| **Render** PostgreSQL | ✅ Free (90 days) | $7/mo |
| **Render** Redis | ✅ Free | $5/mo |
| **Total** | **$0/mo** | **~$39/mo** |

> **Note**: Render free tier has cold starts (~30s delay after 15 min inactivity).
> Upgrade to Starter ($7/mo) for always-on service.

---

## 🐛 Troubleshooting

### Frontend 404 Error
- Verify `vercel.json` exists in repository root
- Check Vercel build logs for errors

### Backend Not Starting
- Check Render logs for errors
- Verify `DATABASE_URL` is set correctly
- Ensure Dockerfile builds successfully

### CORS Errors
- Add exact Vercel URL to `ALLOWED_ORIGINS`
- Include both `https://` prefix and no trailing slash
- Restart Render service after changing env vars

### Database Connection Failed
- Verify PostgreSQL service is running
- Use **Internal Database URL** (not External)
- Check connection string format

### API Connection Timeout
- Render free tier may need ~30s to wake up
- First request after idle triggers cold start
- Consider upgrading to Starter plan

---

## 🔐 Security Notes

- Never commit `.env` files to Git
- Use Render's `generateValue: true` for `SECRET_KEY`
- Enable HTTPS (automatic on both platforms)
- Restrict `ALLOWED_ORIGINS` to your domains only
