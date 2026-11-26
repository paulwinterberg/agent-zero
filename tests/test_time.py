import threading
import time
import unittest

from main.core.time import delay, wait


class TimeModuleTests(unittest.TestCase):
    def test_wait_blocks_for_requested_duration(self):
        started = time.monotonic()

        wait(0.03)

        self.assertGreaterEqual(time.monotonic() - started, 0.02)

    def test_delay_runs_callback_asynchronously_after_interval(self):
        callback_finished = threading.Event()
        callback_thread = []
        caller_thread = threading.current_thread()
        started = time.monotonic()

        def callback():
            callback_thread.append(threading.current_thread())
            callback_finished.set()

        timer = delay(0.05, callback)
        try:
            self.assertFalse(callback_finished.is_set())
            self.assertTrue(callback_finished.wait(timeout=1))
            self.assertGreaterEqual(time.monotonic() - started, 0.04)
            self.assertIsNot(callback_thread[0], caller_thread)
        finally:
            timer.cancel()

    def test_negative_delay_time_is_rejected(self):
        with self.assertRaises(ValueError):
            wait(-0.1)

        with self.assertRaises(ValueError):
            delay(-0.1, lambda: None)


if __name__ == "__main__":
    unittest.main()
