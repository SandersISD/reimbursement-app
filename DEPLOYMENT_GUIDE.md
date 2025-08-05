# 🚀 Deployment Guide - Reimbursement Management System

## Option 1: Render.com (Recommended - Free & Easy)

### Step 1: Push to GitHub
```bash
# Create a new repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/reimbursement-app.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy on Render
1. **Go to [render.com](https://render.com)** and sign up/login
2. **Click "New +"** → **"Blueprint"**
3. **Connect your GitHub repository**
4. **Repository**: Select your `reimbursement-app` repo
5. **Blueprint Name**: `reimbursement-system`
6. **Click "Apply"**

**That's it!** Render will automatically:
- ✅ Create a PostgreSQL database
- ✅ Build your application
- ✅ Deploy with auto-SSL
- ✅ Provide a public URL

### Step 3: Initialize Database (One-time)
After deployment, run this once in the Render shell:
```bash
python init_production_db.py
```

---

## Option 2: Heroku (Classic Choice)

### Step 1: Install Heroku CLI
```bash
# macOS
brew tap heroku/brew && brew install heroku

# Login
heroku login
```

### Step 2: Create Heroku App
```bash
# Create app
heroku create your-reimbursement-app

# Add PostgreSQL
heroku addons:create heroku-postgresql:mini

# Set environment variables
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=$(openssl rand -hex 32)
```

### Step 3: Deploy
```bash
git push heroku main

# Initialize database
heroku run python init_production_db.py

# Open your app
heroku open
```

---

## Option 3: Fly.io (Modern Platform)

### Step 1: Install Fly CLI
```bash
curl -L https://fly.io/install.sh | sh
fly auth login
```

### Step 2: Deploy
```bash
fly launch
# Follow prompts:
# - App name: reimbursement-app
# - Region: Choose closest to you
# - PostgreSQL: Yes
# - Deploy now: Yes
```

### Step 3: Initialize Database
```bash
fly ssh console
python init_production_db.py
exit
```

---

## Option 4: DigitalOcean App Platform

### Step 1: Create App
1. **Go to [DigitalOcean](https://www.digitalocean.com/products/app-platform)**
2. **Create App** → **GitHub** → Select your repo
3. **Configure**:
   - **Name**: `reimbursement-system`
   - **Plan**: Basic ($5/month)
   - **Environment**: Production

### Step 2: Add Database
1. **Add Component** → **Database** → **PostgreSQL**
2. **Plan**: Basic ($15/month)

### Step 3: Environment Variables
Add these in the App settings:
```
FLASK_ENV=production
SECRET_KEY=(generate a random 32-character string)
```

---

## Environment Variables for All Platforms

```bash
# Required
FLASK_ENV=production
SECRET_KEY=your-secret-key-here

# Database (auto-provided by most platforms)
DATABASE_URL=postgresql://...

# Optional
MAX_CONTENT_LENGTH=16777216
```

---

## Production Checklist

### ✅ Before Deployment
- [x] Git repository created
- [x] requirements.txt generated
- [x] Procfile configured
- [x] render.yaml configured
- [x] Environment variables ready
- [x] PostgreSQL support added

### ✅ After Deployment
- [ ] Database initialized
- [ ] Test file uploads
- [ ] Test claim creation
- [ ] Verify email notifications (if added)
- [ ] Set up monitoring
- [ ] Configure backups

---

## Post-Deployment Setup

### 1. Test Your Deployment
```bash
# Test the homepage
curl https://your-app.render.com

# Test API health
curl https://your-app.render.com/
```

### 2. Monitor Your App
- **Render**: Built-in metrics and logs
- **Heroku**: `heroku logs --tail`
- **Fly.io**: `fly logs`

### 3. Custom Domain (Optional)
Most platforms support custom domains:
1. **Render**: Settings → Custom Domains
2. **Heroku**: `heroku domains:add yourdomain.com`
3. **Fly.io**: `fly certs create yourdomain.com`

---

## Scaling & Performance

### Free Tier Limitations
- **Render**: 750 hours/month, sleeps after 15min inactive
- **Heroku**: 1000 hours/month, sleeps after 30min inactive
- **Fly.io**: 160GB-hours/month

### Production Recommendations
- **Paid plan** for 24/7 uptime
- **Database backups** enabled
- **CDN** for file uploads (AWS S3 + CloudFront)
- **Monitoring** (Sentry, DataDog)

---

## Next Steps

1. **Choose a platform** (Render.com recommended for beginners)
2. **Push to GitHub** and deploy
3. **Test thoroughly** with real data
4. **Add custom domain** if needed
5. **Set up monitoring** and backups

**Your reimbursement system will be live on the internet!** 🎉

---

## Support & Troubleshooting

### Common Issues
- **Database connection**: Check DATABASE_URL
- **File uploads**: Verify upload directory permissions
- **Static files**: Ensure Bootstrap CDN is accessible
- **Forms not working**: Check CSRF token configuration

### Debugging
```bash
# Render
Check logs in Render dashboard

# Heroku
heroku logs --tail

# Fly.io
fly logs
```
