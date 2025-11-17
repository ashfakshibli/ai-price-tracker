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
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

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

    for index, product in enumerate(config.get('products', [])):
        import hashlib
        from favicon_utils import get_or_fetch_favicon

        product_id = hashlib.md5(product['url'].encode()).hexdigest()[:12]

        history_data = get_product_history(product_id)
        latest = history_data.get('current') if history_data else None

        # Get favicon for the product's website
        favicon_path = get_or_fetch_favicon(product['url'])

        products.append({
            'id': index,  # Use array index as ID
            'hash_id': product_id,  # Keep hash for file lookup
            'config': product,
            'latest': latest,
            'history_count': len(history_data.get('history', [])) if history_data else 0,
            'history': history_data.get('history', []) if history_data else [],
            'favicon': favicon_path  # Add favicon path
        })

    return products


def get_cron_status():
    """Check if cron job exists and get its frequency."""
    try:
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        if result.returncode == 0 and 'price_tracker.py' in result.stdout:
            # Extract frequency from cron expression
            for line in result.stdout.split('\n'):
                if 'price_tracker.py' in line:
                    parts = line.strip().split()
                    if len(parts) >= 5:
                        # Parse cron schedule
                        minute = parts[0]
                        hour = parts[1]

                        # Determine frequency
                        if minute.startswith('*/'):
                            # Every X minutes
                            freq = int(minute[2:])
                            return {'active': True, 'frequency': freq}
                        elif minute == '0':
                            # Hourly or multi-hourly
                            if hour.startswith('*/'):
                                freq = int(hour[2:]) * 60
                                return {'active': True, 'frequency': freq}
                            elif hour == '*':
                                return {'active': True, 'frequency': 60}

            return {'active': True, 'frequency': 60}  # Default to hourly
        return {'active': False, 'frequency': None}
    except:
        return {'active': False, 'frequency': None}


def get_cron_command(frequency_minutes=60):
    """Get the cron command for a given frequency."""
    script_dir = Path.cwd()
    python_path = subprocess.run(['which', 'python3'], capture_output=True, text=True).stdout.strip()

    # Convert frequency to cron expression
    if frequency_minutes == 30:
        cron_schedule = "*/30 * * * *"
    elif frequency_minutes == 60:
        cron_schedule = "0 * * * *"
    elif frequency_minutes == 120:
        cron_schedule = "0 */2 * * *"
    elif frequency_minutes == 180:
        cron_schedule = "0 */3 * * *"
    else:
        cron_schedule = "0 * * * *"  # Default to hourly

    return f"{cron_schedule} cd {script_dir} && {python_path} price_tracker.py >> {script_dir}/tracker.log 2>&1"


@app.route('/')
def index():
    """Main dashboard page."""
    products = get_all_products_with_history()
    cron_status = get_cron_status()

    return render_template('index.html',
                         products=products,
                         cron_status=cron_status)


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


@app.route('/api/extract_name', methods=['POST'])
def api_extract_name():
    """Extract product name from URL."""
    url = request.json.get('url') if request.is_json else request.form.get('url')

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    try:
        from price_tracker import PriceTracker
        tracker = PriceTracker()
        product_name = tracker.extract_product_name(url)

        if product_name:
            return jsonify({'success': True, 'name': product_name})
        else:
            return jsonify({'success': False, 'error': 'Could not extract product name'}), 400

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/update_product/<int:product_id>', methods=['POST'])
def api_update_product(product_id):
    """Update product configuration."""
    config = load_config()

    if product_id < 0 or product_id >= len(config['products']):
        return jsonify({'error': 'Product not found'}), 404

    # Get update data
    data = request.json if request.is_json else request.form.to_dict()

    # Update product fields
    product = config['products'][product_id]

    if 'name' in data:
        product['name'] = data['name']
    if 'url' in data:
        product['url'] = data['url']
    if 'notify_on_price_drop' in data:
        product['notify_on_price_drop'] = data['notify_on_price_drop'] in [True, 'true', 'on', '1']
    if 'notify_on_availability' in data:
        product['notify_on_availability'] = data['notify_on_availability'] in [True, 'true', 'on', '1']
    if 'track_variants' in data:
        product['track_variants'] = data['track_variants'] in [True, 'true', 'on', '1']

    # Save config
    save_config(config)

    return jsonify({'success': True, 'product': product})


@app.route('/add_product', methods=['POST'])
def add_product():
    """Add a new product to track."""
    name = request.form.get('name', '').strip()
    url = request.form.get('url')
    notify_price = request.form.get('notify_price') == 'on'
    notify_availability = request.form.get('notify_availability') == 'on'
    track_variants = request.form.get('track_variants') == 'on'

    # If name is empty, try to extract it from URL
    if not name and url:
        try:
            from price_tracker import PriceTracker
            tracker = PriceTracker()
            name = tracker.extract_product_name(url)
        except Exception as e:
            print(f"Error extracting name: {e}")
            name = None

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


@app.route('/remove_product/<int:product_id>')
def remove_product(product_id):
    """Remove a product from tracking."""
    config = load_config()

    # Remove product by index
    if 0 <= product_id < len(config['products']):
        removed = config['products'].pop(product_id)
        save_config(config)
        flash(f'Removed {removed["name"]} from tracking!', 'success')
    else:
        flash('Product not found!', 'error')

    return redirect(url_for('index'))


@app.route('/history/<int:product_id>')
def history(product_id):
    """View history for a specific product."""
    config = load_config()

    # Get product by index
    if product_id < 0 or product_id >= len(config.get('products', [])):
        flash('Product not found!', 'error')
        return redirect(url_for('index'))

    product_config = config['products'][product_id]

    # Calculate hash for file lookup
    import hashlib
    from favicon_utils import get_or_fetch_favicon

    hash_id = hashlib.md5(product_config['url'].encode()).hexdigest()[:12]

    history_data = get_product_history(hash_id)

    if not history_data:
        flash('No history data available yet!', 'warning')
        return redirect(url_for('index'))

    # Get favicon
    favicon_path = get_or_fetch_favicon(product_config['url'])

    return render_template('history.html',
                         product=product_config,
                         product_id=product_id,
                         current=history_data.get('current'),
                         history=history_data.get('history', []),
                         favicon=favicon_path)


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
    """Enable cron job with specified frequency."""
    try:
        # Get frequency from form (in minutes)
        frequency = int(request.form.get('frequency', 60))

        # Validate frequency
        if frequency not in [30, 60, 120, 180]:
            frequency = 60  # Default to hourly

        cron_command = get_cron_command(frequency)

        # Get existing crontab
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        existing_cron = result.stdout if result.returncode == 0 else ""

        # Remove any existing price tracker cron jobs
        lines = existing_cron.split('\n')
        new_lines = [line for line in lines if 'price_tracker.py' not in line]
        existing_cron = '\n'.join(new_lines).strip()

        # Add new cron job
        new_cron = (existing_cron + "\n" if existing_cron else "") + cron_command + "\n"

        # Write to crontab
        process = subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE, text=True)
        process.communicate(input=new_cron)

        # Format frequency message
        if frequency == 30:
            freq_msg = "every 30 minutes"
        elif frequency == 60:
            freq_msg = "every hour"
        elif frequency == 120:
            freq_msg = "every 2 hours"
        elif frequency == 180:
            freq_msg = "every 3 hours"
        else:
            freq_msg = f"every {frequency} minutes"

        flash(f'Automatic tracking enabled! Tracker will run {freq_msg}.', 'success')
    except Exception as e:
        flash(f'Error enabling automatic tracking: {e}', 'error')

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
