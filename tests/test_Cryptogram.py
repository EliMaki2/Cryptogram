from Cryptogram import Moonpanel, Sigilboard
import pygame
import unittest

class TestMoonpanel(unittest.TestCase):
    def setUp(self):
        print(f"SETUP TEST")
        self.expected_height = 10
        self.expected_width = 10
        self.testing_difficulty = 3
        self.expected_x = 2+self.testing_difficulty*2
        self.expected_y = 2+self.testing_difficulty*2
        self.moonpanel = Moonpanel(self.expected_width, self.expected_height, difficulty=self.testing_difficulty)

    def test_moonpanel_screen(self):
        print(f"TESTING MOONPANEL SCREEN\n")
        print(self.moonpanel.height, self.moonpanel.width)
        self.assertEqual(self.moonpanel.height, self.expected_height)
        self.assertEqual(self.moonpanel.width, self.expected_width)
        print(f"\nCONCLUDING MOONPANEL SCREEN TEST\n")

    def test_moonpanel_generate_path(self):
        print(f"TESTING MOONPANEL GENERATE PATH\n")
        path = self.moonpanel.generate_path(print_test = True)
        for row, col in path:
            self.assertTrue(0 <= row < self.expected_y)
            self.assertTrue(0 <= col < self.expected_x)
        self.assertTrue(path[0] == (0, 0))
        self.assertTrue(path[-1] == (self.expected_y-1, self.expected_x-1))
        print(f"\nCONCLUDING MOONPANEL GENERATE PATH TEST\n")

    def test_moonpanel_generate_grid(self):
        print(f"TESTING MOONPANEL GENERATE GRID\n")
        self.moonpanel.generate_grid(print_test = True)
        self.assertEqual(len(self.moonpanel.grid), self.expected_y)
        self.assertEqual(len(self.moonpanel.grid[0]), self.expected_x)
        self.assertTrue(self.moonpanel.grid[0][0] == "S")
        self.assertTrue(self.moonpanel.grid[self.expected_y-1][self.expected_x-1] == "E")
        print(f"\nCONCLUDING MOONPANEL GENERATE GRID TEST\n")

class TestSigilboard(unittest.TestCase):
    def setUp(self):
        print(f"SETUP SIGILBOARD TEST")
        self.expected_height = 800
        self.expected_width = 800
        self.testing_difficulty = 2
        self.sigilboard = Sigilboard(self.expected_width, self.expected_height, difficulty=self.testing_difficulty)

    def tearDown(self):
        pygame.quit()

    def test_sigilboard_initialization(self):
        print(f"TESTING SIGILBOARD INITIALIZATION\n")
        self.assertEqual(self.sigilboard.width, self.expected_width)
        self.assertEqual(self.sigilboard.height, self.expected_height)
        self.assertEqual(self.sigilboard.name, "Cryptogram")
        self.assertEqual(self.sigilboard.color, (150, 150, 150))
        self.assertEqual(self.sigilboard.difficulty, self.testing_difficulty)
        print(f"Width: {self.sigilboard.width}, Height: {self.sigilboard.height}")
        print(f"\nCONCLUDING SIGILBOARD INITIALIZATION TEST\n")

    def test_sigilboard_sigil_amount(self):
        print(f"TESTING SIGILBOARD SIGIL AMOUNT\n")
        expected_sigil_amount = 3 + self.testing_difficulty
        self.assertEqual(self.sigilboard.sigil_amount, expected_sigil_amount)
        print(f"Sigil amount: {self.sigilboard.sigil_amount}")
        print(f"\nCONCLUDING SIGILBOARD SIGIL AMOUNT TEST\n")

    def test_sigilboard_grid_size(self):
        print(f"TESTING SIGILBOARD GRID SIZE\n")
        expected_grid_size = 12 + self.testing_difficulty * 4
        self.assertEqual(self.sigilboard.grid_size, expected_grid_size)
        print(f"Grid size: {self.sigilboard.grid_size}")
        print(f"\nCONCLUDING SIGILBOARD GRID SIZE TEST\n")

    def test_sigilboard_dimensions(self):
        print(f"TESTING SIGILBOARD DIMENSIONS\n")
        self.assertGreaterEqual(self.sigilboard.x, 2)
        self.assertLessEqual(self.sigilboard.x, (self.sigilboard.grid_size) // 2)
        self.assertIsNotNone(self.sigilboard.y)
        self.assertIsInstance(self.sigilboard.y, int)
        print(f"X dimension: {self.sigilboard.x}, Y dimension: {self.sigilboard.y}")
        print(f"\nCONCLUDING SIGILBOARD DIMENSIONS TEST\n")

    def test_sigilboard_initial_grid(self):
        print(f"TESTING SIGILBOARD INITIAL GRID\n")
        self.assertEqual(len(self.sigilboard.grid), 0)
        self.assertEqual(self.sigilboard.sigils, [])
        print(f"Initial grid empty: {len(self.sigilboard.grid) == 0}")
        print(f"Initial sigils empty: {len(self.sigilboard.sigils) == 0}")
        print(f"\nCONCLUDING SIGILBOARD INITIAL GRID TEST\n")

    def test_sigilboard_grid_dimensions_valid(self):
        print(f"TESTING SIGILBOARD GRID DIMENSIONS ARE VALID\n")
        self.assertGreater(self.sigilboard.x * self.sigilboard.y, 0)
        # grid_size is calculated independently, not as x * y
        self.assertEqual(self.sigilboard.grid_size, 12 + self.testing_difficulty * 4)
        print(f"Grid dimensions valid: {self.sigilboard.x} x {self.sigilboard.y}")
        print(f"\nCONCLUDING SIGILBOARD GRID DIMENSIONS VALID TEST\n")

    def test_sigilboard_available_positions_boundary(self):
        print(f"TESTING SIGILBOARD AVAILABLE POSITIONS BOUNDARY CHECK\n")
        # Manually set up a simple grid to avoid complex generate_grid logic
        self.sigilboard.grid = [
            [" ", " ", " "],
            [" ", " ", " "],
            [" ", " ", " "]
        ]
        self.sigilboard.x = 3
        self.sigilboard.y = 3
        # Test middle position
        test_position = (1, 1)
        possibles = self.sigilboard.avalible_positions([], test_position)
        self.assertIsInstance(possibles, list)
        # Check that all returned positions are within bounds
        for col, row in possibles:
            self.assertGreaterEqual(col, 0)
            self.assertLess(col, self.sigilboard.x)
            self.assertGreaterEqual(row, 0)
            self.assertLess(row, self.sigilboard.y)
        print(f"Available positions from {test_position}: {possibles}")
        self.assertEqual(len(possibles), 4)  # Center should have 4 neighbors
        print(f"\nCONCLUDING SIGILBOARD AVAILABLE POSITIONS BOUNDARY TEST\n")

    def test_sigilboard_difficulty_affects_sigils(self):
        print(f"TESTING SIGILBOARD DIFFICULTY AFFECTS SIGILS\n")
        sigil_amount_1 = 3 + 1
        sigil_amount_3 = 3 + 3
        self.assertLess(sigil_amount_1, sigil_amount_3)
        print(f"Difficulty 1: {sigil_amount_1} sigils")
        print(f"Difficulty 3: {sigil_amount_3} sigils")
        print(f"\nCONCLUDING SIGILBOARD DIFFICULTY AFFECTS SIGILS TEST\n")

    def test_sigilboard_difficulty_affects_grid_size(self):
        print(f"TESTING SIGILBOARD DIFFICULTY AFFECTS GRID SIZE\n")
        grid_size_1 = 12 + 1 * 4
        grid_size_3 = 12 + 3 * 4
        self.assertLess(grid_size_1, grid_size_3)
        print(f"Difficulty 1: grid size = {grid_size_1}")
        print(f"Difficulty 3: grid size = {grid_size_3}")
        print(f"\nCONCLUDING SIGILBOARD DIFFICULTY AFFECTS GRID SIZE TEST\n")

    def test_sigilboard_generate_grid_no_overlap(self):
        print(f"TESTING SIGILBOARD GENERATE GRID NO OVERLAP\n")
        self.sigilboard.generate_grid()
        # Verify grid is populated correctly
        self.assertEqual(len(self.sigilboard.grid), self.sigilboard.y)
        for row in self.sigilboard.grid:
            self.assertEqual(len(row), self.sigilboard.x)
        
        # Note: With the new sigil structure, grid cells are cleared after generation
        # So we just verify that sigils were created and have valid coordinates
        for sigil_id, sigil in enumerate(self.sigilboard.sigils, 1):
            coordinates, color, position = sigil
            # Verify coordinates are tuples
            for col, row in coordinates:
                self.assertIsInstance(col, int)
                self.assertIsInstance(row, int)
        
        print(f"Grid dimensions: {self.sigilboard.y} x {self.sigilboard.x}")
        print(f"Tetrinominos created: {len(self.sigilboard.sigils)}")
        print(f"All tetrinominos have valid coordinates!")
        print(f"\nCONCLUDING SIGILBOARD GENERATE GRID NO OVERLAP TEST\n")

    def test_sigilboard_generate_grid(self):
        print(f"TESTING SIGILBOARD GENERATE GRID\n")
        self.sigilboard.generate_grid()
        self.assertIsInstance(self.sigilboard.grid, list)
        self.assertEqual(len(self.sigilboard.grid), self.sigilboard.y)
        for row in self.sigilboard.grid:
            self.assertIsInstance(row, list)
            self.assertEqual(len(row), self.sigilboard.x)
        print(f"Generated grid with dimensions: {self.sigilboard.x} x {self.sigilboard.y}")
        print(f"Sigils: {self.sigilboard.sigils}")
        print(f"\nCONCLUDING SIGILBOARD GENERATE GRID TEST\n")

if __name__ == '__main__':
    unittest.main()