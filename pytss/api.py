from .errors import APIError, PyTSSError
from .device import Device
from .firmware import Firmware

import aiohttp

RELEASE_API = 'https://api.ipsw.me/v4/device'
BETA_API = 'https://api.m1sta.xyz/betas'


class FirmwareAPI:
    async def fetch_all_firmwares(self, device: Device) -> Firmware:
        async with aiohttp.ClientSession() as session:
            firmwares = list()
            for api_url in (RELEASE_API, BETA_API):
                async with session.get(f'{api_url}/{device.identifier}') as resp:
                    if resp.status != 200:
                        raise APIError(
                            f'Failed to request firmwares for device: {device.identifier}.',
                            resp.status,
                        )

                    data = await resp.json()

                if api_url == RELEASE_API:
                    firms = data['firmwares']
                elif api_url == BETA_API:
                    firms = data

                for firm in firms:
                    if any(
                        firm['buildid'].casefold() == f.buildid.casefold()
                        for f in firmwares
                    ):
                        continue

                    firmwares.append(Firmware(firm))

        return sorted(
            firmwares,
            key=lambda x: x.buildid,
            reverse=True,
        )

    async def fetch_firmware(
        self, device: Device, buildid: str = None, version: str = None
    ) -> Firmware:
        firmwares = await self.fetch_all_firmwares(device)

        if buildid is None and version is None:
            raise PyTSSError('Must provide either buildid or version.')

        if buildid is not None:
            try:
                return next(
                    firm
                    for firm in firmwares
                    if firm.buildid.casefold() == buildid.casefold()
                )
            except StopIteration:
                pass

        if version is not None:
            try:
                return next(
                    firm
                    for firm in firmwares
                    if firm.version.casefold().replace(' ', '')
                    == version.casefold().replace(' ', '')
                )
            except StopIteration:
                pass

        raise PyTSSError('Unable to find firmware.')
