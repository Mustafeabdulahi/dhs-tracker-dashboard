# ✅ Deployment Checklist

## Pre-Deployment

- [x] Dashboard working locally
- [x] `dashboard_v2.py` is the main file
- [x] `data/historical_arrests.json` exists with data
- [x] `requirements.txt` created (simplified for deployment)
- [x] `.streamlit/config.toml` created
- [x] `Procfile` created (for Heroku)
- [x] `runtime.txt` created
- [x] `README.md` created
- [x] `DEPLOYMENT_GUIDE.md` created
- [ ] `.gitignore` reviewed
- [ ] Test locally one more time

## Deployment Steps

### Quick Deploy (Recommended: Streamlit Cloud)

```bash
# Run the deployment helper script
./deploy.sh
```

OR manually:

```bash
# 1. Initialize Git
git init
git add .
git commit -m "Initial commit"

# 2. Create GitHub repo at https://github.com/new

# 3. Push to GitHub
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main

# 4. Deploy on Streamlit Cloud
# Go to: https://share.streamlit.io/
# - Sign in with GitHub
# - Click "New app"
# - Select your repo
# - Set main file: dashboard_v2.py
# - Click Deploy!
```

## Post-Deployment

- [ ] Verify dashboard loads
- [ ] Test all features:
  - [ ] KPI cards display correctly
  - [ ] Map renders
  - [ ] Top 10 Countries chart shows
  - [ ] Filters work
  - [ ] Search works
  - [ ] Pagination works
  - [ ] Data table displays
- [ ] Check on mobile
- [ ] Test different browsers
- [ ] Share URL with others
- [ ] Update README with live URL

## Maintenance

### Update Data
```bash
# 1. Run scraper locally
python3 dhs_tracker.py

# 2. Commit new data
git add data/historical_arrests.json
git commit -m "Update data - $(date +%Y-%m-%d)"
git push

# Platform will auto-redeploy
```

### Update Dashboard
```bash
# Make changes to dashboard_v2.py
git add dashboard_v2.py
git commit -m "Update dashboard: [description]"
git push
```

## Troubleshooting

### ❌ "Module not found"
**Fix**: Check `requirements.txt` - add missing package

### ❌ "File not found: data/historical_arrests.json"
**Fix**: Make sure file is committed:
```bash
git add data/historical_arrests.json
git commit -m "Add data file"
git push
```

### ❌ "Port binding failed"
**Fix**: Already handled in Procfile/config

### ❌ App is slow
**Fix**: 
- First load always slow (cold start)
- Consider paid tier for always-on
- Optimize data loading

## Platform-Specific Notes

### Streamlit Cloud
- ✅ Free forever
- ✅ Auto-redeploys on git push
- ✅ SSL certificate included
- ⚠️  Sleeps after inactivity
- ⚠️  30-second cold start

### Railway
- ✅ $5/month free credit
- ✅ Auto-redeploys
- ✅ Custom domains
- ⚠️  Credit runs out after ~500 hours

### Heroku
- ✅ Free tier available
- ✅ Wide documentation
- ✅ Reliable
- ⚠️  Sleeps after 30 min inactivity

## URLs to Bookmark

- **GitHub Repo**: `https://github.com/YOUR_USERNAME/YOUR_REPO`
- **Live Dashboard**: `[Add after deployment]`
- **Streamlit Cloud**: `https://share.streamlit.io/`
- **Deployment Logs**: `[Platform-specific]`

## Need Help?

1. Check `DEPLOYMENT_GUIDE.md` for detailed instructions
2. Review Streamlit docs: https://docs.streamlit.io/
3. Ask on Streamlit forum: https://discuss.streamlit.io/

---

**Ready to deploy?** Run `./deploy.sh` to get started! 🚀
