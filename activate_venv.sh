#!/bin/bash
# Quick activation script for the virtual environment
# Usage: source activate_venv.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/venv/bin/activate"

echo "✓ Virtual environment activated"
echo "  Python: $(which python)"
echo "  API Key: $(python -c "import os; from dotenv import load_dotenv; from pathlib import Path; load_dotenv(Path('.env')); k=os.getenv('ANTHROPIC_API_KEY'); print('Set (' + k[:20] + '...)' if k else 'Not found')")"
