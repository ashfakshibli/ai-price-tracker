# Scripts

This directory contains helper scripts for development and deployment.

## Development Scripts

- `activate_venv.sh` - Activate virtual environment
- `run_dashboard.sh` - Start the web dashboard
- `run_tracker.sh` - Run the price tracker once

## Setup Scripts

- `setup.sh` - Initial project setup
- `setup_cron.sh` - Setup local cron jobs
- `setup_heroku_scheduler.sh` - Setup Heroku Scheduler addon

## Deployment Scripts

- `heroku_setup.sh` - Automated Heroku setup

## Usage

All scripts should be run from the project root:

```bash
# Make scripts executable
chmod +x scripts/*.sh

# Run a script
./scripts/run_dashboard.sh
```
