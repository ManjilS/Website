# Deploy to Vercel

Your Flask app is now configured for Vercel deployment with phone number field added.

## ⚠️ CRITICAL: Vercel Limitations for This Project

**Your app uses SQLite + File Uploads which DO NOT work on Vercel serverless.**

### Issues:
1. **SQLite Database**: Vercel's serverless functions are stateless - any database writes will be lost after the function ends
2. **File Uploads** (`uploads/`): Read-only filesystem - proposal files and documents cannot be saved
3. **Session Data**: Will not persist across function invocations

### Recommended Solutions:

#### Option A: Use Vercel with External Services (Best for Vercel)
1. **Database**: Replace SQLite with [Vercel Postgres](https://vercel.com/docs/storage/vercel-postgres)
   ```bash
   vercel postgres create
   ```
   - Update `app.py` to use PostgreSQL instead of SQLite
   - Install `psycopg2-binary` in requirements.txt

2. **File Storage**: Use [Vercel Blob](https://vercel.com/docs/storage/vercel-blob)
   ```bash
   npm install @vercel/blob
   ```
   - Replace file saving logic with blob storage
   - Store blob URLs in database

#### Option B: Deploy to Railway/Render (Easier - Recommended)
Deploy to platforms that support persistent storage:
- **Railway**: Free tier, supports SQLite + file uploads
- **Render**: Free tier, supports persistent disks
- **Fly.io**: Supports volumes for persistent storage

No code changes needed for Option B!

## Quick Deployment Steps

### 1. Install Vercel CLI
```bash
npm install -g vercel
```

### 2. Deploy from project root
```bash
cd /home/dev/Desktop/Website
vercel
```

Follow the prompts:
- Set up and deploy? **Yes**
- Which scope? Select your account
- Link to existing project? **No**
- What's your project's name? `techsprint` (or your choice)
- In which directory is your code located? **./  (press Enter)**
- Want to modify settings? **No**

### 3. Set Environment Variables

In the Vercel dashboard (or via CLI), configure these:

```bash
vercel env add MAIL_USERNAME
vercel env add MAIL_PASSWORD
vercel env add ADMIN_USERNAME
vercel env add ADMIN_PASSWORD
```

Values:
- `MAIL_USERNAME`: Your Gmail address (e.g., `coess@gmail.com`)
- `MAIL_PASSWORD`: Gmail App Password (not your regular password)
- `ADMIN_USERNAME`: Your admin username
- `ADMIN_PASSWORD`: Your admin password

To get Gmail App Password:
1. Go to Google Account → Security
2. Enable 2-Step Verification
3. Search for "App Passwords"
4. Generate password for "Mail"

### 4. Database Consideration

**Important**: SQLite doesn't persist on Vercel (serverless functions are stateless). You have two options:

#### Option A: Use Vercel Postgres (Recommended)
```bash
vercel postgres create
```
Then update `app.py` to use PostgreSQL instead of SQLite.

#### Option B: Use external database
- PlanetScale (MySQL)
- Supabase (PostgreSQL)
- MongoDB Atlas

### 5. File Uploads

Vercel serverless functions have a read-only filesystem. For `uploads/`:

**Use Vercel Blob Storage:**
```bash
npm install @vercel/blob
```

Or use external storage:
- AWS S3
- Cloudinary
- Vercel Blob

### 6. Production Deployment

After testing:
```bash
vercel --prod
```

## Files Created

- `vercel.json` - Vercel configuration
- `api/index.py` - Serverless function wrapper
- `requirements.txt` - Updated with dependencies

## Common Issues

1. **Database not persisting**: Switch to hosted database (see step 4)
2. **File uploads failing**: Use blob storage (see step 5)
3. **Environment variables not working**: Redeploy after setting them
4. **Cold starts**: First request may be slow (Vercel warms up function)

## Alternative: Use Vercel + External Services

If you want to keep SQLite locally for development:
1. Deploy frontend static files to Vercel
2. Deploy backend to Railway, Render, or Fly.io (supports persistent storage)
3. Update frontend API calls to point to your backend URL

## Local Testing

Test the serverless function locally:
```bash
vercel dev
```

This runs your app in a Vercel-like environment on `localhost:3000`.
