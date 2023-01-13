from typing import Callable
import multiprocessing
import time


def _compute(q: multiprocessing.Queue, func: Callable, *args, **kwargs):
    q.put(func(*args, **kwargs))

def subprocess_compute(func: Callable, wallclock_timeout: int, *args, **kwargs):
    """
    Call func in a subprocess, and return the result. Set wallclock_timeout to <= 0 to disable
    Raises TimeoutError if the function does not return in time
    Raises ChildProcessError if the subprocess dies before returning
    """
    q = multiprocessing.Queue()
    p = multiprocessing.Process(
        target=_compute, args=(q, func, *args), kwargs=kwargs, daemon=True)
    wallclock_timeout = max(wallclock_timeout, 0)

    p.start()
    start = time.time()
    while True:
        try:
            return q.get(timeout=1)
        except multiprocessing.queues.Empty:
            if not p.is_alive():
                raise ChildProcessError("Process died before returning")
            if wallclock_timeout:
                if time.time() - start >= wallclock_timeout:
                    raise TimeoutError("Process did not return in time")
                
