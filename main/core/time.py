import time as _time
from threading import Timer
from typing import Callable


def wait(delay_time: float) -> None:
    """Block the current thread for delay_time seconds."""
    if delay_time < 0:
        raise ValueError("delay_time must be non-negative")
    _time.sleep(delay_time)


def delay(delay_time: float, function: Callable[[], None]) -> Timer:
    """Run function on a background thread after delay_time seconds."""
    if delay_time < 0:
        raise ValueError("delay_time must be non-negative")

    timer = Timer(delay_time, function)
    timer.start()
    return timer
