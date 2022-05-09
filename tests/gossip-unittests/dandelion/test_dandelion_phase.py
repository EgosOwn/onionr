from time import sleep, time
import sys
from hashlib import shake_128
import secrets
import asyncio
import unittest
sys.path.append(".")
sys.path.append("src/")
from gossip.dandelion import phase


class FakePhase:
    def __init__(self, seed, epoch_interval_secs: int):
        self.seed = seed
        assert len(self.seed) == 32
        self.epoch = int(time())
        self.epoch_interval = epoch_interval_secs
        self._is_stem = bool(secrets.randbits(1))
        self.phase_id = b''


    def _update_stem_phase(self, cur_time):
        self.epoch = cur_time
        # Hash the self.seed with the time stamp to produce 8 pseudorandom bytes
        # Produce an len(8) byte string for time as well for year 2038 problem
        self.phase_id = shake_128(
            self.seed +
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


class OnionrGossipTestDandelionPhase(unittest.TestCase):

    def test_dandelion_phase(self):
        epoch = 3 # seconds
        seed = phase.seed
        self.assertTrue(len(seed) == 32)
        p = phase.DandelionPhase(epoch)
        fake_p = FakePhase(phase.seed, epoch)

        assert p.phase_id == fake_p.phase_id

    def test_dandelion_phase_both(self):
        epoch = 3 # seconds
        seed = phase.seed
        self.assertTrue(len(seed) == 32)
        p = phase.DandelionPhase(epoch)
        fake_p = FakePhase(phase.seed, epoch)

        assert p.phase_id == fake_p.phase_id


unittest.main()
