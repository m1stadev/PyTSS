from typing import Optional, Union

import aiohttp

from .errors import APIError
from .firmware import Firmware
from .utils import _generate_bytes

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

        self.bb_serial = None
        self.bb_nonce = None

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
                    raise ValueError('Invalid ap_nonce provided')

            if len(ap_nonce) != ap_nonce_len:
                raise ValueError('Invalid ap_nonce provided')
        else:
            ap_nonce = _generate_bytes(ap_nonce_len)

        self._ap_nonce = ap_nonce

    @property
    def bb_nonce(self) -> bytes:
        return self._bb_nonce

    @bb_nonce.setter
    def bb_nonce(self, bb_nonce: Optional[Union[bytes, str]]) -> None:
        if bb_nonce is not None:
            if isinstance(bb_nonce, str):
                try:
                    bb_nonce = bytes.fromhex(bb_nonce)
                except TypeError:
                    raise ValueError('Invalid Baseband Nonce provided')

            if len(bb_nonce) != 20:
                raise ValueError('Invalid Baseband Nonce provided')
        else:
            bb_nonce = _generate_bytes(20)

        self._bb_nonce = bb_nonce

    @property
    def bb_serial(self) -> bytes:
        return self._bb_serial

    @bb_serial.setter
    def bb_serial(self, bb_serial: Optional[Union[bytes, str]]) -> None:
        if bb_serial is not None:
            if isinstance(bb_serial, str):
                try:
                    bb_serial = bytes.fromhex(bb_serial)
                except TypeError:
                    raise ValueError('Invalid Baseband serial number provided')

            if len(bb_serial) != 4:
                raise ValueError('Invalid Baseband serial number provided')
        else:
            bb_serial = _generate_bytes(4)

        self._bb_serial = bb_serial

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
        if sep_nonce is not None:
            if isinstance(sep_nonce, str):
                try:
                    sep_nonce = bytes.fromhex(sep_nonce)
                except TypeError:
                    raise ValueError('Invalid sep_nonce provided')

            if len(sep_nonce) != 20:
                raise ValueError('Invalid sep_nonce provided')
        else:
            sep_nonce = _generate_bytes(20)

        self._sep_nonce = sep_nonce

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
