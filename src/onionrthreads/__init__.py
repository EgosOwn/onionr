from typing import Callable
from typing import Iterable

import traceback
from threading import Thread

from time import sleep

import logger


def _onionr_thread(func: Callable, args: Iterable,
                   sleep_secs: int, initial_sleep):
    if initial_sleep:
        sleep(initial_sleep)
    while True:
        try:
            func(*args)
        except Exception as _:  # noqa
            logger.warn(
                "Onionr thread exception \n" + traceback.format_exc(),
                terminal=True)
        sleep(sleep_secs)


def add_onionr_thread(
        func: Callable, args: Iterable,
        sleep_secs: int, initial_sleep: int = 5):
    """Spawn a new onionr thread that exits when the main thread does.

    Runs in an infinite loop with sleep between calls
    Passes in an interable args and sleep variables"""
    Thread(target=_onionr_thread,
           args=(func, args, sleep_secs, initial_sleep), daemon=True).start()
