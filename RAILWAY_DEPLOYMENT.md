# TechSprint - Railway Deployment Guide ✅

## 🎉 Your App is PRODUCTION-READY for Railway!

All necessary files are configured. Follow these simple steps:

---

## 📋 Pre-Deployment Checklist

✅ `Procfile` - Created (uses gunicorn)
✅ `runtime.txt` - Created (Python 3.12)
✅ `requirements.txt` - Updated (includes gunicorn)
✅ `.gitignore` - Configured (excludes secrets)
✅ Production fixes applied (port binding, secret key, debug off)
✅ Phone field added to registration

---

## 🚀 Deploy to Railway in 5 Minutes

### Step 1: Push to GitHub

### Step 1: Push to GitHub

```bash
cd /home/dev/Desktop/Website
git add .
git commit -m "Production ready: Railway deployment config added"
git push origin dev
```

### Step 2: Deploy on Railway

1. **Go to [railway.app](https://railway.app)** and sign in with GitHub

2. **Click "New Project"** → **"Deploy from GitHub repo"**

3. **Select** `ManjilS/Website` repository

4. **Railway auto-detects:**
   - ✅ Python app (from runtime.txt)
   - ✅ Dependencies (from requirements.txt)
   - ✅ Start command (from Procfile)

### Step 3: Add Environment Variables

In Railway dashboard → Your Project → Variables, add:

```
MAIL_USERNAME=manjil.shrestha2003@gmail.com
MAIL_PASSWORD=dldh roln jnmo kymu
ADMIN_USERNAME=admin
ADMIN_PASSWORD=necsprint2024
SECRET_KEY=change-this-to-random-secret-key-production
```

**Important**: Generate a secure SECRET_KEY:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Step 4: Deploy!

### Cost:
- **Free Tier**: $5 credit/month (enough for development)
- **Hobby**: $5/month for more usage

---

## 🚂 Deploy to Render (Alternative)

### Steps:

1. **Sign up at [render.com](https://render.com)**

2. **Create New Web Service**
   - Connect GitHub account
   - Select `ManjilS/Website` repository

3. **Configure**
   - Name: `techsprint`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python app.py`

4. **Add Environment Variables**
   ```
   MAIL_USERNAME=your_gmail@gmail.com
   MAIL_PASSWORD=your_app_password
   ADMIN_USERNAME=admin
   ADMIN_PASSWORD=your_secure_password
   ```

5. **Enable Persistent Disk**
   - In service settings, add a disk
   - Mount path: `/opt/render/project/src`
   - Size: 1GB (free tier)

6. **Deploy**
   - Render will auto-deploy on every push to GitHub

### Cost:
- **Free Tier**: Available (with some limitations)
- **Starter**: $7/month for better performance

---

## 📊 Comparison

| Feature | Railway | Render | Vercel |
|---------|---------|--------|--------|
| SQLite Support | ✅ Yes | ✅ Yes | ❌ No |
| File Uploads | ✅ Yes | ✅ Yes | ❌ No |
| Free Tier | $5 credit | ✅ Limited | ✅ Good |
| Auto Deploy | ✅ Yes | ✅ Yes | ✅ Yes |
| Code Changes | ❌ None | ❌ None | ✅ Required |
| Best For | This project | This project | Static sites |

---

## 🎯 Recommendation

**Use Railway or Render** - they work with your current code without any modifications and support:
- ✅ SQLite database persistence
- ✅ File upload storage (proposals, documents)
- ✅ Session management
- ✅ Easy deployment from GitHub
- ✅ Auto-deploy on push

**Vercel requires significant refactoring** to use PostgreSQL and blob storage instead of SQLite and local files.

---

## 🔧 Quick Railway Deployment

```bash
# Install Railway CLI (optional)
npm install -g @railway/cli

# Login
railway login

# Link project
railway link

# Deploy
railway up
```

Done! Your app is live with full database and file upload support.
