# Current Task: Make UI elements responsive with icon buttons

## Implementation Plan

### Goal
Replace text buttons with icon buttons and ensure all UI elements are responsive.

### Subtasks

1. **Add icon library (using Unicode/Emoji or external library)**
   - Use Font Awesome or simple Unicode symbols
   - Add icon mapping for common actions

2. **Update button styling**
   - Create icon-only button class
   - Make buttons display side by side (flexbox)
   - Add tooltips for accessibility

3. **Replace text buttons with icons**
   - View History → 👁️ or 📊
   - Remove → 🗑️ or ❌
   - Enable/Disable Cron → ⏰/⏸️
   - Run Now → ▶️ or 🚀

4. **Make table responsive**
   - Stack table cells on mobile
   - Use horizontal scroll for wide tables
   - Adjust action buttons layout

### Changes Required

**File: templates/base.html**
- Add CSS for icon buttons
- Add tooltip styling
- Update responsive breakpoints

**File: templates/index.html**
- Replace button text with icons
- Add title attributes for tooltips
- Update action buttons layout

### Verification

- [ ] Buttons show icons instead of text
- [ ] Tooltips appear on hover
- [ ] Buttons are side by side
- [ ] Table is responsive on mobile
- [ ] All actions still work correctly
