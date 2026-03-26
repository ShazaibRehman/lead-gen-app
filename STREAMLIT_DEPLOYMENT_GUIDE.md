# 🚀 Streamlit Lead Generation App - Deployment Guide

## Overview

Your Streamlit app is ready to deploy! This guide will walk you through deploying it to **Streamlit Cloud** (free) so clients can access it from any browser.

---

## What You Get

✅ **Free Hosting** - No monthly costs
✅ **Live URL** - Share a direct link with clients
✅ **24/7 Availability** - App runs on Streamlit's servers
✅ **Simple Updates** - Push new versions with a git push
✅ **Professional** - Your branded lead generation platform

---

## Step 1: Prepare Your Files

You need to create a GitHub repository with these files:

### Directory Structure:
```
lead-gen-repo/
├── streamlit_app.py          ← Your Streamlit app
├── requirements.txt          ← Python dependencies
├── credentials.json          ← API keys (OPTIONAL - see note below)
└── README.md                 ← Documentation
```

### File 1: requirements.txt

```
streamlit==1.28.1
pandas==2.0.3
requests==2.31.0
openpyxl==3.1.2
```

Save this as `requirements.txt` in your repo.

### File 2: credentials.json

**IMPORTANT SECURITY NOTE:**
- DO NOT commit credentials.json to GitHub
- Instead, use Streamlit Secrets (explained in Step 3)
- Or add to `.gitignore`

### File 3: streamlit_app.py

Already created! Located at:
`/sessions/loving-focused-ride/mnt/Linkedin scraper/streamlit_app.py`

---

## Step 2: Create GitHub Repository

1. **Go to GitHub**: https://github.com/new
2. **Create repository**:
   - Name: `lead-gen-app` (or similar)
   - Description: "Lead Generation Platform"
   - Public (required for free Streamlit Cloud)
   - Initialize with README
3. **Clone locally**:
   ```bash
   git clone https://github.com/YOUR-USERNAME/lead-gen-app.git
   cd lead-gen-app
   ```
4. **Add files**:
   - Copy `streamlit_app.py` into the repo
   - Create `requirements.txt` with content above
   - Create `README.md` (see template below)
5. **Commit and push**:
   ```bash
   git add .
   git commit -m "Initial commit: Lead generation app"
   git push origin main
   ```

---

## Step 3: Deploy to Streamlit Cloud

### 3a. Sign Up for Streamlit Cloud
1. Go to: https://streamlit.io/cloud
2. Click "Sign Up"
3. Sign in with your GitHub account
4. Authorize Streamlit to access your repos

### 3b. Deploy Your App
1. Go to: https://share.streamlit.io
2. Click "New app"
3. Fill in:
   - **Repository**: YOUR-USERNAME/lead-gen-app
   - **Branch**: main
   - **Main file path**: streamlit_app.py
4. Click "Deploy"

Streamlit will:
- Install dependencies from requirements.txt
- Launch your app
- Give you a URL like: `https://your-app-name.streamlit.app`

### 3c. Add API Credentials (IMPORTANT!)

1. In Streamlit Cloud, go to your app settings
2. Click "Secrets"
3. Add your API keys:
   ```toml
   google_places_api_key = "YOUR_ACTUAL_KEY"
   serpapi_api_key = "YOUR_ACTUAL_KEY"
   ```
4. Save

4. **Update your app code** to read from secrets:
   ```python
   import streamlit as st

   google_key = st.secrets["google_places_api_key"]
   serpapi_key = st.secrets["serpapi_api_key"]
   ```

---

## Step 4: Share with Clients

Once deployed, you'll have a URL like:
```
https://lead-gen-app.streamlit.app
```

**Share this link with clients!** They can:
1. Open in browser
2. Enter search criteria
3. Get results instantly
4. Download Excel/CSV files

---

## README.md Template

```markdown
# 🎯 Lead Generation Platform

Professional lead generation tool powered by Google Places API and SerpAPI.

## Features

- 🔍 Search any industry and location
- 👔 Find executives at target companies
- 📊 Download as Excel or CSV
- ⚡ Instant results

## How to Use

1. Enter business type (e.g., "law firms")
2. Enter location (e.g., "Florida")
3. Set number of results (5-50)
4. Click "Generate Leads"
5. Download results as Excel or CSV

## Examples

- "mental health recovery centers in Texas"
- "real estate agencies in New York"
- "consulting firms in Los Angeles"

## Support

For issues or questions, contact: support@glasshouseagency.com

---

Built with Streamlit | © 2026 Glasshouse Agency
```

---

## Common Issues & Fixes

### "ModuleNotFoundError: No module named 'streamlit'"
- **Fix**: Make sure `requirements.txt` is in the repo root
- Streamlit Cloud will install it automatically

### "Credentials not found"
- **Fix**: Use Streamlit Secrets (Step 3c)
- Don't commit credentials.json to GitHub

### "API Error: 403"
- **Fix**: Check API key validity in Streamlit Secrets
- Verify Google Places and SerpAPI accounts are active

### "App runs slow"
- **Fix**: Normal on free tier - results take 1-2 minutes
- Upgrade to Streamlit Pro for faster servers

---

## Monitoring & Updates

### View Logs
- Streamlit Cloud dashboard → Your app → "View Logs"
- See real-time errors and user activity

### Deploy Updates
```bash
# Make code changes
git add .
git commit -m "Update: Improved search logic"
git push origin main
# Streamlit Cloud auto-deploys!
```

### Performance Tips
- Add caching for API results
- Optimize retry logic
- Monitor API quota usage

---

## Cost Analysis

| Item | Cost | Notes |
|------|------|-------|
| Streamlit Cloud | FREE | Up to 3 apps |
| Google Places API | $17/1000 | High volume |
| SerpAPI | $20/month | Up to 100/month free |
| **Total** | **Minimal** | Add-as-you-scale |

---

## Next Steps

1. ✅ Prepare files locally
2. ✅ Create GitHub repo
3. ✅ Deploy to Streamlit Cloud
4. ✅ Configure API secrets
5. ✅ Test the app
6. ✅ Share URL with clients

**You'll have a live lead generation platform in 30 minutes!** 🚀

---

## Support Resources

- **Streamlit Docs**: https://docs.streamlit.io
- **Streamlit Community**: https://discuss.streamlit.io
- **API Docs**:
  - Google Places: https://developers.google.com/maps/documentation/places/web-service
  - SerpAPI: https://serpapi.com/docs

---

**Questions?** Email: support@glasshouseagency.com
