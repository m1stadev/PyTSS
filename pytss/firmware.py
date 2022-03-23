from datetime import datetime
from remotezip import RemoteZip

import asyncio


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
            try:
                file = next(
                    f for f in firm.namelist() if f.casefold() == file.casefold()
                )
            except StopIteration:
                pass  # raise error

            return firm.read(file)

    async def read(self, file: str) -> bytes:
        return await asyncio.to_thread(self._read, file)
