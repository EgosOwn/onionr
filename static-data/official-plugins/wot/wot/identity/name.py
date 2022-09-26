max_len = 21
min_len = 1

class IdentityName(str):
    def __new__(cls, data):
        if data[0] == '0':
            raise ValueError("Name cannot start with 0")
        if not len(data) in list(range(1, 21)):
            raise ValueError(f"Must be in range({min_len}, {max_len})")
        return super().__new__(cls, data)