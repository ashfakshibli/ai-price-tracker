# Current Task: AJAX auto-reload and background task loader

## Implementation Plan

### Goal
- Add product without page reload (AJAX)
- Show loading spinner during background operations
- Auto-refresh product list when new product is added

### Subtasks

1. **Add JavaScript for AJAX form submission**
   - Intercept form submit event
   - Send AJAX POST request
   - Handle response and update UI

2. **Create loader/spinner component**
   - CSS for spinner animation
   - Show/hide loader functions
   - Position loader over relevant sections

3. **Auto-refresh product list**
   - Fetch updated product list via AJAX
   - Replace table contents dynamically
   - Maintain scroll position

4. **Show background task progress**
   - Add loading state for "Run Now" button
   - Show spinner when tracking is running
   - Poll for completion status

### Changes Required

**File: templates/base.html**
- Add loader CSS (spinner animation)
- Add JavaScript section in head or before </body>

**File: templates/index.html**
- Add product-list container ID
- Add form ID for AJAX submission
- Add loader elements

**File: dashboard.py**
- Add JSON endpoint for product list
- Return JSON response after adding product
- Add status endpoint for background tasks

### Verification

- [ ] Form submits without page reload
- [ ] Loader shows during submission
- [ ] Product list updates automatically
- [ ] Background tasks show progress
- [ ] Error handling works correctly
