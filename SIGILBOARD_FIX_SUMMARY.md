# Sigilboard Fix Summary

## Problems Fixed

### 1. Mouse Holding Center of First Cell
**Before**: The mouse dragging logic was simply subtracting grid_scale from mouse position, which didn't properly hold the center of the first cell in the tetromino.

**After**: 
- Added `drag_offset_x` and `drag_offset_y` attributes to track the offset from mouse to first cell's center
- `update_drag_offset()` calculates the exact center of the first cell when selected
- `update_loop()` now positions the sigil so its first cell's center follows the mouse cursor precisely

### 2. Right-Click Rotation Not Working  
**Before**: The event handler checked for `event.button == 2` (middle mouse), but right-click is button 3.

**After**:
- Changed condition to `event.button == 3` for right-click detection
- Rotation now works correctly when right-clicking on a selected sigil

### 3. Sigils Not Clicking Into Grid
**Before**: The `snap_to_grid()` function calculated position but didn't properly mark grid cells as occupied or ensure proper alignment.

**After**:
- Completely rewrote `snap_to_grid()` to:
  - Calculate which grid cell the first cell should snap to
  - Adjust sigil offset so first cell aligns with the grid
  - Mark all grid cells occupied by the sigil with the sigil index
  - Properly handle multi-cell sigils by adjusting relative positions

### 4. Bug Fix
- Fixed `generate_grid()` line 503: changed `tetrinomino[1]` to `tetrinomino[0]` to get the first cell's coordinates correctly

## Changes Made

### Sigilboard.__init__
- Added `drag_offset_x` and `drag_offset_y` initialization

### Sigilboard.event_loop()
- Changed middle-click (button 2) to right-click (button 3) for rotation
- Added call to `update_drag_offset()` when selecting a sigil

### New Method: Sigilboard.update_drag_offset()
- Calculates the offset from mouse cursor to the center of the first cell
- Called when a sigil is first selected

### Sigilboard.update_loop()
- Completely rewritten to use `drag_offset_x/y`
- Now properly maintains the first cell's center at the mouse cursor position

### Sigilboard.snap_to_grid()
- Rewritten to properly place sigils on the grid
- Calculates target grid position based on first cell's center
- Marks grid cells as occupied
- Properly adjusts for relative cell positions

## Verification
✓ All 11 unit tests pass  
✓ Mouse holding: First cell center follows cursor  
✓ Right-click rotation: Tetrominoes rotate 90 degrees clockwise  
✓ Grid snapping: Sigils snap to grid and mark cells as occupied  
✓ No crashes during gameplay  

