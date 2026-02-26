# 🚀 QUICK START: Deploy Newsletter Distiller to Render

## Complete in 5 Steps (15 minutes)

### Step 1: Push Code to GitHub
```bash
cd "/Users/prom1/Desktop/Newsletter Distiller"
git remote add origin https://github.com/YOUR_USERNAME/newsletter-distiller.git
git branch -M main
git push -u origin main
```

### Step 2: Set Up Google OAuth
1. Go to https://console.cloud.google.com
2. Create project: "Newsletter Distiller"
3. Enable Gmail API
4. Create OAuth 2.0 credentials (Web app)
5. Download credentials.json
6. Note your CLIENT_ID and CLIENT_SECRET

### Step 3: Deploy to Render
1. Go to https://render.com → Sign up with GitHub
2. Click **New** → **Web Service**
3. Select your `newsletter-distiller` repository
4. Fill in:
   - **Name**: newsletter-distiller
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements_web.txt`
   - **Start Command**: `gunicorn wsgi:app`
5. Click **Create Web Service**

### Step 4: Add Environment Variables
In Render dashboard, add these:

```
FLASK_ENV=production
SECRET_KEY=YOUR_SECURE_RANDOM_KEY
DATABASE_URL=sqlite:///newsletter_distiller.db
GMAIL_CREDENTIALS_FILE=credentials.json
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
```

### Step 5: Update Google OAuth Redirect URI
1. Go to Google Cloud Console
2. Update OAuth Redirect URI to your Render URL:
   - Format: `https://newsletter-distiller.onrender.com/gmail/callback`

---

## ✅ You're Live!

Your app is now running at: `https://newsletter-distiller.onrender.com`

**Next:**
1. Create an account
2. Connect your Gmail
3. Label emails with "To-Summarize"
4. Click "Process Newsletters Now"
5. View summaries in dashboard

---

## 📚 Full Guides

- [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md) - Detailed Render instructions
- [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - Complete checklist
- [WEB_APP_ARCHITECTURE.md](WEB_APP_ARCHITECTURE.md) - Architecture overview
- [WEB_APP_README.md](WEB_APP_README.md) - Full documentation

---

## ❓ Troubleshooting

| Issue | Solution |
|-------|----------|
| App won't start | Check Render Logs tab |
| Gmail auth fails | Verify redirect URI matches |
| Can't create account | Check database (run init command) |
| Processing doesn't work | Verify GOOGLE_CLIENT_* variables |

---

Generated: February 26, 2026 | Status: ✅ READY TO DEPLOY
