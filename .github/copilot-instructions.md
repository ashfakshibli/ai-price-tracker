# AI Price Tracker - Copilot Instructions

## Architecture Overview

**Core Components:**
- `price_tracker.py` - Main scraping engine using Selenium + Claude AI for data extraction
- `dashboard.py` - Flask web UI for product management
- `models.py` - SQLAlchemy ORM (SQLite database) for data persistence
- `favicon_utils.py` - Favicon fetching/caching utilities

**Data Flow:**
1. Selenium loads product pages in headless Chrome (handles JS-heavy sites)
2. Waits for price elements to appear (up to 20s)
3. Interacts with variant buttons (e.g., BestBuy "Fair/Good/Excellent" conditions)
4. Claude 3.5 Haiku analyzes rendered HTML to extract structured data
5. SQLAlchemy ORM persists products, price history, and variants to `tracker.db`
6. Dashboard displays data with real-time updates via AJAX polling

## Critical Development Workflows

**Environment Setup:**
```bash
# ALWAYS use virtual environment - project requires it
source venv/bin/activate

# Run applications (helper scripts auto-activate venv)
./run_tracker.sh      # Run price tracker once
./run_dashboard.sh    # Start web dashboard on :5000
```

**Environment Variables:**
- `.env` file MUST contain `ANTHROPIC_API_KEY` (loaded via `python-dotenv`)
- Both `price_tracker.py` and `dashboard.py` explicitly load `.env` using `Path(__file__).parent / '.env'` pattern

**Testing Changes:**
- Use test files (`test_*.py`) to verify specific features
- Dashboard changes: start `./run_dashboard.sh` and test in browser
- Scraping logic: modify `price_tracker.py` and run `./run_tracker.sh`

## Project-Specific Conventions

**Task Management Workflow (CRITICAL):**
- `Tasks.md` - Master task list (mark completed with `[x]`)
- `CurrentImplementation.md` - Detailed implementation plan for current task ONLY
- **Process:** Add task → Detail in CurrentImplementation.md → Implement → Test → Cross off in Tasks.md → Clean CurrentImplementation.md
- **Rule:** Do NOT create summary documents or update README unless important

**Database Models (SQLAlchemy ORM):**
- `Product` - Tracks monitored products (1:many relationship with PriceHistory)
- `PriceHistory` - Price check snapshots (1:many relationship with Variant)
- `Variant` - Product variants (e.g., different conditions)
- Access via `db.get_session()` - ALWAYS close sessions in finally blocks
- Products sorted by `created_at DESC` (newest first) - see `dashboard.py:39`

**Selenium Scraping Patterns:**
- Headless Chrome with 180s page load timeout, 20s for price elements
- Retry logic: 3 attempts with exponential backoff (5s, 10s, 15s)
- Variant detection: tries multiple CSS selectors (see `price_tracker.py:115-124`)
- Availability logic prioritizes positive signals (shipping dates, enabled "Add to Cart")
- HTML passed to Claude AI for structured extraction (50K chars typically)

**Claude AI Integration:**
- Model: `claude-3-5-haiku-20241022` (cost-effective, ~$0.001/check)
- Used for: extracting product data from HTML, generating product names from URLs
- See `price_tracker.py:356` (`_extract_product_data`) and `:440` (`extract_product_name`)

## Integration Points

**Flask Dashboard Routes:**
- `/` - Main dashboard (lists products, cron status)
- `/api/products` - JSON product list
- `/add_product` - Add new product (extracts name via Claude, saves to DB)
- `/api/check_product_status/<id>` - Poll for background price checks
- `/history/<id>` - Product price history page

**Cron Job Management:**
- `setup_cron.sh` - Sets up automated tracking
- Frequencies: 30min, 1hr, 2hr, 3hr (mapped to cron expressions in `dashboard.py:105-115`)
- Helper scripts (`run_*.sh`) used in cron jobs to ensure venv activation

**Favicon Caching:**
- Favicons stored in `static/favicons/` using MD5 hash of domain
- Auto-fetched on first product view, cached for subsequent loads
- Default fallback: `static/favicons/default-favicon.svg`

## Key File References

**Availability Detection Logic:**
- `price_tracker.py:204-295` - Complex shipping/cart availability checks
- Positive signals: selected shipping tiles with delivery dates, enabled "Add to Cart"
- Negative signals: "Unavailable" text in main product area (NOT variant buttons)

**Database Session Management:**
- `models.py:190-200` - `db.get_session()` pattern
- Example: `dashboard.py:36-70` - proper session handling with try/finally

**AJAX Polling Pattern:**
- `templates/index.html` - Frontend polls `/api/products` and `/api/logs` for updates
- Products appear immediately in list, then update with price data asynchronously

## Common Patterns

**Adding New Product (Dashboard):**
1. User submits URL
2. `extract_product_name()` uses Claude to scrape product name
3. Product saved to DB with basic info
4. Background: `price_tracker.py` fetches actual price/availability
5. Frontend polls for updates

**Price Change Detection:**
- Compare current vs. previous `PriceHistory` entries
- Notify on: price drops (if `notify_on_price_drop: true`)
- Notify on: availability changes (if `notify_on_availability: true`)

**Variant Handling:**
- BestBuy-specific: "Fair", "Good", "Excellent" open-box conditions
- Each variant gets own availability/price check
- Stored in `Variant` table linked to `PriceHistory`
