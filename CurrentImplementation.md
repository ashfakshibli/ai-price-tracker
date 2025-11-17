# Current Implementation Plan

## Overview
Implementing UI/UX improvements for product addition flow and fixing availability logic.

## Tasks

### 1. Progressive Product Loading
**Goal**: Improve UX during product addition - show loader, add product to list immediately, update with price data later

**Current Flow**:
- User submits form
- AJAX request sent to `/add_product`
- Loader shows "Adding product..."
- Waits for complete response
- Updates product list

**New Flow**:
- User submits form
- Show loader "Extracting product information..."
- Product added to DB with basic info (name, URL)
- Product appears in list immediately with "Checking price..." status
- Background task fetches price data
- Product row updates with actual price/availability data

**Implementation**:
1. Split `/add_product` endpoint:
   - Quick response: Add product to DB, return immediately
   - Background task: Fetch price data separately
2. Add new endpoint `/api/check_product_status/<product_id>`:
   - Returns current price check status
3. Frontend polling:
   - After product added, poll status endpoint
   - Update product row when data available

**Files to modify**:
- `dashboard.py`: Split add_product logic, add status endpoint
- `templates/index.html`: Update AJAX to poll for status
- `price_tracker.py`: May need to expose price checking function

---

### 2. Fix Shipping Availability Logic
**Goal**: Products with "Get It Tomorrow" or any shipping date should show as "Available"

**Current Issue**:
- Products showing as "Unavailable" when they have shipping dates
- Need to check where availability is determined

**Investigation needed**:
1. Check `price_tracker.py` - where is `can_add_to_cart` set?
2. Look at BestBuy scraping logic
3. Update logic to recognize shipping dates as "available"

**Implementation**:
- Find where availability is parsed from webpage
- Update logic: If shipping date exists OR can_add_to_cart → Available
- Test with "Get It Tomorrow" products

**Files to modify**:
- `price_tracker.py`: Update availability detection logic

---

### 3. Direct Paste Functionality
**Goal**: Paste button should paste immediately on click, no tooltip needed

**Current Behavior**:
- Button shows "Paste from clipboard" tooltip
- Requires click to paste
- Tooltip is unnecessary

**New Behavior**:
- Click button → immediately paste
- No tooltip shown
- Cleaner UX

**Implementation**:
- Remove `title="Paste from clipboard"` attribute
- Function already works correctly
- Just remove the tooltip

**Files to modify**:
- `templates/index.html`: Remove title attribute from paste button

---

### 4. Verify Product Sorting
**Goal**: Ensure products are sorted by creation date descending (latest first)

**Current Implementation**:
- `dashboard.py`: `get_all_products_with_history()`
- Query: `.order_by(Product.created_at.desc())`
- Should already be working

**Verification**:
1. Check if query is correct
2. Test by adding multiple products
3. Verify order in UI

**Files to check**:
- `dashboard.py`: Confirm ORDER BY clause
- May already be working, just need to verify

---

## Implementation Order

1. **Task 3** - Direct paste (easiest, 1-line change)
2. **Task 4** - Verify sorting (already implemented, just verify)
3. **Task 2** - Fix shipping logic (requires investigation)
4. **Task 1** - Progressive loading (most complex, requires backend changes)

---

## Testing Checklist

- [ ] Paste button works immediately without tooltip
- [ ] Products sorted correctly (newest first)
- [ ] "Get It Tomorrow" products show as Available
- [ ] Product appears in list before price is fetched
- [ ] Product row updates with price data when available
- [ ] Loader shows appropriate messages during each stage
- [ ] Error handling works for failed price fetches
