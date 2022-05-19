class _SoC:
    pass


class BasebandSoC(_SoC):
    def __init__(self, *, gold_cert_id: int, nonce: bytes, serial: bytes):
        self.nonce = nonce
        self.gc_id = gold_cert_id
        self.serial = serial

    @property
    def nonce(self) -> bytes:
        return self._nonce

    @nonce.setter
    def nonce(self, nonce: bytes):
        if not isinstance(nonce, bytes):
            raise TypeError("Baseband nonce must be of type 'bytes'")

        if len(nonce) != 20:
            raise ValueError('Baseband nonce must be 20 bytes long')

        self._nonce = nonce

    @property
    def gc_id(self) -> int:
        return self._gc_id

    @gc_id.setter
    def gc_id(self, gc_id: int):
        if not isinstance(gc_id, int):
            raise TypeError("Baseband gold cert ID must be of type 'int'")

        self._gc_id = gc_id

    @property
    def serial(self) -> bytes:
        return self._serial

    @serial.setter
    def serial(self, serial: bytes):
        if not isinstance(serial, bytes):
            raise TypeError("Baseband serial must be of type 'bytes'")

        self._serial = serial
