# Heroku Deployment - Quick Reference

## Files Created for Deployment

### Core Heroku Files
- ✅ `Procfile` - Defines web dyno command (gunicorn)
- ✅ `runtime.txt` - Specifies Python version (3.11.9)
- ✅ `.slugignore` - Excludes test files and dev scripts from deployment

### CI/CD Configuration
- ✅ `.github/workflows/deploy.yml` - GitHub Actions workflow for auto-deployment

### Security & Configuration
- ✅ `.env.example` - Template for environment variables (never commit .env!)
- ✅ `.gitattributes` - Ensures proper line endings
- ✅ `.gitignore` - Updated to protect sensitive files
- ✅ `SECURITY.md` - Security best practices
- ✅ `HEROKU_DEPLOYMENT.md` - Comprehensive deployment guide

### Helper Scripts
- ✅ `heroku_setup.sh` - Automated Heroku configuration script

### Application Updates
- ✅ `requirements.txt` - Added gunicorn for production
- ✅ `dashboard.py` - Updated to use PORT env var and disable debug in production

## Quick Deployment Steps

### 1. Initial Setup (One-Time)

```bash
# Run automated setup
./heroku_setup.sh

# OR manually:
heroku create your-app-name
heroku buildpacks:add heroku/python
heroku buildpacks:add https://github.com/heroku/heroku-buildpack-google-chrome
heroku buildpacks:add https://github.com/heroku/heroku-buildpack-chromedriver
heroku config:set ANTHROPIC_API_KEY="your_key"
heroku config:set FLASK_SECRET_KEY="$(openssl rand -hex 32)"
```

### 2. GitHub Actions Setup (For Auto-Deployment)

**Add these secrets in GitHub repository settings:**
- `HEROKU_API_KEY` - Get with: `heroku auth:token`
- `HEROKU_APP_NAME` - Your Heroku app name
- `HEROKU_EMAIL` - Your Heroku account email

### 3. Deploy

**Automatic (via GitHub Actions):**
```bash
git push origin main
```

**Manual:**
```bash
git push heroku main
```

## Security Checklist

Before deploying:
- [ ] `.env` is in `.gitignore` ✅
- [ ] No API keys in code ✅
- [ ] `ANTHROPIC_API_KEY` set on Heroku
- [ ] `FLASK_SECRET_KEY` set on Heroku
- [ ] GitHub secrets configured
- [ ] Test files excluded via `.slugignore` ✅

## Common Commands

```bash
# View logs
heroku logs --tail --app your-app-name

# Restart app
heroku restart --app your-app-name

# Check status
heroku ps --app your-app-name

# View config
heroku config --app your-app-name

# Open app
heroku open --app your-app-name

# Run commands
heroku run python price_tracker.py --app your-app-name
```

## What Gets Deployed

**Included:**
- ✅ Core application files (dashboard.py, price_tracker.py, models.py, etc.)
- ✅ Templates and static files
- ✅ Requirements and configuration
- ✅ README and documentation

**Excluded (via .slugignore):**
- ❌ Test files (test_*.py, test_*.html)
- ❌ Development scripts (run_*.sh, setup.sh)
- ❌ Local data and databases
- ❌ Documentation files (Tasks.md, CurrentImplementation.md)
- ❌ Virtual environment and caches
- ❌ Git and IDE files

## Monitoring

```bash
# Stream logs
heroku logs --tail --app your-app-name

# Check for errors
heroku logs --tail --app your-app-name | grep ERROR

# View deployment history
heroku releases --app your-app-name

# Rollback if needed
heroku rollback --app your-app-name
```

## Troubleshooting

**Build fails:**
- Check buildpacks: `heroku buildpacks --app your-app-name`
- Review build logs: `heroku logs --tail --app your-app-name`

**App crashes:**
- Check logs: `heroku logs --tail --app your-app-name`
- Verify env vars: `heroku config --app your-app-name`
- Restart: `heroku restart --app your-app-name`

**Selenium/Chrome issues:**
- Verify Chrome buildpack is installed
- Check for memory limits (upgrade dyno if needed)

## Next Steps After Deployment

1. Visit your app: `https://your-app-name.herokuapp.com`
2. Add products to track via web interface
3. Consider adding Heroku Scheduler for automated checks
4. Set up monitoring/alerting
5. Review logs regularly

## Documentation

- **Full deployment guide**: [HEROKU_DEPLOYMENT.md](HEROKU_DEPLOYMENT.md)
- **Security guide**: [SECURITY.md](SECURITY.md)
- **Main README**: [README.md](README.md)

## Support

- Heroku docs: https://devcenter.heroku.com
- GitHub Actions: https://docs.github.com/actions
- Issues: Open an issue in the GitHub repository
