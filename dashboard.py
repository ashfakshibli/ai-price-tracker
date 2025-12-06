#!/usr/bin/env python3
"""
Web dashboard for AI Price Tracker.

Now uses SQLite database with SQLAlchemy ORM for data persistence.
"""

import os
import subprocess
import json
import requests
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from dotenv import load_dotenv

# Database imports
from models import db, Product, PriceHistory, Variant
from favicon_utils import get_or_fetch_favicon

# Load environment variables from .env file
# Use explicit path to ensure .env is found regardless of working directory
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)

# Use environment variable for secret key, fallback to random for local dev
app.secret_key = os.environ.get('FLASK_SECRET_KEY') or os.urandom(24)

LOG_FILE = "tracker.log"

# Create database tables if they don't exist
db.create_tables()


def get_all_products_with_history():
    """Get all products with their latest data, sorted by creation time (newest first)."""
    session = db.get_session()

    try:
        # Query all active products, ordered by creation time (newest first)
        products_db = session.query(Product).filter_by(is_active=True).order_by(Product.created_at.desc()).all()

        products = []
        for product in products_db:
            # Get latest price check
            latest = product.latest_price

            # Get or fetch favicon
            if not product.favicon_path:
                product.favicon_path = get_or_fetch_favicon(product.url)
                session.commit()

            # Build product dict for template
            products.append({
                'id': product.id,
                'config': {
                    'name': product.name,
                    'url': product.url,
                    'notify_on_price_drop': product.notify_on_price_drop,
                    'notify_on_availability': product.notify_on_availability,
                    'track_variants': product.track_variants
                },
                'latest': latest.to_dict() if latest else None,
                'history_count': len(product.price_history),
                'favicon': product.favicon_path or 'static/favicons/default-favicon.svg',
                'created_at': product.created_at.isoformat() if product.created_at else None
            })

        return products
    finally:
        session.close()


def get_heroku_scheduler_jobs():
    """Check if Heroku Scheduler addon is installed and get basic info."""
    try:
        # Check if we're on Heroku
        if not os.environ.get('DYNO'):
            return {'installed': False}
        
        app_name = os.environ.get('HEROKU_APP_NAME', 'ai-price-tracker').strip()
        api_key = os.environ.get('HEROKU_API_KEY', '').strip()
        
        # Try Heroku Platform API if we have credentials
        if api_key and app_name:
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Accept': 'application/vnd.heroku+json; version=3'
            }
            
            addons_url = f'https://api.heroku.com/apps/{app_name}/addons'
            response = requests.get(addons_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                addons = response.json()
                for addon in addons:
                    addon_service_name = addon.get('addon_service', {}).get('name', '')
                    if 'scheduler' in addon_service_name.lower():
                        return {
                            'installed': True,
                            'name': addon.get('name', 'scheduler'),
                            'plan': addon.get('plan', {}).get('name', 'scheduler:standard'),
                            'state': addon.get('state', 'provisioned')
                        }
        
        # Fallback: Check for SCHEDULER_URL or other scheduler-related env vars
        # Heroku automatically sets attachment env vars when addon is provisioned
        scheduler_env_vars = [key for key in os.environ.keys() if 'SCHEDULER' in key.upper()]
        if scheduler_env_vars:
            return {
                'installed': True,
                'name': 'scheduler',
                'plan': 'scheduler:standard',
                'state': 'provisioned'
            }
        
        return {'installed': False}
            
    except Exception as e:
        print(f"Error checking Heroku Scheduler: {e}")
        # Fallback: Check for scheduler env vars
        scheduler_env_vars = [key for key in os.environ.keys() if 'SCHEDULER' in key.upper()]
        if scheduler_env_vars:
            return {
                'installed': True,
                'name': 'scheduler',
                'plan': 'scheduler:standard',
                'state': 'provisioned'
            }
        return {'installed': False}


def get_cron_status():
    """Check if cron job exists and get its frequency."""
    # Check if running on Heroku
    if os.environ.get('DYNO'):
        # Fetch Heroku Scheduler jobs
        scheduler_jobs = get_heroku_scheduler_jobs()
        return {
            'enabled': False, 
            'frequency': None, 
            'is_heroku': True,
            'scheduler_jobs': scheduler_jobs
        }
    
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
    heroku_app_name = os.environ.get('HEROKU_APP_NAME', '')

    return render_template('index.html',
                         products=products,
                         cron_status=cron_status,
                         heroku_app_name=heroku_app_name)


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

    session = db.get_session()
    try:
        exists = session.query(Product).filter_by(url=url, is_active=True).first() is not None
        return jsonify({'exists': exists, 'url': url})
    finally:
        session.close()


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
    session = db.get_session()
    try:
        product = session.query(Product).filter_by(id=product_id, is_active=True).first()

        if not product:
            return jsonify({'error': 'Product not found'}), 404

        # Get update data
        data = request.json if request.is_json else request.form.to_dict()

        # Update product fields
        if 'name' in data:
            product.name = data['name']
        if 'url' in data:
            product.url = data['url']
        if 'notify_on_price_drop' in data:
            product.notify_on_price_drop = data['notify_on_price_drop'] in [True, 'true', 'on', '1']
        if 'notify_on_availability' in data:
            product.notify_on_availability = data['notify_on_availability'] in [True, 'true', 'on', '1']
        if 'track_variants' in data:
            product.track_variants = data['track_variants'] in [True, 'true', 'on', '1']

        product.updated_at = datetime.utcnow()
        session.commit()

        product_dict = {
            'id': product.id,
            'name': product.name,
            'url': product.url,
            'notify_on_price_drop': product.notify_on_price_drop,
            'notify_on_availability': product.notify_on_availability,
            'track_variants': product.track_variants
        }

        return jsonify({'success': True, 'product': product_dict})
    except Exception as e:
        session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        session.close()


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

    # Add product to database
    session = db.get_session()
    try:
        # Check if URL already exists
        existing = session.query(Product).filter_by(url=url).first()
        if existing:
            message = f'This URL is already being tracked as "{existing.name}"'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': message}), 400
            flash(message, 'error')
            return redirect(url_for('index'))

        # Create new product
        product = Product(
            name=name,
            url=url,
            notify_on_price_drop=notify_price,
            notify_on_availability=notify_availability,
            track_variants=track_variants
        )

        session.add(product)
        session.commit()
        product_id = product.id  # Get the ID before closing session

        # Trigger immediate background price check
        import threading
        def background_check():
            try:
                from price_tracker import PriceTracker
                tracker = PriceTracker()
                tracker.check_single_product(product_id)
            except Exception as e:
                print(f"Error in background check for product {product_id}: {e}")

        thread = threading.Thread(target=background_check)
        thread.daemon = True
        thread.start()

        message = f'Added {name} to tracking! Initial price check is running in the background.'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'message': message, 'product': {'id': product_id, 'name': name, 'url': url}})

        flash(message, 'success')
        return redirect(url_for('index'))
    except Exception as e:
        session.rollback()
        message = f'Error adding product: {str(e)}'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': message}), 500
        flash(message, 'error')
        return redirect(url_for('index'))
    finally:
        session.close()


@app.route('/remove_product/<int:product_id>')
def remove_product(product_id):
    """Remove a product from tracking (soft delete)."""
    session = db.get_session()
    try:
        product = session.query(Product).filter_by(id=product_id).first()
        if product:
            # Soft delete - mark as inactive instead of deleting
            product.is_active = False
            session.commit()
            flash(f'Removed {product.name} from tracking!', 'success')
        else:
            flash('Product not found!', 'error')
    except Exception as e:
        session.rollback()
        flash(f'Error removing product: {str(e)}', 'error')
    finally:
        session.close()

    return redirect(url_for('index'))


@app.route('/history/<int:product_id>')
def history(product_id):
    """View history for a specific product."""
    session = db.get_session()
    try:
        product = session.query(Product).filter_by(id=product_id, is_active=True).first()

        if not product:
            flash('Product not found!', 'error')
            return redirect(url_for('index'))

        # Get all price history for this product
        price_history = product.price_history  # Already ordered by date desc

        if not price_history:
            flash('No history data available yet!', 'warning')
            return redirect(url_for('index'))

        # Current (latest) price
        current = price_history[0].to_dict() if price_history else None

        # Historical prices (all but the latest)
        history_list = [h.to_dict() for h in price_history[1:]] if len(price_history) > 1 else []

        product_dict = {
            'name': product.name,
            'url': product.url
        }

        return render_template('history.html',
                             product=product_dict,
                             product_id=product_id,
                             current=current,
                             history=history_list,
                             favicon=product.favicon_path or 'static/favicons/default-favicon.svg')
    finally:
        session.close()


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
        # Check if running on Heroku
        if os.environ.get('DYNO'):
            flash('⚠️ Cron is not available on Heroku. Please use Heroku Scheduler addon instead. '
                  'Run: heroku addons:create scheduler:standard --app your-app-name', 'warning')
            return redirect(url_for('index'))
        
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
        # Check if running on Heroku
        if os.environ.get('DYNO'):
            flash('⚠️ Cron is not available on Heroku. Use Heroku Scheduler addon to manage scheduled tasks.', 'warning')
            return redirect(url_for('index'))
        
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
    # Get port from environment variable (Heroku) or use default
    port = int(os.environ.get('PORT', 5000))
    
    print("=" * 60)
    print("AI Price Tracker Dashboard")
    print("=" * 60)
    print("\nUsing SQLite database: tracker.db")
    print("Starting web server...")
    print(f"Dashboard URL: http://localhost:{port}")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60)

    # Disable debug mode in production (when PORT env var is set by Heroku)
    debug_mode = os.environ.get('PORT') is None
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
