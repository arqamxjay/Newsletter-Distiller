# Newsletter Distiller Web App - Setup & Deployment Guide

## Quick Start (Local Development)

### Prerequisites
- Python 3.9+
- Redis (for background jobs)
- Gmail API credentials (from Google Cloud Console)

### Step 1: Install Dependencies

```bash
pip install -r requirements_web.txt
```

### Step 2: Configure Environment

Create a `.env` file:

```env
FLASK_ENV=development
SECRET_KEY=dev-secret-key-change-in-production
DATABASE_URL=sqlite:///newsletter_distiller.db
GMAIL_CREDENTIALS_FILE=credentials.json
GOOGLE_CLIENT_ID=your-client-id-here
GOOGLE_CLIENT_SECRET=your-client-secret-here
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### Step 3: Initialize Database

```bash
python
>>> from app import create_app, db
>>> app = create_app()
>>> with app.app_context(): db.create_all()
>>> exit()
```

### Step 4: Start Redis

```bash
redis-server
```

### Step 5: Run the App (Terminal 1)

```bash
python wsgi.py
```

### Step 6: Run Celery Worker (Terminal 2)

```bash
celery -A app.workers.tasks worker --loglevel=info
```

Visit http://localhost:5000

---

## Google Cloud Setup

### 1. Create OAuth 2.0 Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project: "Newsletter Distiller"
3. Enable Gmail API:
   - APIs & Services → Library
   - Search "Gmail API"
   - Click Enable
4. Create OAuth 2.0 credentials:
   - APIs & Services → Credentials
   - Create Credentials → OAuth client ID
   - Application type: Web application
   - Authorized redirect URIs:
     - http://localhost:5000/gmail/callback (local)
     - https://yourapp.com/gmail/callback (production)
5. Download credentials.json

### 2. Add Test Users

1. Go to OAuth consent screen
2. Add your email as a test user
3. Save

---

## Deployment to Production

### Option 1: Heroku (Easiest)

```bash
# Install Heroku CLI
brew install heroku/brew/heroku

# Login
heroku login

# Create app
heroku create Newsletter-Distiller

# Add buildpack for Python
heroku buildpacks:add heroku/python

# Set environment variables
heroku config:set SECRET_KEY=your-secret-key
heroku config:set GOOGLE_CLIENT_ID=your-client-id
heroku config:set GOOGLE_CLIENT_SECRET=your-client-secret

# Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Add Redis
heroku addons:create heroku-redis:premium-0

# Deploy
git push heroku main

# Initialize database
heroku run python -c "from app import create_app, db; app = create_app(); db.create_all()"
```

### Option 2: Google Cloud Run

```bash
# Create app.yaml
cat > app.yaml << EOF
runtime: python39
env: standard

env_variables:
  FLASK_ENV: "production"
  SECRET_KEY: "your-secret-key"
  DATABASE_URL: "postgresql://user:pass@/db"

automatic_scaling:
  min_instances: 1
  max_instances: 10
EOF

# Deploy
gcloud run deploy newsletter-distiller \
  --source . \
  --platform managed \
  --region us-central1
```

### Option 3: AWS Elastic Beanstalk

```bash
# Install EB CLI
pip install awsebcli

# Initialize
eb init -p python-3.9 newsletter-distiller

# Create environment
eb create production

# Deploy
eb deploy
```

### Option 4: DigitalOcean App Platform

1. Connect GitHub repository
2. Create `Procfile`:
```
web: gunicorn wsgi:app
worker: celery -A app.workers.tasks worker --loglevel=info
```
3. Set environment variables in dashboard
4. Deploy

---

## Production Checklist

- [ ] Set `FLASK_ENV=production`
- [ ] Use strong `SECRET_KEY`
- [ ] Enable HTTPS/SSL
- [ ] Use PostgreSQL (not SQLite)
- [ ] Use Redis for caching/jobs
- [ ] Set up email sending
- [ ] Configure error logging (Sentry)
- [ ] Set up uptime monitoring
- [ ] Enable CORS for your domain
- [ ] Rate limit API endpoints
- [ ] Configure backup strategy
- [ ] Set up CI/CD pipeline

---

## Database Migrations (Optional)

If you want to track schema changes:

```bash
pip install flask-migrate

# Initialize
flask db init

# Create migration
flask db migrate -m "Initial migration"

# Apply migration
flask db upgrade
```

---

## Monitoring & Maintenance

### View Logs
```bash
heroku logs --tail  # Heroku
gcloud run logs read --limit 50  # Google Cloud Run
```

### Database Backup
```bash
# Heroku
heroku pg:backups:capture
heroku pg:backups:download

# AWS RDS
aws rds create-db-snapshot --db-instance-identifier newsletter-db
```

### Celery Flower (Job Monitoring)
```bash
pip install flower
celery -A app.workers.tasks flower
# Visit http://localhost:5555
```

---

## Scaling Considerations

- **Database**: Upgrade to managed PostgreSQL for production
- **Jobs**: Use SQS/RabbitMQ instead of Redis for more reliability
- **Caching**: Add Redis caching layer for user preferences
- **Load Balancing**: Use CloudFlare or AWS ALB
- **CDN**: Serve static files from CloudFront/CloudFlare

---

## Troubleshooting

### "Address already in use"
```bash
# Find and kill process on port 5000
lsof -i :5000 | grep -v COMMAND | awk '{print $2}' | xargs kill -9
```

### Redis connection errors
```bash
# Check Redis is running
redis-cli ping
# Should return: PONG
```

### Gmail token expired
- User needs to re-authorize at Settings page
- System automatically attempts refresh

### Celery worker not processing
```bash
# Check worker status
celery -A app.workers.tasks inspect active
celery -A app.workers.tasks inspect registered
```

---

## Next Features to Implement

- [ ] Scheduled job execution (every hour, daily, etc.)
- [ ] Email digest compilation
- [ ] User-to-user email forwarding
- [ ] Admin dashboard
- [ ] Analytics & reporting
- [ ] Webhook support
- [ ] API for third-party integrations
- [ ] Dark mode UI
- [ ] Mobile app

---

## Support

For issues or questions:
1. Check logs: `heroku logs --tail`
2. Test locally: `python wsgi.py`
3. Check Celery worker: `celery -A app.workers.tasks inspect`
