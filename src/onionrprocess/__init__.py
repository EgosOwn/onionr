from audioop import mul
import multiprocessing


def run_func_in_new_process(func, *args, **kwargs):
    queue = multiprocessing.Queue()

    def _wrap_func():
        if args and kwargs:
            queue.put(func(*args, **kwargs))
        elif args:
            queue.put(func(*args))
        elif kwargs:
            queue.put(func(**kwargs))
        else:
            queue.put(func())

    proc = multiprocessing.Process(target=_wrap_func, daemon=True)
    proc.start()
    return queue.get()

