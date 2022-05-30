import plistlib
import re
from random import getrandbits
from uuid import UUID

from aiohttp import ClientSession

from ._utils import FrozenUserDict
from .device import Device
from .errors import APIError
from .firmware import Firmware, FirmwareImage
from .manifest import BuildIdentity, BuildManifest, RestoreType
from .soc import Baseband, _SoC

TSS_API = 'http://gs.apple.com/TSS/controller'
TSS_HEADERS = {
    'Cache-Control': 'no-cache',
    'Content-Type': 'text/xml; charset="utf-8"',
    'User-Agent': 'InetURL/1.0',
}
TSS_PARAMS = {'action': 2}

TSS_CLIENT_VERSION = 'libauthinstall-850.0.2'


class TSSResponse(FrozenUserDict):
    def __init__(self, response: str):
        self._response = response

        if re.match('STATUS+=[0-9]+&MESSAGE=[a-zA-Z]+', response) is None:
            raise ValueError('Invalid TSS response provided')

        for r in response.split('&'):
            if r.split('=')[0] == 'STATUS':
                status_code = int(r.split('=')[1])
                if status_code != 0:
                    raise APIError(f'Failed to receive TSS response', status_code)

            elif r.split('=')[0] == 'REQUEST_STRING':
                self.data = plistlib.loads(str.encode(r.split('=', 1)[1]))

            elif r.split('=')[0] == 'MESSAGE':  # Not handling response message for now
                pass

            else:
                raise ValueError(f"Unknown item found in TSS response: '{r}'")


class TSS:
    def __init__(self, device: Device, build_identity: BuildIdentity):
        self.device = device
        self.identity = build_identity

        self._create_base_request()
        self._add_ap_firmware()
        self._images: list = []

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

        if 'UniqueBuildID' in self.identity.keys():
            request['UniqueBuildID'] = self.identity['UniqueBuildID']
        else:
            raise KeyError('Unique Build ID not found in build identity')

        request['ApNonce'] = self.device.ap_nonce
        request['ApProductionMode'] = True

        if self.device.is_64bit:
            request['@ApImg4Ticket'] = True
            request['ApSecurityMode'] = True

            request['SepNonce'] = self.device.sep_nonce

            if 'PearlCertificationRootPub' in self.identity.keys():
                request['PearlCertificationRootPub'] = self.identity[
                    'PearlCertificationRootPub'
                ]
        else:
            request['@APTicket'] = True

        # TODO: put in the rest of what tsschecker does here

        self._request = request

    def _handle_restore_request_rules(self, image: dict) -> None:
        for rule in image['Info']['RestoreRequestRules']:
            break_ = False
            for key, val in rule['Conditions'].items():
                if break_ == True:
                    break

                conditions_mapping = {
                    'ApRawProductionMode': 'ApProductionMode',
                    'ApCurrentProductionMode': 'ApProductionMode',
                    'ApRawSecurityMode': 'ApSecurityMode',
                    'ApRequiresImage4': 'ApSupportsImg4',
                    'ApDemotionPolicyOverride': 'DemotionPolicy',
                    'ApInRomDFU': 'ApInRomDFU',
                }
                if key in conditions_mapping.keys():
                    if val == '':
                        val = None

                    if key == 'ApRequiresImage4':
                        val2 = self.device.supports_img4
                    else:
                        val2 = self._request.get(conditions_mapping[key])
                    if val != val2:
                        break_ = True
                else:
                    break_ = True

            if break_ == True:
                continue

            actions = rule['Actions']
            for key, val in actions.items():
                if val != 255:
                    self._request.pop(key, None)
                    image[key] = val

    def _add_ap_firmware(self) -> None:
        request = {}

        for name, img in self.identity['Manifest'].items():
            # These are only included in their respective SoC's requests
            if any(
                name.startswith(i)
                for i in (
                    'BasebandFirmware',
                    'Baobab,',
                    'BMU,',
                    'eUICC,',
                    'Rap,',
                    'Savage,',
                    'SE,',
                    'Timer,',
                    'Yonkers,',
                )
            ):
                continue

            # Skip these
            if any(i in name for i in ('BaseSystem', 'Diags')):
                continue

            # RestoreRequestRules are required for devices that use IMG4
            if self.device.supports_img4 == True:
                if 'RestoreRequestRules' not in img['Info'].keys():
                    continue
                else:
                    self._handle_restore_request_rules(img)

            if 'Trusted' in img.keys():
                if 'Digest' not in img.keys():
                    img['Digest'] = bytes()

            if 'Info' in img.keys():
                img.pop('Info', None)

            request[name] = img

            self._request.update(request)

    def _add_baseband_firmware(self, baseband: Baseband) -> None:
        request = {
            '@BBTicket': True,
            'BbGoldCertId': baseband.gc_id,
            'BbNonce': baseband.nonce,
            'BbSNUM': baseband.serial,
        }
        request.update(self.identity.baseband_data)

        baseband_firmware = self.identity['Manifest']['BasebandFirmware']
        baseband_firmware.pop('Info', None)  # Remove 'Info' dict if found

        if request['BbChipID'] == 0x68:
            if request['BbGoldCertId'] in (0x26F3FACC, 0x5CF2EC4E, 0x8399785A):
                keys_to_remove = ('PSI2-PartialDigest', 'RestorePSI2-PartialDigest')
            else:
                keys_to_remove = ('PSI-PartialDigest', 'RestorePSI-PartialDigest')

            for key in keys_to_remove:
                baseband_firmware.pop(key, None)

        request['BasebandFirmware'] = baseband_firmware

        self._request.update(request)
        self._images.append(FirmwareImage.Baseband)

    @classmethod
    async def new(
        self,
        device: Device,
        *,
        firmware: Firmware = None,
        build_manifest: BuildManifest = None,
        restore_type: RestoreType,
    ) -> 'TSS':
        if device.ecid is None:
            raise TypeError('No ECID is set')

        if device.ap_nonce is None:
            raise TypeError('No ApNonce is set')

        if device.sep_nonce is None and device.is_64bit:
            raise TypeError('No SepNonce is set')

        if build_manifest is None:
            if firmware is None:
                raise TypeError('Neither a firmware nor a build manifest were provided')

            build_manifest = BuildManifest(await firmware.read('BuildManifest.plist'))

        identity = build_manifest.get_identity(device, restore_type)

        return TSS(device, identity)

    def add_image(self, image: FirmwareImage, soc: _SoC) -> None:
        if image in self._images:
            raise ValueError(f"Image already added to TSS request: '{image.name}'")

        if not isinstance(soc, _SoC):
            raise TypeError(f"Invalid SoC provided: '{soc}'")

        if image == FirmwareImage.Baseband:
            if not isinstance(soc, Baseband):
                raise TypeError('Non-Baseband SoC provided')

            if not self.identity.supports_cellular:
                raise ValueError('Device does not have cellular support')

            self._add_baseband_firmware(soc)

        elif image == FirmwareImage.SecureElement:
            pass
        elif image == FirmwareImage.Savage:
            pass
        elif image == FirmwareImage.Yonkers:
            pass
        elif image == FirmwareImage.Vinyl:
            pass
        elif image == FirmwareImage.Rose:
            pass
        elif image == FirmwareImage.Veridian:
            pass
        else:
            raise TypeError(f"Invalid firmware image provided: '{image}'")

    async def send(self) -> TSSResponse:
        async with ClientSession() as session, session.post(
            TSS_API,
            params=TSS_PARAMS,
            headers=TSS_HEADERS,
            data=plistlib.dumps(self._request),
        ) as resp:
            return TSSResponse(await resp.text())
