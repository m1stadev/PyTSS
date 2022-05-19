class _SoC:
    def _class_name(self) -> str:
        return type(self).__name__


class Baseband(_SoC):
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
            raise TypeError(f"{self._class_name} nonce must be of type 'bytes'")

        self._nonce = nonce

    @property
    def gc_id(self) -> int:
        return self._gc_id

    @gc_id.setter
    def gc_id(self, gc_id: int):
        if not isinstance(gc_id, int):
            raise TypeError(
                f"{self._class_name} gold certificate ID must be of type 'int'"
            )

        self._gc_id = gc_id

    @property
    def serial(self) -> bytes:
        return self._serial

    @serial.setter
    def serial(self, serial: bytes):
        if not isinstance(serial, bytes):
            raise TypeError(f"{self._class_name} serial must be of type 'bytes'")

        self._serial = serial
