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
        boardconfig: str = None,
        generator: str = None,
        apnonce: str = None,
        sepnonce: str = None,
    ):
        await self._fetch_device_info(identifier)
        self.ecid = self.verify_ecid(ecid)

        if getattr(self, 'board', None) is None and boardconfig is not None:
            self.board = self._verify_board(boardconfig)

        self.generator = self._verify_generator(generator) if generator else None

        self.apnonce = self._verify_nonce(apnonce) if apnonce else None

        self.sepnonce = self._verify_nonce(sepnonce) if sepnonce else None

        if (generator and apnonce) and (not 0x8020 <= self.cpid < 0x8900):
            await self._verify_apnonce_pair()

        return self

    @property
    def is_64bit(self) -> bool:
        return 0x8960 <= self.cpid < 0x8900

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

    # Data verification functions
    def _verify_ecid(self, ecid: str) -> str:
        try:
            int(ecid, 16)  # Make sure the ECID provided is hexadecimal, not decimal
        except (ValueError, TypeError):
            raise DeviceError('Invalid ECID provided.')

        ecid = hex(int(ecid, 16)).removeprefix('0x')
        if len(ecid) not in (
            11,
            13,
            14,
        ):  # All hex ECIDs without zero-padding are either 11, 13, or 14 characters long
            raise DeviceError('Invalid ECID provided.')

        return ecid

    async def _verify_board(self, boardconfig: str) -> str:
        for board in [
            board
            for board in self._data['boards']
            if board['boardconfig']
            .lower()
            .endswith('ap')  # Exclude development boards that may show up
        ]:
            if board['boardconfig'].casefold() == boardconfig.casefold():
                boardconfig = board['boardconfig']
                break
        else:
            raise DeviceError('Invalid board config provided.')

        return boardconfig

    def _verify_generator(self, generator: str) -> str:
        if generator is None:
            return

        if not generator.startswith('0x'):  # Generator must start wth '0x'
            raise DeviceError('Invalid generator provided.')

        if (
            len(generator) != 18
        ):  # Generator must be 18 characters long, including '0x' prefix
            raise DeviceError('Invalid generator provided.')

        try:
            int(generator, 16)  # Generator must be hexadecimal
        except:
            raise DeviceError('Invalid generator provided.')

        return generator.lower()

    def _verify_nonce(self, nonce: str) -> str:
        if any(arg is None for arg in (self.cpid, nonce)):
            return

        try:
            int(nonce, 16)
        except ValueError or TypeError:
            raise DeviceError('Invalid nonce provided.')

        if 0x8010 <= self.cpid < 0x8900:  # A10+ device nonces are 64 characters long
            nonce_len = 64
        else:  # A9 and below device nonces are 40 characters
            nonce_len = 40

        if len(nonce) != nonce_len:
            raise DeviceError('Invalid nonce provided.')

        return nonce.lower()

    def __verify_apnonce_pair(self) -> bool:
        gen = bytes.fromhex(self.generator.removeprefix('0x'))
        if len(self.apnonce) == 64:
            gen_hash = sha384(gen).hexdigest()[:-32]
        elif len(self.apnonce) == 40:
            gen_hash = sha1(gen).hexdigest()

        if gen_hash != self.apnonce:
            raise DeviceError('Invalid generator-ApNonce pair provided.')

    async def _verify_apnonce_pair(self) -> Optional[bool]:
        await asyncio.to_thread(self.__verify_apnonce_pair)
