import asyncio
from datetime import datetime
from enum import IntEnum

from remotezip import RemoteZip


class FirmwareImage(IntEnum):
    Baseband = 0x1
    SecureElement = 0x2  # NFC
    Savage = 0x3  # A11 FaceID
    Yonkers = 0x4  # A12+ FaceID
    Vinyl = 0x5  # eSIM
    Rose = 0x6  # U1
    Veridian = 0x7  # BMU (Battery Management Unit)


class Firmware:
    def __init__(self, data: dict) -> None:
        self._data = data
        for key in data.keys():
            if key.lower() in ('identifier', 'signed'):
                continue

            if (
                any(date == key for date in ('releasedate', 'uploaddate'))
                and data[key] is not None
            ):
                setattr(
                    self,
                    key,
                    datetime.strptime(
                        data[key].replace('T', ' ').replace('Z', ''),
                        '%Y-%m-%d %H:%M:%S',
                    ),
                )
            else:
                setattr(self, key, data[key])

    def _read(self, file: str) -> bytes:
        with RemoteZip(self.url) as firm:
            file = next(
                (f for f in firm.namelist() if f.casefold() == file.casefold()), None
            )
            if file is None:
                raise ValueError(f"File not found in firmware: '{file}'")

            return firm.read(file)

    async def read(self, file: str) -> bytes:
        return await asyncio.to_thread(self._read, file)
