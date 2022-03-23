from .device import Device
from .manifest import BuildIdentity

TSS_CLIENT_VERSION = 'libauthinstall-776.140.3'


class TSSManifest:
    def __init__(self):
        self.request = {
            '@HostPlatformInfo': 'mac',
            '@VersionInfo': TSS_CLIENT_VERSION,
            '@ApImg4Ticket': True,
            'ApProductionMode': True,
            'ApSecurityMode': True,
            'ApSupportsImg4': True,
        }

    def add_tags(self, device: Device, identity: BuildIdentity) -> None:
        if device.apnonce is not None:
            self.request['ApNonce'] = device.apnonce

        if device.ecid is not None:
            self.request['ApECID'] = device.ecid

        if device.sepnonce is not None:
            self.request['ApSepNonce'] = device.sepnonce

        for key in (
            'Ap,OSLongVersion',
            'ApBoardID',
            'ApChipID',
            'ApSecurityDomain',
            'BMU,BoardID',
            'BMU,ChipID',
            'Baobab,BoardID',
            'Baobab,ChipID',
            'Baobab,ManifestEpoch',
            'Baobab,SecurityDomain',
            'BbActivationManifestKeyHash',
            'BbCalibrationManifestKeyHash',
            'BbChipID',
            'BbFDRSecurityKeyHash',
            'BbFactoryActivationManifestKeyHash',
            'BbProvisioningManifestKeyHash',
            'BbSkeyId',
            'eUICC,ChipID',
            'Manifest',
            'PearlCertificationRootPub',
            'Rap,BoardID',
            'Rap,ChipID',
            'Rap,SecurityDomain',
            'SE,ChipID',
            'Savage,ChipID',
            'Savage,PatchEpoch',
            'UniqueBuildID',
            'Yonkers,BoardID',
            'Yonkers,ChipID',
            'Yonkers,PatchEpoch',
        ):
            if key in identity.keys():
                if key.startswith('0x') and isinstance(identity[key], str):
                    identity[key] = int(identity[key], 16)

                self.request[key] = identity[key]

        for key, val in identity['Manifest']:  # Iterate through each component
            if key in ('BasebandFirmware', 'SE,UpdatePayload', 'BaseSystem', 'Diags'):
                continue

            if not any(k in val.keys() for k in ('Info', 'RestoreRequestRules')):
                continue

            if 'RestoreRequestRules' not in val.keys():
                continue

            if val['Trusted'] == False:
                continue

            if not any(
                val[k] == True
                for k in (
                    'IsFirmwarePayload',
                    'IsSecondaryFirmwarePayload',
                    'IsFUDFirmware',
                )
            ):
                continue
