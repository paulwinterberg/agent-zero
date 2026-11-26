import unittest

import pygame

from main.core import hints


class HintsModuleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()

    def tearDown(self):
        hints._message = None
        hints._should_pause_game = False
        hints._remaining_time = 0.0

    def test_paused_hint_waits_for_space_to_close(self):
        hints.display("Tutorial message", should_pause_game=True)

        self.assertTrue(hints._update(1, []))
        self.assertTrue(hints._is_active())

        space_pressed = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
        self.assertTrue(hints._update(1, [space_pressed]))
        self.assertFalse(hints._is_active())

    def test_timed_hint_expires_after_display_time(self):
        hints.display("Timed message", display_time=1)

        self.assertFalse(hints._update(0.5, []))
        self.assertTrue(hints._is_active())
        self.assertFalse(hints._update(0.5, []))
        self.assertFalse(hints._is_active())

    def test_negative_display_time_is_rejected(self):
        with self.assertRaises(ValueError):
            hints.display("Timed message", display_time=-1)


if __name__ == "__main__":
    unittest.main()
