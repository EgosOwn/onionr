import multiprocessing

import mimcvdf


def _wrap_vdf_create(queue, block_data_bytes, rounds):
    queue.put(mimcvdf.vdf_create(block_data_bytes, rounds))


def do_vdf(block_data_bytes):
    queue = multiprocessing.Queue()
    vdf_proc = multiprocessing.Process(target=_wrap_vdf_create, args=(queue, block_data_bytes, 1000))
    vdf_proc.start()
    vdf_proc.join()
    return queue.get()