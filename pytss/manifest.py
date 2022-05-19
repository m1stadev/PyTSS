import plistlib
from enum import Enum

from ._utils import FrozenUserDict
from .device import Device


class RestoreType(str, Enum):
    ERASE = 'Erase'
    UPDATE = 'Update'


class BuildIdentity(FrozenUserDict):
    def __init__(self, identity: dict) -> None:
        self.data = identity

    @property
    def baseband_data(self) -> dict:
        if not self.supports_cellular:
            raise TypeError('Device does not have cellular support.')

        baseband_data = {}

        if 'BbChipID' in self.data.keys():
            baseband_data['BbChipID'] = int(self.data['BbChipID'], 16)
        else:
            raise KeyError('Baseband Chip ID not found in build identity')

        for key in (
            'BbProvisioningManifestKeyHash',
            'BbActivationManifestKeyHash',
            'BbCalibrationManifestKeyHash',
            'BbFactoryActivationManifestKeyHash',
            'BbFDRSecurityKeyHash',
            'BbSkeyId',
        ):
            if key in self.data.keys():
                baseband_data[key] = self.data[key]

        return baseband_data

    @property
    def board_id(self) -> int:
        board_id = self.data.get('ApBoardID')
        if board_id is None:
            raise KeyError('Board ID not found in build identity')

        return int(board_id, 16)

    @property
    def chip_id(self) -> int:
        chip_id = self.data.get('ApChipID')
        if chip_id is None:
            raise KeyError('Chip ID not found in build identity')

        return int(chip_id, 16)

    @property
    def supports_cellular(self) -> bool:
        manifest = self.data.get('Manifest')
        if manifest is None:
            raise KeyError('Manifest dict not found in build identity')

        return 'BasebandFirmware' in manifest.keys()

    @property
    def restore_type(self) -> RestoreType:
        info = self.data.get('Info')
        if info is None:
            raise KeyError('Info dict not found in build identity')

        restore_type = info.get('RestoreBehavior')
        if restore_type is None:
            raise KeyError('Restore type not found in build identity')

        if restore_type == 'Erase':
            return RestoreType.ERASE
        elif restore_type == 'Update':
            return RestoreType.UPDATE
        else:
            raise ValueError(
                f"Unknown restore type found in build identity: '{restore_type}'"
            )

    @property
    def security_domain(self) -> int:
        security_domain = self.data.get('ApSecurityDomain')
        if security_domain is None:
            raise KeyError('Security domain not found in build identity')

        return int(security_domain, 16)

    def get_component(self, component: str) -> dict:
        manifest = self.data.get('Manifest')
        if manifest is None:
            raise KeyError('Manifest dict not found in build identity')

        if component not in manifest.keys():
            raise KeyError(f"Component not found: '{component}'")

        return manifest.get(component)


class BuildManifest:
    def __init__(self, manifest: bytes) -> None:
        self._data = plistlib.loads(manifest)
        self.identities = [
            BuildIdentity(identity) for identity in self._data['BuildIdentities']
        ]

    def get_identity(self, device: Device, restore_type: RestoreType) -> BuildIdentity:
        identity = next(
            (
                identity
                for identity in self.identities
                if identity.board_id == device.board_id
                and identity.chip_id == device.chip_id
                and identity.restore_type == restore_type
            ),
            None,
        )

        if identity is None:
            raise ValueError(
                f"{restore_type} build identity not found for device: '{device.identifier}'"
            )

        return identity
