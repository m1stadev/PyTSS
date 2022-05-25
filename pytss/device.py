from random import getrandbits
from typing import Optional, Union

import aiohttp

from .errors import APIError
from .firmware import Firmware

RELEASE_API = 'https://api.ipsw.me/v4/device'
BETA_API = 'https://api.m1sta.xyz/betas'


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
        self.ap_nonce = None

        self.sep_nonce = None

    @property
    def ap_nonce(self) -> bytes:
        return self._ap_nonce

    @ap_nonce.setter
    def ap_nonce(self, ap_nonce: Optional[Union[bytes, str]]) -> None:
        ap_nonce_len = 32 if 0x8010 <= self.chip_id < 0x8900 else 20

        if ap_nonce is not None:
            if isinstance(ap_nonce, str):  # Assume hexadecimal
                try:
                    ap_nonce = bytes.fromhex(ap_nonce)
                except TypeError:
                    raise ValueError('Invalid AP nonce provided')

            if len(ap_nonce) != ap_nonce_len:
                raise ValueError('Invalid AP nonce provided')
        else:
            ap_nonce = bytes()  # Set as empty bytes

        self._ap_nonce = ap_nonce

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
    def sep_nonce(self) -> bytes:
        return self._sep_nonce

    @sep_nonce.setter
    def sep_nonce(self, sep_nonce: Optional[Union[bytes, str]]) -> None:
        if not self.is_64bit:
            raise TypeError('32-bit devices do not have SEP')

        if sep_nonce is not None:
            if isinstance(sep_nonce, str):
                try:
                    sep_nonce = bytes.fromhex(sep_nonce)
                except TypeError:
                    raise ValueError('Invalid SEP nonce provided')

            if len(sep_nonce) != 20:
                raise ValueError('Invalid SEP nonce provided')
        else:
            sep_nonce = bytes(getrandbits(8) for _ in range(20))

        self._sep_nonce = sep_nonce

    @property
    def is_64bit(self) -> bool:
        return not 0x8900 < self.chip_id < 0x8955

    @property
    def supports_img4(self) -> bool:
        return self.chip_id == 0x7002 or self.is_64bit

    async def fetch_firmware(
        self, *, version: str = None, buildid: str = None
    ) -> Firmware:
        if version is None and buildid is None:
            raise ValueError('Either a version or buildid must be provided')

        async with aiohttp.ClientSession() as session:
            firmwares = list()
            async with session.get(f'{RELEASE_API}/{self.identifier}') as resp:
                if resp.status == 200:
                    release_data = await resp.json()
                    firmwares.extend(release_data['firmwares'])

            async with session.get(f'{BETA_API}/{self.identifier}') as resp:
                if resp.status == 200:
                    beta_data = await resp.json()
                    firmwares.extend(beta_data)

        if buildid:
            firm = next(
                (f for f in firmwares if f['buildid'].casefold() == buildid.casefold()),
                None,
            )

        elif version:
            firm = next(
                (f for f in firmwares if f['version'].casefold() == version.casefold()),
                None,
            )

        if firm is None:
            raise ValueError('No firmware was found for the provided version/buildid')

        return Firmware(firm)
