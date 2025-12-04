## Deploy to Render

This app is configured to run on Render using Gunicorn.

### Prerequisites
- A Render account
- Your repository connected to Render

### Steps
1. Ensure `requirements.txt` includes `gunicorn` (already present).
2. The app binds to `PORT` and `0.0.0.0` in `app.py` for production.
3. Use the provided `render.yaml` for one-click deployment, or set the service commands manually:
	- Build Command: `pip install -r requirements.txt`
	- Start Command: `gunicorn app:app --workers 2 --threads 4 --timeout 120 --bind 0.0.0.0:$PORT`
4. Set environment variables:
	- `MAIL_USERNAME` and `MAIL_PASSWORD` for SMTP
	- `ADMIN_USERNAME` and `ADMIN_PASSWORD` (optional)

### Notes
- The SQLite database (`registrations.db`) is stored on disk. For multi-instance or persistent storage across deploys, consider using Render PostgreSQL and updating the app to use `DATABASE_URL`.
- File uploads go to `uploads/`. On Render, use persistent disks or external storage if needed.
#  necSprint 2025 - Hackathon Registration Website

A Flask web application for hackathon registration, project submissions, and event management.

## 🔧 Prerequisites

- **Python 3.7+** installed
- **pip** (Python package installer)
- Web browser

##  How to Run

### Step 1: Navigate to Project Directory
```bash
cd Website
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run the Application
```bash
python app.py
```

**That's it!** The website will be available at: **http://localhost:5000**

### Alternative Method (Using Virtual Environment)
```bash
# Create virtual environment
python -m venv .venv

# Activate it
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```




##  Architecture

- **Frontend:** HTML/CSS/JavaScript templates
- **Backend:** Flask (Python web framework)
- **Database:** SQLite (auto-created)
- **Files:** Uploaded to `uploads/` folder

