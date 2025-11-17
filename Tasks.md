# Dashboard Improvement Tasks

## Completed Tasks

- [x] Make everything the header center aligned
- [x] Make two section body of the dashboard. Automatic tracking and Tracked products list should be on left and Add new product should be on right.
- [x] Make all the UI elements responsive. The buttons should be side by side and rather than button name show icons for the function of the buttons.
- [x] The page should be auto loading items when added new product in the history without reloading the page. also if there is a process running in the background should show loader for that task.
- [x] Add a sidebar to show debug of steps the app is doing in the back ground when a new url is added.
- [x] In last checked do not show the timestamp rather show the minutes ago last check was done. Use modern UX guidelines to improve more UX and UI of the dashboard.

## New Tasks

- [x] Use modern button styles (not emoji icons which look clunky)
- [x] History and delete buttons should be side by side
- [x] Clicking delete button should show popup for confirmation with product info and history
- [x] Debug logs sidebar overlaps Add product section - make whole section squeeze responsively when sidebar opens
- [x] Add paste URL option if URL found in clipboard to add new product (skip if already being tracked)

## Latest Features

- [x] Auto-generate product name from URL scraping (using Claude AI)
- [x] Edit/update functionality for tracked items (modal-based editing)
- [x] Inline editing on product name - click directly on name to edit (more intuitive)
- [x] Merchant favicon icons displayed next to products (auto-fetched and cached)
- [x] Tracking frequency selector - choose between 30min, 1hr, 2hr, or 3hr intervals (cron details hidden from users)
- [x] Reorganized dashboard layout - Automatic Tracking moved under Add Product (right column), left column shows only tracked products
- [x] Product sorting by creation time - newest products appear first in the list
- [x] **Database Migration** - Migrated from JSON files to SQLite database with SQLAlchemy ORM (proper data models, relationships, better data integrity)

## Current Tasks (In Progress)

- [x] **Direct paste functionality** - Remove tooltip, make paste button paste directly on click
- [x] **Verify product sorting** - DB query sorts by creation date descending (latest first) ✓ Confirmed working
- [x] **Fix shipping availability logic** - "Get It Tomorrow" or date means product is available (fixed to recognize "tomorrow", "today")
- [x] **Better loader messages** - Show "Extracting product name from URL..." when name extraction is happening
- [x] **Progressive product loading** - Display product immediately after adding, then update with price data when background processing completes (requires price_tracker.py integration)

