import multiprocessing

import mimcvdf


def _wrap_vdf_create(queue, block_data_bytes, rounds):
    queue.put(mimcvdf.vdf_create(block_data_bytes, rounds))


def _wrap_vdf_verify(queue, block_data_bytes, block_hash_hex, rounds):
    queue.put(mimcvdf.vdf_verify(block_data_bytes, block_hash_hex, rounds))



def rounds_for_bytes(byte_count: int):
    return byte_count * 1000



def create_vdf(block_data_bytes):
    rounds = rounds_for_bytes(block_data_bytes)
    queue = multiprocessing.Queue()
    vdf_proc = multiprocessing.Process(
        target=_wrap_vdf_create,
        args=(queue, block_data_bytes, rounds))
    vdf_proc.start()
    vdf_proc.join()
    return queue.get()


def verify_vdf(block_hash_hex, block_data_bytes):
    rounds = rounds_for_bytes(block_data_bytes)
    if rounds < 10 ** 6:
        # >million rounds it starts to take long enough to warrant a subprocess
        queue = multiprocessing.Queue()
        vdf_proc = multiprocessing.Process(
            target=_wrap_vdf_verify,
            args=(queue, block_data_bytes, block_hash_hex, rounds))
        vdf_proc.start()
        vdf_proc.join()
        return queue.get()
    return mimcvdf.vdf_verify(block_data_bytes, block_hash_hex, rounds)

