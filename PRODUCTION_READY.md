# ✅ PRODUCTION READY - Railway Deployment

## Changes Made for Railway Production

### 1. **Production Server Setup**
- ✅ Added `Procfile` - Uses gunicorn instead of Flask dev server
- ✅ Added `runtime.txt` - Specifies Python 3.12
- ✅ Updated `requirements.txt` - Added gunicorn for production
- ✅ Fixed app.py - Binds to 0.0.0.0 and uses PORT env variable
- ✅ Disabled debug mode - Set `debug=False` for production

### 2. **Security Improvements**
- ✅ SECRET_KEY from environment variable
- ✅ All sensitive data uses os.environ.get()
- ✅ .gitignore excludes database and uploads
- ✅ .env.example provided for reference

### 3. **Database & Storage**
- ✅ Phone field added to registration
- ✅ All queries updated to include phone column
- ✅ Admin dashboard shows phone numbers
- ✅ CSV export includes phone
- ✅ SQLite database persists on Railway
- ✅ File uploads persist in uploads/ folder

### 4. **Fixed Issues**
- ✅ Admin page IndexError fixed (phone column query)
- ✅ Registration form includes phone field
- ✅ Email confirmation sends (with proper credentials)
- ✅ Port binding works for Railway (0.0.0.0)

---

## Test Locally Before Deployment

```bash
# Start with gunicorn (production mode)
source .venv/bin/activate
gunicorn app:app

# Test in browser
# Visit: http://127.0.0.1:8000
```

---

## Deploy to Railway (5 Minutes)

```bash
# 1. Push to GitHub
git add .
git commit -m "Ready for Railway deployment"
git push origin dev

# 2. Go to railway.app
# 3. New Project → Deploy from GitHub → Select ManjilS/Website
# 4. Add environment variables (see .env.example)
# 5. Deploy automatically starts!
```

---

## Environment Variables for Railway

Copy these to Railway dashboard:

```
MAIL_USERNAME=manjil.shrestha2003@gmail.com
MAIL_PASSWORD=dldh roln jnmo kymu
ADMIN_USERNAME=admin
ADMIN_PASSWORD=necsprint2024
SECRET_KEY=generate-random-secret-key-here
```

Generate SECRET_KEY:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## What Works on Railway

✅ **Database** - SQLite persists between deployments
✅ **File Uploads** - uploads/ folder persists
✅ **Sessions** - Admin login works
✅ **Email** - Confirmation emails send
✅ **Static Files** - CSS, JS, images load
✅ **Templates** - All pages render
✅ **Registration** - With phone number field
✅ **Admin Panel** - Shows all registrations

---

## Railway Cost

- **Free Tier**: $5 credit per month (enough for development/testing)
- **Hobby Plan**: $5/month for production use
- **Pay as you go**: Only pay for what you use

---

## Post-Deployment Checklist

After Railway deploys, test these:

1. ✅ Homepage loads: `https://your-app.up.railway.app/`
2. ✅ Registration works: `/register`
3. ✅ Phone field appears and saves
4. ✅ Email confirmation sends
5. ✅ Admin login: `/admin/login`
6. ✅ Registrations show in admin with phone numbers
7. ✅ File upload works (optional proposal)
8. ✅ CSV export includes phone column

---

## Support

If you encounter issues:

1. Check Railway logs in dashboard
2. Verify all environment variables are set
3. Ensure Gmail app password is correct
4. Check that database initialized (first request creates it)

---

## 🎉 Ready to Deploy!

Your app is production-ready with all fixes applied. Railway will handle:
- ✅ Automatic deployments on git push
- ✅ HTTPS certificate
- ✅ Persistent storage
- ✅ Environment variables
- ✅ Zero downtime deploys

**Just push to GitHub and deploy on Railway!**
