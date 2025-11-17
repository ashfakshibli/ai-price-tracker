#!/bin/bash
# Helper script to run price tracker with virtual environment

cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

# Run the price tracker
python price_tracker.py "$@"
