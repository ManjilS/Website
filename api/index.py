from app import app

# Vercel requires the app to be exported as 'app'
# The serverless function will automatically invoke it
app = app
