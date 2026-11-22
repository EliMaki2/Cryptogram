import unittest
from unittest.mock import patch

import pygame
import Pyscreen


class TestWindowInteraction(unittest.TestCase):
    def setUp(self):
        self.width_scale = patch.object(Pyscreen, "width_ratio", 0.5)
        self.height_scale = patch.object(Pyscreen, "height_ratio", 0.75)
        self.selected_window = patch.object(Pyscreen, "selected_window", None)
        self.width_scale.start()
        self.height_scale.start()
        self.selected_window.start()
        self.addCleanup(self.width_scale.stop)
        self.addCleanup(self.height_scale.stop)
        self.addCleanup(self.selected_window.stop)
        self.window = Pyscreen.Window(400, 600, 500, 200)

    def click(self, pos):
        self.window.event_loop(pygame.event.Event(
            pygame.MOUSEBUTTONDOWN, {"pos": pos, "button": 1}
        ))

    def test_scaled_topbar_click_and_drag(self):
        self.click((260, 156))
        self.assertTrue(self.window.selected)
        self.assertTrue(self.window.dragging)
        self.assertEqual(self.window.drag_offset, (20, 8))

        with patch("pygame.mouse.get_pos", return_value=(310, 186)):
            self.window.update_loop()
        self.assertEqual((self.window.x, self.window.y), (600, 240))

        self.click((310, 186))
        self.assertFalse(self.window.dragging)

    def test_scaled_close_button_click(self):
        self.click((445, 156))
        self.assertTrue(self.window.closing)

    def test_dragging_is_clamped_to_logical_screen(self):
        self.click((260, 156))
        with patch("pygame.mouse.get_pos", return_value=(2000, 2000)):
            self.window.update_loop()
        self.assertEqual(
            (self.window.x, self.window.y),
            (Pyscreen.target_width - self.window.width,
             Pyscreen.target_height - self.window.height),
        )


class TestWindowDrawing(unittest.TestCase):
    def test_ui_tint_preserves_window_content(self):
        class SolidSprite:
            def draw(self, surface):
                surface.fill((33, 99, 77))

        window = Pyscreen.Window(500, 500, 0, 0, closable=False, resizable=False)
        window.sprites.append(SolidSprite())
        output = pygame.Surface((500, 500))

        window.ui_tint = (255, 255, 255)
        window.draw_loop(output)
        self.assertEqual(output.get_at((100, 10))[:3], (200, 200, 200))
        self.assertEqual(output.get_at((250, 250))[:3], (33, 99, 77))

        window.ui_tint = (200, 100, 100)
        window.draw_loop(output)
        self.assertEqual(output.get_at((100, 10))[:3], (157, 79, 79))
        self.assertEqual(output.get_at((250, 250))[:3], (33, 99, 77))

        window.draw_loop(output)
        self.assertEqual(output.get_at((100, 10))[:3], (157, 79, 79))
