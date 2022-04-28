from hashlib import sha1, sha384
from typing import Optional
from .errors import APIError, DeviceError

import aiohttp
import asyncio


class Device:
    async def init(
        self,
        identifier: str,
        ecid: str,
        board: str = None,
        boot_nonce: str = None,
        apnonce: str = None,
        sepnonce: str = None,
    ):
        self.ecid = ecid

        if getattr(self, 'board', None) is None and board is not None:
            self.board = self._verify_board(board)

        self.boot_nonce = boot_nonce

        self.apnonce = apnonce

        self.sepnonce = sepnonce

        if (boot_nonce and apnonce) and (not 0x8020 <= self.cpid < 0x8900):
            await self._verify_apnonce_pair()

        return self

    @property
    def apnonce(self) -> bytes:
        return self._apnonce

    @apnonce.setter
    def apnonce(self, apnonce: Optional[Union[bytes, str]]) -> None:
        apnonce_len = 32 if 0x8010 <= self.cpid < 0x8900 else 20

        if apnonce is not None:
            if isinstance(apnonce, str):  # Assume hexadecimal
                try:
                    apnonce = bytes.fromhex(apnonce)
                except TypeError:
                    raise DeviceError('Invalid ApNonce provided.')

            if len(apnonce) != apnonce_len:
                raise DeviceError('Invalid ApNonce provided.')
        else:
            pass  # generate apnonce here

        self._apnonce = apnonce

    @property
    def ecid(self) -> int:
        return self._ecid

    @ecid.setter
    def ecid(self, ecid: Union[int, str]) -> None:
        if isinstance(ecid, str):  # Assume hexadecimal
            try:
                ecid = int(ecid, 16)
            except ValueError:
                raise DeviceError('Invalid ECID provided.')

        self._ecid = ecid

    @property
    def boot_nonce(self) -> bytes:
        return self._boot_nonce

    @boot_nonce.setter
    def boot_nonce(self, boot_nonce: Optional[Union[str, bytes]]) -> None:
        if boot_nonce is not None:
            if isinstance(boot_nonce, str):  # Assume hexadecimal
                try:
                    boot_nonce = bytes.fromhex(boot_nonce)
                except TypeError:
                    raise DeviceError('Invalid Boot Nonce provided.')

        else:
            pass  # make random bytes here

        self._boot_nonce = boot_nonce

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
                    raise DeviceError('Invalid SepNonce provided.')

            if len(sepnonce) != 20:
                raise DeviceError('Invalid SepNonce provided.')
        else:
            pass  # generate sepnonce here

        self._sepnonce = sepnonce

    @property
    def supports_img4(self) -> bool:
        return not 0x8900 < self.cpid < 0x8955

    async def _fetch_device_info(self, identifier: str) -> None:
        async with aiohttp.ClientSession() as session, session.get(
            f'https://api.ipsw.me/v4/devices'
        ) as resp:
            if resp.status != 200:
                raise APIError(
                    'Failed to request device information from IPSW.me.', resp.status
                )

            data = await resp.json()

        for device in data:
            if device['identifier'].casefold() == identifier.casefold():
                self._data = device
                break
        else:
            raise DeviceError('Invalid device identifier provided.')

        self.identifier = self._data['identifier']

        valid_boards = [
            board
            for board in self._data['boards']
            if board['boardconfig']
            .lower()
            .endswith('ap')  # Exclude development boards that may show up
        ]

        if len(valid_boards) == 1:
            self.board = valid_boards[0]['boardconfig']
            self.cpid = valid_boards[0]['cpid']
            self.bdid = valid_boards[0]['bdid']

    async def _verify_board(self, board: str) -> str:
        for b in [
            b
            for b in self._data['boards']
            if board['boardconfig']
            .lower()
            .endswith('ap')  # Exclude development boards that may show up
        ]:
            if b['boardconfig'].casefold() == board.casefold():
                board = b['boardconfig']
                break
        else:
            raise DeviceError('Invalid board config provided.')

        return board

    def __verify_apnonce_pair(self) -> bool:
        boot_nonce = bytes.fromhex(self.boot_nonce.removeprefix('0x'))
        if len(self.apnonce) == 64:
            apnonce = sha384(boot_nonce).hexdigest()[:-32]
        elif len(self.apnonce) == 40:
            apnonce = sha1(boot_nonce).hexdigest()

        if apnonce != self.apnonce:
            raise DeviceError('Invalid Boot Nonce-ApNonce pair provided.')

    async def _verify_apnonce_pair(self) -> Optional[bool]:
        await asyncio.to_thread(self.__verify_apnonce_pair)
