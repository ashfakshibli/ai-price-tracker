#!/usr/bin/env python3
"""
Web dashboard for AI Price Tracker.
"""

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

app = Flask(__name__)
app.secret_key = os.urandom(24)

CONFIG_FILE = "config.json"
DATA_DIR = Path("data")
LOG_FILE = "tracker.log"


def load_config():
    """Load configuration from JSON file."""
    if Path(CONFIG_FILE).exists():
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {"products": [], "check_interval_hours": 1, "notifications": {"terminal": True, "email": False}}


def save_config(config):
    """Save configuration to JSON file."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)


def get_product_history(product_id):
    """Get historical data for a product."""
    data_file = DATA_DIR / f"{product_id}.json"
    if data_file.exists():
        with open(data_file, 'r') as f:
            return json.load(f)
    return None


def get_all_products_with_history():
    """Get all products with their latest data."""
    config = load_config()
    products = []

    for product in config.get('products', []):
        import hashlib
        product_id = hashlib.md5(product['url'].encode()).hexdigest()[:12]

        history_data = get_product_history(product_id)
        latest = history_data.get('current') if history_data else None

        products.append({
            'id': product_id,
            'config': product,
            'latest': latest,
            'history_count': len(history_data.get('history', [])) if history_data else 0
        })

    return products


def get_cron_status():
    """Check if cron job exists."""
    try:
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        if result.returncode == 0:
            return 'price_tracker.py' in result.stdout
        return False
    except:
        return False


def get_cron_command():
    """Get the cron command that would be added."""
    script_dir = Path.cwd()
    python_path = subprocess.run(['which', 'python3'], capture_output=True, text=True).stdout.strip()
    return f"0 * * * * cd {script_dir} && {python_path} price_tracker.py >> {script_dir}/tracker.log 2>&1"


@app.route('/')
def index():
    """Main dashboard page."""
    products = get_all_products_with_history()
    cron_active = get_cron_status()
    cron_command = get_cron_command()

    return render_template('index.html',
                         products=products,
                         cron_active=cron_active,
                         cron_command=cron_command)


@app.route('/api/products')
def api_products():
    """Get products list as JSON."""
    products = get_all_products_with_history()
    return jsonify({'products': products, 'count': len(products)})


@app.route('/api/logs')
def api_logs():
    """Get recent log entries as JSON."""
    lines = request.args.get('lines', 50, type=int)

    log_entries = []
    if Path(LOG_FILE).exists():
        with open(LOG_FILE, 'r') as f:
            log_entries = f.readlines()[-lines:]

    return jsonify({'logs': log_entries, 'count': len(log_entries)})


@app.route('/api/check_url')
def api_check_url():
    """Check if a URL is already being tracked."""
    url = request.args.get('url', '')

    if not url:
        return jsonify({'exists': False})

    config = load_config()
    exists = any(product['url'] == url for product in config['products'])

    return jsonify({'exists': exists, 'url': url})


@app.route('/api/product/<int:product_id>')
def api_product(product_id):
    """Get a single product with history."""
    products = get_all_products_with_history()

    for product in products:
        if product['id'] == product_id:
            return jsonify(product)

    return jsonify({'error': 'Product not found'}), 404


@app.route('/add_product', methods=['POST'])
def add_product():
    """Add a new product to track."""
    name = request.form.get('name')
    url = request.form.get('url')
    notify_price = request.form.get('notify_price') == 'on'
    notify_availability = request.form.get('notify_availability') == 'on'
    track_variants = request.form.get('track_variants') == 'on'

    if not name or not url:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'Name and URL are required!'}), 400
        flash('Name and URL are required!', 'error')
        return redirect(url_for('index'))

    config = load_config()
    config['products'].append({
        'name': name,
        'url': url,
        'notify_on_price_drop': notify_price,
        'notify_on_availability': notify_availability,
        'track_variants': track_variants
    })
    save_config(config)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True, 'message': f'Added {name} to tracking!', 'product': {'name': name, 'url': url}})

    flash(f'Added {name} to tracking!', 'success')
    return redirect(url_for('index'))


@app.route('/remove_product/<product_id>')
def remove_product(product_id):
    """Remove a product from tracking."""
    config = load_config()

    # Find and remove product
    for i, product in enumerate(config['products']):
        import hashlib
        pid = hashlib.md5(product['url'].encode()).hexdigest()[:12]
        if pid == product_id:
            removed = config['products'].pop(i)
            save_config(config)
            flash(f'Removed {removed["name"]} from tracking!', 'success')
            break

    return redirect(url_for('index'))


@app.route('/history/<product_id>')
def history(product_id):
    """View history for a specific product."""
    config = load_config()

    # Find product config
    product_config = None
    for product in config.get('products', []):
        import hashlib
        pid = hashlib.md5(product['url'].encode()).hexdigest()[:12]
        if pid == product_id:
            product_config = product
            break

    if not product_config:
        flash('Product not found!', 'error')
        return redirect(url_for('index'))

    history_data = get_product_history(product_id)

    if not history_data:
        flash('No history data available yet!', 'warning')
        return redirect(url_for('index'))

    return render_template('history.html',
                         product=product_config,
                         product_id=product_id,
                         current=history_data.get('current'),
                         history=history_data.get('history', []))


@app.route('/logs')
def logs():
    """View tracker logs."""
    log_content = []

    if Path(LOG_FILE).exists():
        with open(LOG_FILE, 'r') as f:
            log_content = f.readlines()[-500:]  # Last 500 lines

    return render_template('logs.html', logs=log_content)


@app.route('/enable_cron', methods=['POST'])
def enable_cron():
    """Enable cron job."""
    try:
        cron_command = get_cron_command()

        # Get existing crontab
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        existing_cron = result.stdout if result.returncode == 0 else ""

        # Check if already exists
        if 'price_tracker.py' in existing_cron:
            flash('Cron job already exists!', 'warning')
            return redirect(url_for('index'))

        # Add new cron job
        new_cron = existing_cron + cron_command + "\n"

        # Write to crontab
        process = subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE, text=True)
        process.communicate(input=new_cron)

        flash('Cron job enabled! Tracker will run hourly.', 'success')
    except Exception as e:
        flash(f'Error enabling cron: {e}', 'error')

    return redirect(url_for('index'))


@app.route('/disable_cron', methods=['POST'])
def disable_cron():
    """Disable cron job."""
    try:
        # Get existing crontab
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)

        if result.returncode != 0:
            flash('No cron jobs found!', 'warning')
            return redirect(url_for('index'))

        # Remove price tracker lines
        lines = result.stdout.split('\n')
        new_lines = [line for line in lines if 'price_tracker.py' not in line]
        new_cron = '\n'.join(new_lines)

        # Write to crontab
        process = subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE, text=True)
        process.communicate(input=new_cron)

        flash('Cron job disabled!', 'success')
    except Exception as e:
        flash(f'Error disabling cron: {e}', 'error')

    return redirect(url_for('index'))


@app.route('/run_now', methods=['POST'])
def run_now():
    """Run tracker manually now."""
    try:
        flash('Starting manual tracking run...', 'info')
        # Run in background
        subprocess.Popen(['python3', 'price_tracker.py'],
                        stdout=open('tracker.log', 'a'),
                        stderr=subprocess.STDOUT)
        flash('Tracker is running! Check logs for progress.', 'success')
    except Exception as e:
        flash(f'Error running tracker: {e}', 'error')

    return redirect(url_for('index'))


if __name__ == '__main__':
    # Create data directory if it doesn't exist
    DATA_DIR.mkdir(exist_ok=True)

    print("=" * 60)
    print("AI Price Tracker Dashboard")
    print("=" * 60)
    print("\nStarting web server...")
    print("Dashboard URL: http://localhost:5000")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60)

    app.run(debug=True, host='0.0.0.0', port=5000)
