from random import getrandbits


def _generate_bytes(length: int) -> bytes:
    return bytes(getrandbits(8) for _ in range(length))
