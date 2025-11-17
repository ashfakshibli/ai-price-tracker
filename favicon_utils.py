#!/usr/bin/env python3
"""
Utility functions for fetching and caching favicons from websites.
"""

import hashlib
import os
import requests
from pathlib import Path
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup


FAVICON_DIR = Path("static/favicons")
FAVICON_DIR.mkdir(exist_ok=True, parents=True)

DEFAULT_FAVICON = "default-favicon.png"


def get_domain_from_url(url):
    """Extract domain from URL."""
    parsed = urlparse(url)
    return parsed.netloc or parsed.path


def get_favicon_filename(url):
    """Generate a unique filename for a favicon based on domain."""
    domain = get_domain_from_url(url)
    # Use MD5 hash of domain for filename
    hash_str = hashlib.md5(domain.encode()).hexdigest()[:12]
    return f"{hash_str}.ico"


def get_favicon_path(url):
    """Get the relative path to a favicon, downloading if necessary."""
    filename = get_favicon_filename(url)
    filepath = FAVICON_DIR / filename

    # If already cached, return the path
    if filepath.exists():
        return f"static/favicons/{filename}"

    # Try to download favicon
    try:
        favicon_url = find_favicon_url(url)
        if favicon_url and download_favicon(favicon_url, filepath):
            return f"static/favicons/{filename}"
    except Exception as e:
        print(f"Error fetching favicon for {url}: {e}")

    # Return default or None if failed
    return None


def find_favicon_url(url):
    """Find the favicon URL for a website."""
    domain = get_domain_from_url(url)
    base_url = f"https://{domain}" if not url.startswith('http') else url.split('/', 3)[:3]
    base_url = '/'.join(base_url) if isinstance(base_url, list) else base_url

    # Method 1: Try common favicon locations
    common_paths = [
        '/favicon.ico',
        '/favicon.png',
        '/apple-touch-icon.png',
        '/apple-touch-icon-precomposed.png',
    ]

    for path in common_paths:
        try:
            test_url = urljoin(base_url, path)
            response = requests.head(test_url, timeout=5, allow_redirects=True)
            if response.status_code == 200:
                return test_url
        except:
            continue

    # Method 2: Parse HTML for favicon link
    try:
        response = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        soup = BeautifulSoup(response.content, 'html.parser')

        # Look for various favicon tags
        icon_links = soup.find_all('link', rel=lambda x: x and ('icon' in x.lower() or 'shortcut' in x.lower()))

        for link in icon_links:
            href = link.get('href')
            if href:
                return urljoin(base_url, href)

    except Exception as e:
        print(f"Error parsing HTML for favicon: {e}")

    # Method 3: Fallback to /favicon.ico
    return urljoin(base_url, '/favicon.ico')


def download_favicon(url, save_path):
    """Download a favicon from URL and save to path."""
    try:
        response = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

        if response.status_code == 200 and len(response.content) > 0:
            with open(save_path, 'wb') as f:
                f.write(response.content)
            return True
    except Exception as e:
        print(f"Error downloading favicon from {url}: {e}")

    return False


def get_or_fetch_favicon(url):
    """Get cached favicon or fetch if not exists. Returns relative path or None."""
    return get_favicon_path(url)
