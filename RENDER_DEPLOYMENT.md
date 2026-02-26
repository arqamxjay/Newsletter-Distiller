# Deploy to Render - Step by Step Guide

## What is Render?
Render is a modern cloud platform with a **free tier** that requires no credit card for basic deployments.

## Prerequisites
✅ Git repository initialized (done)  
✅ GitHub account (needed)  
✅ Render account (free)

---

## Step 1: Create GitHub Repository

1. Go to [github.com/new](https://github.com/new)
2. Repository name: `newsletter-distiller`
3. Click **Create repository**
4. Copy the commands to push your local repo:

```bash
cd "/Users/prom1/Desktop/Newsletter Distiller"

# Add remote
git remote add origin https://github.com/YOUR_USERNAME/newsletter-distiller.git

# Rename branch to main (if needed)
git branch -M main

# Push to GitHub
git push -u origin main
```

---

## Step 2: Sign Up for Render

1. Go to [render.com](https://render.com)
2. Click **Sign Up**
3. Sign up with GitHub (easier)
4. Authorize Render to access your GitHub account

---

## Step 3: Create a New Web Service on Render

1. Go to [dashboard.render.com](https://dashboard.render.com)
2. Click **New +** → **Web Service**
3. Select **Connect a repository**
4. Find and select `newsletter-distiller`
5. Click **Connect**

---

## Step 4: Configure the Web Service

Fill in the form:

| Setting | Value |
|---------|-------|
| **Name** | newsletter-distiller |
| **Environment** | Python 3 |
| **Region** | Any (e.g., us-east) |
| **Branch** | main |
| **Build Command** | `pip install -r requirements_web.txt` |
| **Start Command** | `gunicorn wsgi:app` |

---

## Step 5: Add Environment Variables

Click **Environment** and add these variables:

```
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-here-change-this
DATABASE_URL=sqlite:///newsletter_distiller.db
GMAIL_CREDENTIALS_FILE=credentials.json
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

**Get your Google Cloud credentials:**
1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create OAuth 2.0 credentials
3. Add redirect URI: `https://your-render-app.onrender.com/gmail/callback`

---

## Step 6: Deploy

Click **Create Web Service**

Render will automatically:
- Install dependencies
- Build your app
- Deploy it live
- Provide a URL like: `https://newsletter-distiller.onrender.com`

---

## Step 7: Initialize Database on Render

After deployment, run this in Render's shell:

```bash
python -c "from app import create_app, db; app = create_app('production'); with app.app_context(): db.create_all()"
```

Or go to your Render dashboard → **Shell** tab and run it there.

---

## Testing Your Deployment

1. Visit your URL: `https://newsletter-distiller.onrender.com`
2. Create an account
3. Connect your Gmail
4. Test processing a newsletter

---

## Troubleshooting

### App won't start
Check logs: Render Dashboard → **Logs** tab

### Gmail connection fails
- Verify OAuth redirect URI matches your Render URL
- Check credentials in environment variables

### Database errors
- Run initialization command in Shell tab
- Check `DATABASE_URL` environment variable

---

## Scaling Up (Optional)

For production with more users:
1. Upgrade to paid plan ($7+/month)
2. Add PostgreSQL database addon
3. Add Redis for background jobs
4. Scale with multiple instances

---

## Monitoring

- **Logs**: Render Dashboard → Logs
- **Health**: Render Dashboard → Health
- **Metrics**: Available on paid plans

---

## Next Steps

After deployment:
1. ✅ Share your app URL with users
2. ✅ Add custom domain (optional)
3. ✅ Set up SSL (automatic on Render)
4. ✅ Monitor usage in dashboard

---

**Your app is now live! 🎉**

Share your Render URL with users and they can:
- Sign up
- Connect their Gmail
- Process newsletters
- See summaries in dashboard

