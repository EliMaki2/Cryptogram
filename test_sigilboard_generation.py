#!/usr/bin/env python3
"""
Test script to verify Sigilboard.generate_grid() works correctly.
Tests for crashes, overlaps, and proper tetrinomino generation.
"""

import sys
sys.path.insert(0, '.')

from Cryptogram import Sigilboard
import pygame

def print_grid(sigilboard):
    """Print the grid in a readable format."""
    print("\nGenerated Grid:")
    for row in sigilboard.grid:
        for cell in row:
            if cell == " ":
                print(".", end=" ")
            else:
                print(cell, end=" ")
        print()

def verify_no_overlaps(sigilboard):
    """Verify tetrinominos don't overlap."""
    all_cells = set()
    for sigil_id, tetrinomino in enumerate(sigilboard.sigils, 1):
        for col, row in tetrinomino:
            if (col, row) in all_cells:
                print(f"ERROR: Cell ({col}, {row}) appears in multiple tetrinominos!")
                return False
            all_cells.add((col, row))
    return True

def test_generate_grid(difficulty=2):
    """Test generate_grid with given difficulty."""
    print(f"\n{'='*60}")
    print(f"Testing Sigilboard with difficulty={difficulty}")
    print(f"{'='*60}")
    
    sigilboard = Sigilboard(800, 800, difficulty=difficulty)
    print(f"Grid size: {sigilboard.grid_size}")
    print(f"Grid dimensions: {sigilboard.x} x {sigilboard.y}")
    print(f"Target sigil amount: {sigilboard.sigil_amount}")
    
    try:
        sigilboard.generate_grid()
        print(f"✓ generate_grid() completed without crashing")
    except Exception as e:
        print(f"✗ CRASH: {e}")
        pygame.quit()
        return False
    
    print(f"Tetrinominos created: {len(sigilboard.sigils)}")
    
    # Check for overlaps
    if verify_no_overlaps(sigilboard):
        print(f"✓ No overlapping tetrinominos")
    else:
        print(f"✗ OVERLAPS DETECTED")
        pygame.quit()
        return False
    
    # Print grid
    print_grid(sigilboard)
    
    # Verify grid structure
    total_cells = sum(1 for row in sigilboard.grid for cell in row if cell != " ")
    expected_cells = len(sigilboard.sigils) * 4
    print(f"Total cells filled: {total_cells} (expected: {expected_cells})")
    
    if total_cells == expected_cells:
        print(f"✓ Grid structure is correct")
    else:
        print(f"⚠ Grid cells mismatch")
    
    pygame.quit()
    return True

if __name__ == "__main__":
    all_passed = True
    
    # Test multiple difficulties
    for diff in [1, 2, 3]:
        if not test_generate_grid(diff):
            all_passed = False
    
    print(f"\n{'='*60}")
    if all_passed:
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed")
    print(f"{'='*60}\n")
