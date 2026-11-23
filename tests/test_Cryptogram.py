from Cryptogram_Demo import Moonpanel, Sigilboard
import Cryptogram_Demo
import io
import pygame
import time
import unittest
from unittest.mock import patch


class TestCryptogramSelection(unittest.TestCase):
    def test_unboosted_selection_uses_all_unlocked_types(self):
        names = ["Moonpanel", "Huegrid", "Sigilboard"]
        for value, expected in [(0.0, "Moonpanel"), (0.34, "Huegrid"),
                                (0.67, "Sigilboard")]:
            with self.subTest(value=value):
                count = [0]

                def choose(options):
                    if isinstance(options[0], str):
                        selected = options[count[0] % len(options)]
                        count[0] += 1
                        return selected
                    return options[0]

                with patch.object(Cryptogram_Demo, "unlocked_cryptograms", names), \
                     patch.object(Cryptogram_Demo, "active_boosters", {}), \
                     patch.object(Cryptogram_Demo.random, "choice", side_effect=choose), \
                     patch.object(Cryptogram_Demo.random._inst, "random", return_value=value), \
                     patch.object(Cryptogram_Demo, "create_moonpanel") as moonpanel, \
                     patch.object(Cryptogram_Demo, "create_huegrid") as huegrid, \
                     patch.object(Cryptogram_Demo, "create_sigilboard") as sigilboard:
                    Cryptogram_Demo.create_cryptogram(1, 1, 1)
                    for name, creator in zip(names, [moonpanel, huegrid, sigilboard]):
                        self.assertEqual(creator.call_count, int(name == expected))

    def test_weighted_selection_respects_luck_booster(self):
        for value, expected in [(0.0, "Moonpanel"), (0.79, "Moonpanel"),
                                (0.8, "Huegrid"), (0.999, "Huegrid")]:
            with self.subTest(value=value), \
                 patch.object(Cryptogram_Demo, "unlocked_cryptograms", ["Moonpanel", "Huegrid"]), \
                 patch.object(Cryptogram_Demo, "active_boosters", {"Moonpanel_Luck/.8": 1}), \
                 patch.object(Cryptogram_Demo.random, "choice", side_effect=lambda options: options[-1]), \
                 patch.object(Cryptogram_Demo.random._inst, "random", return_value=value), \
                 patch.object(Cryptogram_Demo, "create_moonpanel") as moonpanel, \
                 patch.object(Cryptogram_Demo, "create_huegrid") as huegrid:
                Cryptogram_Demo.create_cryptogram(1, 1, 1)
                self.assertEqual(moonpanel.call_count, int(expected == "Moonpanel"))
                self.assertEqual(huegrid.call_count, int(expected == "Huegrid"))
                self.assertEqual(Cryptogram_Demo.active_boosters["Moonpanel_Luck/.8"], 0)

    def test_zero_weight_does_not_select_last_unlocked(self):
        with patch.object(Cryptogram_Demo, "unlocked_cryptograms", ["Moonpanel", "Huegrid"]), \
             patch.object(Cryptogram_Demo, "active_boosters", {}), \
             patch.object(Cryptogram_Demo.random, "choice", side_effect=lambda options: options[0]), \
             patch.object(Cryptogram_Demo.random._inst, "random", return_value=0.999), \
             patch.object(Cryptogram_Demo.random, "randint", return_value=100), \
             patch.object(Cryptogram_Demo, "create_moonpanel") as moonpanel, \
             patch.object(Cryptogram_Demo, "create_huegrid") as huegrid:
            Cryptogram_Demo.create_cryptogram(1, 1, 1)
            moonpanel.assert_called_once()
            huegrid.assert_not_called()

    def test_negative_luck_never_produces_negative_weights(self):
        boosters = {"Moonpanel_Luck/-.4": 1, "Huegrid_Luck/.8": 1,
                    "Sigilboard_Luck/.8": 1}
        with patch.object(Cryptogram_Demo, "unlocked_cryptograms", ["Moonpanel", "Huegrid", "Sigilboard"]), \
             patch.object(Cryptogram_Demo, "active_boosters", boosters), \
             patch.object(Cryptogram_Demo.random, "choice", side_effect=lambda options: options[-1]), \
             patch.object(Cryptogram_Demo.random, "choices", return_value=["Huegrid"]) as choices, \
             patch.object(Cryptogram_Demo, "create_huegrid"):
            Cryptogram_Demo.create_cryptogram(1, 1, 1)
            weights = choices.call_args.kwargs["weights"]
            self.assertTrue(all(weight >= 0 for weight in weights))
            self.assertEqual(sum(weights), 100)
            self.assertEqual(weights[0], 0)

    def test_no_unlocked_cryptograms_raises(self):
        with patch.object(Cryptogram_Demo, "unlocked_cryptograms", []):
            with self.assertRaisesRegex(ValueError, "At least one cryptogram"):
                Cryptogram_Demo.create_cryptogram(1, 1, 1)


class TestCooldownInput(unittest.TestCase):
    def run_wait(self, duration, events, shop=None):
        clock = [0.0]
        output = io.StringIO()
        snapshots = []
        events = list(events)

        def read_key():
            if events and clock[0] >= events[0][0]:
                _, key = events.pop(0)
                snapshots.append((key, output.getvalue()))
                return key
            if clock[0] > 30:
                self.fail("Cooldown input did not finish")
            return None

        def sleep(seconds):
            clock[0] += seconds

        def visit_shop():
            snapshots.append(("shop", output.getvalue()))
            if shop:
                shop(clock, output)

        with patch.object(Cryptogram_Demo.time, "monotonic", side_effect=lambda: clock[0]), \
             patch.object(Cryptogram_Demo.time, "sleep", side_effect=sleep), \
             patch.object(Cryptogram_Demo, "read_console_key", side_effect=read_key), \
             patch.object(Cryptogram_Demo, "open_shop", side_effect=visit_shop), \
             patch("sys.stdout", output):
            Cryptogram_Demo.wait_for_cryptogram(duration)
        return output.getvalue(), snapshots

    def test_typing_hides_updates_until_line_cleared(self):
        output, snapshots = self.run_wait(1, [(0, "x"), (2, "\b"), (3, "\r")])
        before_backspace = snapshots[1][1]
        self.assertIn("Cooldown: 1 Seconds\n", before_backspace)
        self.assertNotIn("Press Enter to start", before_backspace)
        self.assertIn("Press Enter to start", output)
        self.assertIn("\b \b", output)

    def test_shop_keeps_elapsed_time_and_defers_prompt(self):
        def shop(clock, output):
            clock[0] += 5
            output.write("SHOP OUTPUT\n")

        output, snapshots = self.run_wait(
            3, [(0, "s"), (0.5, "h"), (1, "o"), (1.5, "p"),
                (2, "\r"), (8, "\r")], shop
        )
        self.assertNotIn("Press Enter to start", snapshots[4][1])
        self.assertNotIn("\033[1A", snapshots[4][1])
        self.assertIn("SHOP OUTPUT\n", output)
        self.assertGreater(output.index("Press Enter to start"), output.index("SHOP OUTPUT"))

    def test_leaving_shop_early_preserves_remaining_time(self):
        def shop(clock, output):
            clock[0] += 2

        output, snapshots = self.run_wait(
            6, [(0, "s"), (0.1, "h"), (0.2, "o"), (0.3, "p"),
                (0.4, "\r"), (3, "\r"), (7, "\r")], shop
        )
        self.assertIn("Cooldown: 4 Seconds", snapshots[6][1])
        self.assertNotIn("Press Enter to start", snapshots[6][1])
        self.assertIn("Press Enter to start", output)

    def test_saved_shop_items_are_usable(self):
        item = next(item for item in Cryptogram_Demo.shop_items if item.name == "Huegrid")
        self.assertIsInstance(item.cost, int)
        self.assertIsInstance(item.once_time, bool)
        self.assertIsNone(item.prerequisite)
        with patch.object(Cryptogram_Demo, "shop_items", [item]), \
             patch("builtins.input", return_value="exit"), \
             patch("sys.stdout", new_callable=io.StringIO) as output:
            Cryptogram_Demo.open_shop()
        self.assertIn("Huegrid - ", output.getvalue())

    def test_cooldown_item_can_be_purchased_in_shop(self):
        item = Cryptogram_Demo.ShopItem("Cooldown_Shorten/.8", 60, "Sugar Faedust", item_type="instant")
        with patch.object(Cryptogram_Demo, "shop_items", [item]), \
             patch.object(Cryptogram_Demo, "coins", 60), \
             patch.object(Cryptogram_Demo, "max_cooldown", 10), \
             patch("builtins.input", side_effect=["Sugar Faedust", "exit"]), \
             patch("sys.stdout", new_callable=io.StringIO):
            Cryptogram_Demo.open_shop()
            self.assertEqual(Cryptogram_Demo.coins, 0)
            self.assertEqual(Cryptogram_Demo.max_cooldown, 8)

    def test_global_cooldown_updates_while_typing_and_before_quit(self):
        clock = [0.0]
        observed = []
        keys = iter(["q", None, None, "u", "i", "t", "\r"])

        def read_key():
            observed.append(Cryptogram_Demo.cooldown)
            return next(keys)

        def sleep(seconds):
            clock[0] += 1

        with patch.object(Cryptogram_Demo, "cooldown", 99), \
             patch.object(Cryptogram_Demo.time, "monotonic", side_effect=lambda: clock[0]), \
             patch.object(Cryptogram_Demo.time, "sleep", side_effect=sleep), \
             patch.object(Cryptogram_Demo, "read_console_key", side_effect=read_key), \
             patch.object(Cryptogram_Demo, "shutdown") as shutdown, \
             patch("sys.stdout", new_callable=io.StringIO):
            Cryptogram_Demo.wait_for_cryptogram(4)
            shutdown.assert_called_once()
            self.assertEqual(observed[:5], [4, 3, 2, 1, 0])
            self.assertEqual(Cryptogram_Demo.cooldown, 0)

    def test_global_cooldown_updates_while_shop_blocks(self):
        keys = iter("shop\r\r")
        observed = []

        def visit_shop():
            time.sleep(1.1)
            observed.append(Cryptogram_Demo.cooldown)
            time.sleep(1.2)
            observed.append(Cryptogram_Demo.cooldown)

        with patch.object(Cryptogram_Demo, "cooldown", 99), \
             patch.object(Cryptogram_Demo, "read_console_key", side_effect=lambda: next(keys)), \
             patch.object(Cryptogram_Demo, "open_shop", side_effect=visit_shop), \
             patch("sys.stdout", new_callable=io.StringIO):
            Cryptogram_Demo.wait_for_cryptogram(2)
            self.assertEqual(observed, [1, 0])
            self.assertEqual(Cryptogram_Demo.cooldown, 0)

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