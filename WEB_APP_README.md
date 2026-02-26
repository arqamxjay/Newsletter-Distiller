# Newsletter Distiller - Web App Version

A multi-user web application that automatically fetches, cleans, summarizes, and delivers newsletters from Gmail using AI.

## Features

✨ **Multi-User Support** - Each user manages their own Gmail account  
🔐 **OAuth 2.0 Authentication** - Secure Gmail integration  
📧 **Email Processing** - Fetch, clean, and summarize newsletters  
⚙️ **Customizable Settings** - Configure processing preferences  
📊 **Dashboard** - Track processed newsletters  
🔄 **Background Jobs** - Process emails asynchronously  

## Project Structure

```
app/
├── __init__.py           # Flask app factory
├── models/               # Database models
├── routes/               # Blueprint routes
│   ├── auth.py          # Login/signup
│   ├── dashboard.py      # Dashboard
│   └── gmail.py         # OAuth flows
├── templates/           # HTML templates
│   ├── base.html
│   ├── auth/
│   └── dashboard/
└── static/              # CSS, JS, images

config.py               # Configuration
wsgi.py                # WSGI entry point
requirements_web.txt   # Python dependencies
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements_web.txt
```

### 2. Update .env File

```
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///newsletter_distiller.db
GMAIL_CREDENTIALS_FILE=credentials.json
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
```

### 3. Initialize Database

```bash
python
>>> from app import create_app, db
>>> app = create_app()
>>> with app.app_context(): db.create_all()
>>> exit()
```

### 4. Run Locally

```bash
python wsgi.py
```

Visit http://localhost:5000 and sign up!

## Deployment

### Heroku

```bash
heroku create your-app-name
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DATABASE_URL=postgresql://...
heroku config:set GMAIL_CREDENTIALS_FILE=credentials.json
git push heroku main
```

### Google Cloud Run

```bash
gcloud run deploy newsletter-distiller --source .
```

### AWS Elastic Beanstalk

```bash
eb init
eb create
eb deploy
```

## Database Models

- **User** - User accounts with email/password
- **GmailToken** - OAuth tokens for each user
- **UserPreferences** - Per-user processing settings
- **Newsletter** - Processed newsletters history

## Next Steps

- [ ] Integrate background job processing with Celery
- [ ] Add email sending functionality
- [ ] Implement admin dashboard
- [ ] Add scheduling for automatic processing
- [ ] Deploy to production server
- [ ] Set up email notifications

## Architecture Notes

The web app follows MVC architecture:
- **Models** - Database layer (`app/models/`)
- **Views** - Template rendering (`app/templates/`)
- **Controllers** - Route handlers (`app/routes/`)

Authentication uses Flask-Login with SQLAlchemy for session management.

OAuth credentials are stored securely and automatically refreshed when needed.
