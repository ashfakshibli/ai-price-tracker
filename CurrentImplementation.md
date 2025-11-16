# Current Task: Make two section body layout

## Implementation Plan

### Goal
Create a two-column layout where:
- Left side: Automatic tracking + Tracked products list
- Right side: Add new product form

### Subtasks

1. **Update index.html layout structure**
   - Create a grid or flexbox layout
   - Left column: Cron status + Products table
   - Right column: Add product form

2. **Add responsive CSS classes**
   - Use CSS Grid or Flexbox
   - Make it stack on mobile (single column)

3. **Adjust card widths and spacing**
   - Ensure proper spacing between columns
   - Make cards fill their columns

### Changes Required

**File: templates/index.html**
- Wrap cron and products sections in a left container
- Wrap add product form in a right container
- Add grid/flex container wrapper

**File: templates/base.html**
- Add grid layout CSS classes
- Add responsive breakpoints

### Verification

- [ ] Two column layout on desktop
- [ ] Left side shows cron + products
- [ ] Right side shows add product form
- [ ] Stacks to single column on mobile
- [ ] Proper spacing and alignment
