# Security Configuration for Heroku Deployment

## Environment Variables

All sensitive information MUST be stored as environment variables, never in code.

### Required Environment Variables

```bash
# Set on Heroku before deployment
ANTHROPIC_API_KEY=<your-api-key>
FLASK_SECRET_KEY=<random-secret-key>
```

### Setting Environment Variables

```bash
# On Heroku
heroku config:set ANTHROPIC_API_KEY="your_key" --app your-app-name
heroku config:set FLASK_SECRET_KEY="$(openssl rand -hex 32)" --app your-app-name

# Locally (create .env file - NEVER commit this)
echo "ANTHROPIC_API_KEY=your_key" > .env
echo "FLASK_SECRET_KEY=$(openssl rand -hex 32)" >> .env
```

## Security Checklist

### Before First Deployment
- [ ] Verify `.env` is in `.gitignore`
- [ ] Confirm no API keys in code
- [ ] Set `ANTHROPIC_API_KEY` on Heroku
- [ ] Set `FLASK_SECRET_KEY` on Heroku
- [ ] Configure GitHub secrets (HEROKU_API_KEY, HEROKU_APP_NAME, HEROKU_EMAIL)
- [ ] Review `.slugignore` to exclude sensitive files
- [ ] Ensure debug mode is disabled in production

### Regular Security Maintenance
- [ ] Rotate API keys every 90 days
- [ ] Rotate Flask secret key periodically
- [ ] Review Heroku access logs monthly
- [ ] Update dependencies regularly (`pip list --outdated`)
- [ ] Monitor for security advisories
- [ ] Review GitHub Actions workflow permissions

## Files That Must NEVER Be Committed

```
.env
.env.local
.env.production
*.db (database files with user data)
cookies.txt
config.json (if it contains secrets)
```

## Verification

Run this command to check for accidentally committed secrets:

```bash
# Check for .env in git history
git log --all --full-history -- .env

# Should return nothing. If it does, you need to remove it from history:
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all
```

## Production Security Settings

The following security measures are automatically enabled:

1. **HTTPS Only**: Heroku enforces HTTPS by default
2. **Debug Mode Off**: Automatically disabled when `PORT` env var is set
3. **Session Security**: Flask secret key used for session encryption
4. **Environment Isolation**: Production uses Heroku config vars, not .env files

## Incident Response

If an API key is compromised:

1. **Immediately** deactivate the old key at [console.anthropic.com](https://console.anthropic.com/settings/keys)
2. Generate a new API key
3. Update Heroku config: `heroku config:set ANTHROPIC_API_KEY="new_key" --app your-app-name`
4. Restart the app: `heroku restart --app your-app-name`
5. Review access logs for unauthorized usage
6. If key was committed to git, rewrite history (see Verification section)

## Monitoring

```bash
# Check for exposed secrets in logs
heroku logs --tail --app your-app-name | grep -i "api.*key"

# Should return nothing. If it does, fix logging to mask secrets.
```

## Additional Security Recommendations

1. **Enable Two-Factor Authentication**
   - Heroku account: [dashboard.heroku.com/account](https://dashboard.heroku.com/account)
   - GitHub account: Settings → Password and authentication
   - Anthropic account: [console.anthropic.com](https://console.anthropic.com)

2. **Limit Access**
   - Use Heroku teams to control app access
   - Review GitHub repository collaborators
   - Use least-privilege principle

3. **Regular Updates**
   ```bash
   # Check for outdated packages
   pip list --outdated
   
   # Update requirements.txt
   pip install --upgrade package-name
   pip freeze > requirements.txt
   ```

4. **Audit Logs**
   - Review Heroku activity: [dashboard.heroku.com/apps/your-app-name/activity](https://dashboard.heroku.com/apps/your-app-name/activity)
   - Review GitHub Actions runs
   - Check Anthropic API usage

## Contact

For security issues, contact the repository maintainer immediately. Do not open public issues for security vulnerabilities.
