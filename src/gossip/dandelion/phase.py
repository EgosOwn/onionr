from time import time
from hashlib import shake_128
from secrets import randbits
import secrets

seed = secrets.token_bytes(32)


class DandelionPhase:
    def __init__(self, epoch_interval_secs: int):
        assert len(seed) == 32
        self.epoch = int(time())
        self.epoch_interval = epoch_interval_secs
        self._is_stem = bool(randbits(1))
        self.phase_id = b''


    def _update_stem_phase(self, cur_time):
        self.epoch = cur_time
        # Hash the seed with the time stamp to produce 8 pseudorandom bytes
        # Produce an len(8) byte string for time as well for year 2038 problem
        self.phase_id = shake_128(
            seed +
            int.to_bytes(cur_time, 8, 'big')).digest(8)

        # Use first byte of phase id as random source for stem phase picking
        if self.phase_id[0] % 2:
            self._is_stem = True
        else:
            self._is_stem = False


    def remaining_time(self) -> int:
        current_time = int(time())

        return max(0, self.epoch_interval - (current_time - self.epoch))


    def is_stem_phase(self) -> bool:
        current_time = int(time())
        if current_time - self.epoch >= self.epoch_interval:
            self._update_stem_phase(current_time)
        return self._is_stem
