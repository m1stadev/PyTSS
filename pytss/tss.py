import plistlib
import re
from random import getrandbits
from uuid import UUID

from aiohttp import ClientSession

from .device import Device
from .firmware import Firmware, FirmwareImage
from .manifest import BuildIdentity, BuildManifest, RestoreType

TSS_API = 'http://gs.apple.com/TSS/controller'
TSS_HEADERS = {
    'Cache-Control': 'no-cache',
    'Content-Type': 'text/xml; charset="utf-8"',
    'User-Agent': 'InetURL/1.0',
}
TSS_PARAMS = {'action': 2}

TSS_CLIENT_VERSION = 'libauthinstall-850.0.2'


class TSSResponse:
    def __init__(self, response: str):
        self._response = response

        if re.match('STATUS+=[0-9]+&MESSAGE=[a-zA-Z]+', response) is None:
            raise ValueError('Invalid TSS response provided')

        for r in response.split('&'):
            if r.split('=')[0] == 'STATUS':
                status_code = int(r.split('=')[1])
                if status_code != 0:
                    pass  # raise error

            elif r.split('=')[0] == 'REQUEST_STRING':
                apticket = plistlib.loads(str.encode(r.split('=', 1)[1]))
                if 'ApImg4Ticket' not in apticket.keys():
                    raise ValueError('ApTicket not found in TSS response')

                self.data = apticket['ApImg4Ticket']

            elif r.split('=')[0] == 'MESSAGE':  # Not handling response message for now
                pass

            else:
                raise ValueError(f"Unknown item found in TSS response: '{r}'")


class TSS:
    def __init__(self, device: Device, build_identity: BuildIdentity):
        self.device = device
        self.identity = build_identity

        self._create_base_request()

    def _create_base_request(self) -> None:
        request = {
            '@Locality': 'en_US',
            '@HostPlatformInfo': 'mac',
            '@VersionInfo': TSS_CLIENT_VERSION,
            '@UUID': str(
                UUID(bytes=getrandbits(128).to_bytes(16, 'big'), version=4)
            ).upper(),
        }

        request['ApBoardID'] = self.device.board_id
        request['ApChipID'] = self.device.chip_id
        request['ApECID'] = self.device.ecid
        request['ApSecurityDomain'] = self.identity.security_domain

        request['UniqueBuildID'] = self.identity.unique_buildid

        request['ApNonce'] = self.device.apnonce
        request['ApProductionMode'] = True

        if self.device.supports_img4:
            request['@ApImg4Ticket'] = True
            request['ApSecurityMode'] = True

            request['SepNonce'] = self.device.sepnonce

            if self.identity.pearlcertrootpub is not None:
                request['PearlCertificationRootPub'] = self.identity.pearlcertrootpub
        else:
            request['@APTicket'] = True

        # TODO: put in the rest of what tsschecker does here

        self._request = request

    @classmethod
    async def create_request(
        self, device: Device, firmware: Firmware, *, restore_type: RestoreType
    ) -> 'TSS':
        if device.ecid is None:
            raise TypeError('No ECID is set')

        if device.apnonce is None:
            raise TypeError('No ApNonce is set')

        if device.sepnonce is None:
            raise TypeError('No SepNonce is set')

        manifest = BuildManifest(await firmware.read('BuildManifest.plist'))
        identity = manifest.get_identity(device, restore_type)

        return TSS(device, identity)

    def add_image(self, image: FirmwareImage) -> None:
        # TODO: iterate thru every FirmwareImage and write an internal function for adding each tag
        pass

    async def send(self) -> TSSResponse:
        async with ClientSession() as session, session.post(
            TSS_API,
            params=TSS_PARAMS,
            headers=TSS_HEADERS,
            data=plistlib.dumps(self._request),
        ) as resp:
            return TSSResponse(await resp.text())
