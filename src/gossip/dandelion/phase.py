from time import time
from hashlib import shake_128


class DandelionPhase:
    def __init__(self, seed: bytes, epoch_interval_secs: int):
        self.seed = seed  # Seed intended to be from good random source like urandom
        assert len(self.seed) == 32
        self.epoch = int(time())
        self.epoch_interval = epoch_interval_secs
        self._is_stem = True
        self.phase_id = b''


    def _update_stem_phase(self, cur_time):
        self.epoch = cur_time
        # Hash the seed with the time stamp to produce 8 pseudorandom bytes
        # Produce an len(8) byte string for time as well for year 2038 problem
        self.phase_id = shake_128(
            self.seed +
            int.to_bytes(cur_time, 8, 'big')).digest(8)

        # Use first byte of phase id as random source for stem phase picking
        if int.from_bytes(self.phase_id[0], 'big') % 2:
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
