from random import getrandbits
from typing import Optional, Union

import aiohttp

from .errors import APIError
from .firmware import Firmware

RELEASE_API = 'https://api.ipsw.me/v4/device'
BETA_API = 'https://api.m1sta.xyz/betas'


def _generate_bytes(length: int) -> bytes:
    return bytes(getrandbits(8) for _ in range(length))


class Device:
    def __init__(
        self,
        identifier: str,
        chip_id: int,
        board_id: int,
        *,
        ecid: Optional[Union[int, str]] = None,
    ):
        self.identifier = identifier
        self.chip_id = chip_id
        self.board_id = board_id

        self.ecid = ecid
        self.apnonce = None
        self.sepnonce = None

    @property
    def apnonce(self) -> bytes:
        return self._apnonce

    @apnonce.setter
    def apnonce(self, apnonce: Optional[Union[bytes, str]]) -> None:
        apnonce_len = 32 if 0x8010 <= self.chip_id < 0x8900 else 20

        if apnonce is not None:
            if isinstance(apnonce, str):  # Assume hexadecimal
                try:
                    apnonce = bytes.fromhex(apnonce)
                except TypeError:
                    raise ValueError('Invalid ApNonce provided')

            if len(apnonce) != apnonce_len:
                raise ValueError('Invalid ApNonce provided')
        else:
            apnonce = _generate_bytes(apnonce_len)

        self._apnonce = apnonce

    @property
    def ecid(self) -> int:
        return self._ecid

    @ecid.setter
    def ecid(self, ecid: Optional[Union[int, str]]) -> None:
        if isinstance(ecid, str):  # Assume hexadecimal
            try:
                ecid = int(ecid, 16)
            except ValueError:
                raise ValueError('Invalid ECID provided')

        self._ecid = ecid

    @property
    def sepnonce(self) -> bytes:
        return self._sepnonce

    @sepnonce.setter
    def sepnonce(self, sepnonce: Optional[Union[bytes, str]]) -> None:
        if sepnonce is not None:
            if isinstance(sepnonce, str):
                try:
                    sepnonce = bytes.fromhex(sepnonce)
                except TypeError:
                    raise ValueError('Invalid SepNonce provided')

            if len(sepnonce) != 20:
                raise ValueError('Invalid SepNonce provided')
        else:
            sepnonce = _generate_bytes(20)

        self._sepnonce = sepnonce

    @property
    def supports_img4(self) -> bool:
        return not 0x8900 < self.chip_id < 0x8955

    async def fetch_firmware(
        self, *, version: str = None, buildid: str = None
    ) -> Firmware:
        if version is None and buildid is None:
            raise ValueError('Either a version or buildid must be provided')

        async with aiohttp.ClientSession() as session:
            async with session.get(f'{RELEASE_API}/{self.identifier}') as resp:
                if resp.status != 200:
                    raise APIError(
                        f"Failed to request firmwares for device identfier: '{self.identifier}'",
                        resp.status,
                    )

                data = await resp.json()

            if buildid:
                firm = next(
                    (
                        f
                        for f in data['firmwares']
                        if f['buildid'].casefold() == buildid.casefold()
                    ),
                    None,
                )

            elif version:
                firm = next(
                    (
                        f
                        for f in data['firmwares']
                        if f['version'].casefold() == version.casefold()
                    ),
                    None,
                )

            if firm is None:
                async with session.get(f'{BETA_API}/{self.identifier}') as resp:
                    if resp.status != 200:
                        raise APIError(
                            f"Failed to request firmwares for device identfier: '{self.identifier}'",
                            resp.status,
                        )

                    data = await resp.json()

                if buildid:
                    firm = next(
                        (
                            f
                            for f in data
                            if f['buildid'].casefold() == buildid.casefold()
                        ),
                        None,
                    )

                elif version:
                    firm = next(
                        (
                            f
                            for f in data
                            if f['version'].casefold() == version.casefold()
                        ),
                        None,
                    )

        if firm is None:
            raise ValueError('No firmware was found for the provided version/buildid')

        return Firmware(firm)
