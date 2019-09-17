from __future__ import annotations
from typing import Union, Generic
from gevent import sleep
def wait_for_set_var(obj, attribute, sleep_seconds: Union[int, float]=0):
    """Wait for an object to get an attribute with an optional sleep time"""
    while not hasattr(obj, attribute):
        if hasattr(obj, attribute): break
        if sleep_seconds > 0: sleep(sleep_seconds)