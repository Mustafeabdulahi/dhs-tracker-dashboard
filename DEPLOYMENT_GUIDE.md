# 🚀 Deployment Guide

This guide will help you deploy your DHS Tracker Dashboard to the web.

## 📋 Pre-Deployment Checklist

- [x] Dashboard working locally (`streamlit run dashboard_v2.py`)
- [ ] Git repository initialized
- [ ] Data file included (`data/historical_arrests.json`)
- [ ] Requirements file created
- [ ] Streamlit config created
- [ ] Choose deployment platform

---

## 🌟 Option 1: Streamlit Community Cloud (RECOMMENDED - FREE)

**Best for**: Quick deployment, free hosting, automatic updates

### Steps:

1. **Initialize Git Repository**
   ```bash
   cd /Users/mustafeabdulahi/Desktop/ice_arrest_tracker
   git init
   git add .
   git commit -m "Initial commit - DHS Tracker Dashboard"
   ```

2. **Create GitHub Repository**
   - Go to https://github.com/new
   - Create a new repository (e.g., "dhs-tracker-dashboard")
   - Don't initialize with README (you already have one)

3. **Push to GitHub**
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/dhs-tracker-dashboard.git
   git branch -M main
   git push -u origin main
   ```

4. **Deploy on Streamlit Cloud**
   - Go to https://share.streamlit.io/
   - Sign in with GitHub
   - Click "New app"
   - Select your repository
   - Set main file path: `dashboard_v2.py`
   - Click "Deploy"!

**✅ Done!** Your app will be live at `https://YOUR_USERNAME-dhs-tracker-dashboard.streamlit.app`

---

## 🐳 Option 2: Docker + Any Cloud Platform

**Best for**: Full control, scalability

### Create Dockerfile:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "dashboard_v2.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Deploy to:
- **Heroku**: `heroku container:push web && heroku container:release web`
- **Railway**: Connect GitHub repo, auto-deploys
- **Render**: Connect GitHub repo, select "Docker"
- **Google Cloud Run**: `gcloud run deploy`
- **AWS**: Use ECS or Elastic Beanstalk

---

## 🔧 Option 3: Railway (FREE TIER)

**Best for**: Simple deployment, generous free tier

### Steps:

1. **Push to GitHub** (same as Option 1, steps 1-3)

2. **Deploy on Railway**
   - Go to https://railway.app/
   - Sign up/login with GitHub
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Railway auto-detects Streamlit
   - Add environment variable: `PORT=8501`
   - Click "Deploy"

**✅ Done!** Your app will be live with a Railway URL.

---

## 🌐 Option 4: Heroku (FREE TIER)

**Best for**: Traditional PaaS experience

### Files Needed:

**Procfile:**
```
web: streamlit run dashboard_v2.py --server.port=$PORT --server.address=0.0.0.0
```

**runtime.txt:**
```
python-3.9.16
```

### Deploy:
```bash
heroku login
heroku create your-app-name
git push heroku main
heroku open
```

---

## 📊 Post-Deployment

### 1. **Verify Everything Works**
   - [ ] Dashboard loads
   - [ ] Charts render correctly
   - [ ] Filters work
   - [ ] Data table displays
   - [ ] Search functionality works

### 2. **Update Data**
   To update the data:
   - Run `python3 dhs_tracker.py` locally
   - Commit new `historical_arrests.json`
   - Push to GitHub
   - Platform will auto-redeploy

### 3. **Monitor Usage**
   - Check Streamlit Cloud analytics
   - Monitor response times
   - Review error logs

### 4. **Share Your Dashboard**
   - Add URL to README.md
   - Share on social media
   - Add to your portfolio

---

## 🔒 Security Notes

- Data is public (no sensitive info)
- No authentication needed for viewing
- Consider adding basic auth if needed
- Rate limiting handled by platform

---

## 💡 Tips

- **Free Tier Limits**: Most platforms sleep after inactivity
- **Wake Time**: First load may take 30-60 seconds
- **Updates**: Push to GitHub to update
- **Custom Domain**: Available on paid tiers
- **SSL**: Automatically provided by all platforms

---

## 🆘 Troubleshooting

### Issue: "Module not found"
**Solution**: Check `requirements.txt` has all dependencies

### Issue: "Data file not found"
**Solution**: Ensure `data/historical_arrests.json` is committed

### Issue: "Port already in use"
**Solution**: Use `--server.port=8502` or kill other Streamlit processes

### Issue: "Memory limit exceeded"
**Solution**: Optimize data loading, consider paid tier

---

## 📞 Support

Need help? Common resources:
- Streamlit Docs: https://docs.streamlit.io/
- Streamlit Forum: https://discuss.streamlit.io/
- GitHub Issues: [Your repo]/issues

---

## ✅ Quick Start Deployment (Streamlit Cloud)

```bash
# 1. Initialize git
cd /Users/mustafeabdulahi/Desktop/ice_arrest_tracker
git init
git add .
git commit -m "Initial commit"

# 2. Create GitHub repo and push
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main

# 3. Go to share.streamlit.io and deploy!
```

**That's it! Your dashboard is live!** 🎉
