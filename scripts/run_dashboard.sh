#!/bin/bash
# Helper script to run dashboard with virtual environment

cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

# Run the dashboard
python dashboard.py "$@"
