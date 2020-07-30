from typing import Callable
from typing import Iterable

from threading import Thread

from utils.bettersleep import better_sleep


def _onionr_thread(func: Callable, args: Iterable,
                   sleep: int, initial_sleep):
    better_sleep(initial_sleep)
    while True:
        func(*args)
        better_sleep(sleep)


def add_onionr_thread(
        func: Callable, args: Iterable,
        sleep: int, initial_sleep: int = 5):
    """Spawn a new onionr thread that exits when the main thread does.

    Runs in an infinite loop with sleep between calls
    Passes in an interable args and sleep variables"""
    Thread(target=_onionr_thread,
           args=(func, args, sleep, initial_sleep), daemon=True).start()
