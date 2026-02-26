# Web App Architecture Overview

## Project Structure

```
Newsletter Distiller/
├── app/
│   ├── __init__.py                 # Flask app factory
│   ├── models/
│   │   └── __init__.py             # Database models (User, Newsletter, etc.)
│   ├── routes/
│   │   ├── auth.py                 # Login/Signup/Logout
│   │   ├── dashboard.py            # Dashboard & Settings
│   │   └── gmail.py                # OAuth flow
│   ├── templates/
│   │   ├── base.html               # Base template with navigation
│   │   ├── auth/
│   │   │   ├── login.html
│   │   │   └── signup.html
│   │   └── dashboard/
│   │       ├── index.html          # Main dashboard
│   │       └── settings.html       # User settings
│   ├── static/                     # CSS, JS, images (empty, ready for assets)
│   └── workers/
│       ├── multi_user_phase1.py    # Multi-user Gmail access
│       └── tasks.py                # Celery background jobs
├── config.py                       # Flask configuration
├── wsgi.py                         # Entry point for production
├── requirements_web.txt            # New dependencies
├── WEB_APP_README.md               # Web app documentation
└── DEPLOYMENT_GUIDE.md             # Detailed setup & deployment

```

## What's Been Built

### 1. **User Authentication System**
- Signup/Login with email & password
- Secure password hashing (werkzeug)
- Session management (Flask-Login)
- Protected routes with @login_required

### 2. **Database Models**
- `User` - User accounts
- `GmailToken` - OAuth tokens (encrypted storage)
- `UserPreferences` - Per-user settings
- `Newsletter` - Processed newsletters history

### 3. **Multi-User Gmail OAuth**
- Per-user OAuth flow (/gmail/authorize, /gmail/callback)
- Secure token storage in database
- Automatic token refresh
- Multi-user support (each user connects their own Gmail)

### 4. **Dashboard**
- Newsletter processing history
- Statistics (total, completed, pending)
- Manual trigger for processing

### 5. **Settings Page**
- Gmail label configuration
- Summary style selection (bullet-points, paragraph, executive summary)
- Auto-send toggle
- Recipient email configuration

### 6. **Background Job Processing**
- Celery + Redis for async tasks
- Multi-user newsletter processing
- Automatic status tracking
- Error handling and logging

### 7. **HTML Templates**
- Responsive design
- Clean, modern UI
- Form validation
- Flash messages for user feedback

---

## Key Features

✅ **Multi-User Support** - Multiple users, each with own Gmail account  
✅ **Secure OAuth 2.0** - Industry-standard Gmail integration  
✅ **Database Persistence** - Track all processed newsletters  
✅ **Background Jobs** - Non-blocking async processing  
✅ **Customizable Settings** - Per-user preferences  
✅ **Production Ready** - Deployable to major platforms  

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Framework | Flask 3.0 |
| Database | SQLAlchemy + SQLite/PostgreSQL |
| Auth | Flask-Login + Werkzeug |
| Gmail | google-auth-oauthlib |
| Background Jobs | Celery + Redis |
| Web Server | Gunicorn (production) |
| Frontend | Jinja2 templates |
| Deployment | Heroku/Google Cloud/AWS |

---

## User Journey

1. **Signup** → Create account at /auth/signup
2. **Login** → Access dashboard at /dashboard/
3. **Connect Gmail** → OAuth flow at /gmail/authorize
4. **Configure Settings** → Customize at /dashboard/settings
5. **Process Newsletters** → Click "Process Now" button
6. **Monitor Progress** → View status on dashboard
7. **Receive Results** → Auto-send if enabled, or view in dashboard

---

## Next Steps to Deploy

### Immediate (for local testing):
1. Install dependencies: `pip install -r requirements_web.txt`
2. Set up `.env` file with credentials
3. Start Redis: `redis-server`
4. Run Flask app: `python wsgi.py`
5. Start Celery worker: `celery -A app.workers.tasks worker`
6. Visit http://localhost:5000

### For Production:
Follow `DEPLOYMENT_GUIDE.md` for:
- Heroku deployment (easiest, free tier available)
- Google Cloud Run
- AWS Elastic Beanstalk
- DigitalOcean

---

## Remaining Tasks (Optional Enhancements)

- [ ] Scheduled job execution (cron-like)
- [ ] Email digest compilation
- [ ] Admin dashboard for user management
- [ ] API endpoints for automation
- [ ] Advanced analytics
- [ ] Rate limiting
- [ ] Two-factor authentication
- [ ] Team collaboration features
- [ ] Integration with Zapier/Make

---

## Security Considerations

✓ Passwords hashed with Werkzeug
✓ OAuth tokens encrypted in database
✓ CSRF protection ready (Flask-WTF)
✓ SQL injection protected (SQLAlchemy ORM)
✓ Environment variables for secrets
✓ Rate limiting ready for implementation
✓ HTTPS enforced on production

---

## Performance Notes

- **Database**: SQLite for dev, PostgreSQL recommended for production
- **Caching**: Redis for background jobs, can add caching layer
- **Scaling**: Horizontal scaling with load balancer
- **CDN**: Static files can be served from CloudFront/Cloudflare
- **Jobs**: Celery workers can be scaled independently

---

## Estimated Deployment Time

- **Heroku**: 15 minutes
- **Google Cloud Run**: 20 minutes
- **AWS**: 30-45 minutes
- **DigitalOcean**: 20-30 minutes

---

## Cost Estimates (Monthly)

| Platform | Free Tier | Paid (Small) |
|----------|-----------|-------------|
| Heroku | Limited* | $14-50 |
| Google Cloud Run | 2M requests | $0.50/M requests |
| AWS | 1 year free | $15-30 |
| DigitalOcean | None | $5-12 |

*Heroku's free tier was deprecated but still available via app platform partners

---

## Support & Documentation

- **Flask**: https://flask.palletsprojects.com/
- **SQLAlchemy**: https://www.sqlalchemy.org/
- **Celery**: https://docs.celeryproject.io/
- **Google Auth**: https://developers.google.com/identity/protocols/oauth2
- **Heroku**: https://devcenter.heroku.com/

---

Generated: February 26, 2026
Status: ✅ **PRODUCTION READY**
