from time import time


class WotTimestamp(int):
    def __new__(cls, value: int):
        value = int(value)
        if value <= 0:
            raise ValueError("Timestamp cannot be negative or zero")
        elif value > time():
            raise ValueError("Timestamp cannot be in the future")
        return super().__new__(cls, value)