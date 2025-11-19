# Heroku Deployment Guide

## Overview

This guide explains how to deploy the AI Price Tracker to Heroku with automated CI/CD from GitHub Actions.

## Prerequisites

1. **Heroku Account**: Sign up at [heroku.com](https://heroku.com)
2. **GitHub Repository**: Your code must be in a GitHub repository
3. **Anthropic API Key**: Get one from [console.anthropic.com](https://console.anthropic.com/settings/keys)

## Initial Heroku Setup

### 1. Create Heroku App

```bash
# Install Heroku CLI (if not already installed)
brew install heroku/brew/heroku  # macOS
# or visit: https://devcenter.heroku.com/articles/heroku-cli

# Login to Heroku
heroku login

# Create a new Heroku app
heroku create your-app-name

# Note: If you don't specify a name, Heroku will generate a random one
```

### 2. Configure Environment Variables on Heroku

**CRITICAL: Set your API key before deploying**

```bash
# Set Anthropic API key (REQUIRED)
heroku config:set ANTHROPIC_API_KEY="your_actual_api_key_here" --app your-app-name

# Set Flask secret key for session security (RECOMMENDED)
heroku config:set FLASK_SECRET_KEY="$(openssl rand -hex 32)" --app your-app-name

# Verify environment variables are set
heroku config --app your-app-name
```

### 3. Add Chrome Buildpack for Selenium

The app uses Selenium with headless Chrome. Add the required buildpacks:

```bash
# Add Python buildpack (primary)
heroku buildpacks:add heroku/python --app your-app-name

# Add Chrome and ChromeDriver buildpacks for Selenium
heroku buildpacks:add https://github.com/heroku/heroku-buildpack-google-chrome --app your-app-name
heroku buildpacks:add https://github.com/heroku/heroku-buildpack-chromedriver --app your-app-name

# Verify buildpacks
heroku buildpacks --app your-app-name
```

## GitHub Actions CI/CD Setup

### 1. Get Heroku API Key

```bash
# Get your Heroku API key
heroku auth:token
```

Copy the token that's displayed.

### 2. Configure GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions → New repository secret

Add these three secrets:

1. **HEROKU_API_KEY**: Your Heroku API token from step 1
2. **HEROKU_APP_NAME**: Your Heroku app name (e.g., `your-app-name`)
3. **HEROKU_EMAIL**: The email you use for your Heroku account

### 3. Automatic Deployment

Once configured, every push to the `main` branch will:
1. ✅ Trigger the GitHub Actions workflow
2. ✅ Deploy to Heroku automatically
3. ✅ Run migrations and start the app

You can also trigger manual deployment from GitHub Actions tab.

## What Gets Deployed

The `.slugignore` file excludes unnecessary files from deployment:
- ❌ Test files (`test_*.py`)
- ❌ Development scripts (`run_*.sh`, `setup.sh`)
- ❌ Documentation files (`Tasks.md`, `CurrentImplementation.md`)
- ❌ Local data and database files
- ✅ Only production-ready code is deployed

## Security Features

### 1. Environment Variables Protection
- `.env` file is **never** committed to git (blocked by `.gitignore`)
- API keys stored as Heroku config vars
- GitHub Actions uses encrypted secrets

### 2. Secret Key Rotation
```bash
# Rotate Flask secret key if needed
heroku config:set FLASK_SECRET_KEY="$(openssl rand -hex 32)" --app your-app-name
```

### 3. API Key Management
```bash
# Update Anthropic API key
heroku config:set ANTHROPIC_API_KEY="new_key_here" --app your-app-name

# View configured variables (values are masked)
heroku config --app your-app-name
```

## Monitoring & Logs

### View Application Logs
```bash
# Stream live logs
heroku logs --tail --app your-app-name

# View recent logs
heroku logs --num=100 --app your-app-name

# Filter for errors only
heroku logs --tail --app your-app-name | grep ERROR
```

### Check App Status
```bash
# Check dyno status
heroku ps --app your-app-name

# Restart app if needed
heroku restart --app your-app-name
```

## Database Management

The app uses SQLite by default. For production, consider upgrading to PostgreSQL:

```bash
# Add PostgreSQL addon (free tier available)
heroku addons:create heroku-postgresql:mini --app your-app-name

# This automatically sets DATABASE_URL environment variable
```

## Troubleshooting

### Deployment Fails
```bash
# Check build logs
heroku logs --tail --app your-app-name

# Common issues:
# 1. Missing buildpacks → Add Chrome buildpacks (see step 3 above)
# 2. Missing dependencies → Check requirements.txt
# 3. Missing API key → Set ANTHROPIC_API_KEY
```

### App Crashes on Start
```bash
# Check error logs
heroku logs --tail --app your-app-name

# Restart the app
heroku restart --app your-app-name

# Check dyno status
heroku ps --app your-app-name
```

### Chrome/Selenium Issues
```bash
# Verify buildpacks are installed
heroku buildpacks --app your-app-name

# Should show:
# 1. heroku/python
# 2. heroku-buildpack-google-chrome
# 3. heroku-buildpack-chromedriver
```

## Manual Deployment (Alternative)

If you prefer manual deployment without GitHub Actions:

```bash
# Add Heroku remote (if not already added)
heroku git:remote --app your-app-name

# Deploy manually
git push heroku main

# View logs
heroku logs --tail --app your-app-name
```

## Scaling

```bash
# Check current dyno configuration
heroku ps --app your-app-name

# Scale up web dynos (costs apply beyond free tier)
heroku ps:scale web=2 --app your-app-name

# Scale down
heroku ps:scale web=1 --app your-app-name
```

## Cost Management

**Free Tier Limits:**
- 550-1000 free dyno hours/month (verified account)
- App sleeps after 30 minutes of inactivity
- No cost for basic deployment

**Paid Features:**
- Hobby tier ($7/mo) - No sleep, custom domains
- Professional tier - Advanced features, autoscaling

## Useful Commands

```bash
# Open app in browser
heroku open --app your-app-name

# Run one-off commands
heroku run python price_tracker.py --app your-app-name

# Access bash shell
heroku run bash --app your-app-name

# View all config vars
heroku config --app your-app-name

# Delete an app (careful!)
heroku apps:destroy --app your-app-name --confirm your-app-name
```

## Security Checklist

- ✅ `.env` file is in `.gitignore`
- ✅ API keys stored as Heroku config vars
- ✅ GitHub secrets configured for CI/CD
- ✅ Flask secret key set for session security
- ✅ Debug mode disabled in production
- ✅ No sensitive files in `.slugignore` deployed
- ✅ HTTPS enabled by default on Heroku

## Support

- **Heroku Documentation**: [devcenter.heroku.com](https://devcenter.heroku.com)
- **GitHub Actions**: [docs.github.com/actions](https://docs.github.com/actions)
- **Anthropic API**: [docs.anthropic.com](https://docs.anthropic.com)

## Next Steps

After deployment:
1. Visit your app URL: `https://your-app-name.herokuapp.com`
2. Add products to track
3. Monitor logs for any issues
4. Set up scheduled tasks (Heroku Scheduler addon) for automatic price checks
