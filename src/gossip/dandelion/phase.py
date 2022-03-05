from time import time
from hashlib import shake_128


class DandelionPhase:
    def __init__(self, seed: bytes, epoch_interval_secs: int):
        self.seed = seed  # Seed intended to be from good random source like urandom
        assert len(self.seed) == 32
        self.epoch = int(time())
        self.epoch_interval = epoch_interval_secs
        self._is_stem = True


    def _update_stem_phase(self, cur_time):
        self.epoch = cur_time
        # Hash the seed with the time stamp to produce 1 pseudorandom byte
        # We produce an len(8) byte string for year 2038 problem
        choice = shake_128(
            self.seed +
            int.to_bytes(cur_time, 8, 'big')).digest(1)

        # If the byte is even
        if int.from_bytes(choice, 'big') % 2:
            self._is_stem = True
        else:
            self._is_stem = False


    def remaining_time(self) -> int:
        current_time = int(time())
        return self.epoch_interval - (current_time - self.epoch)


    def is_stem_phase(self) -> bool:
        current_time = int(time())
        if current_time - self.epoch >= self.epoch_interval:
            self._update_stem_phase(current_time)
        return self._is_stem
