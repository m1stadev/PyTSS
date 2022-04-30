import plistlib
from enum import Enum

from .device import Device


class RestoreType(str, Enum):
    ERASE = 'Erase'
    UPDATE = 'Update'


class BuildIdentity:
    def __init__(self, identity: dict) -> None:
        self._data = identity

    @property
    def board_id(self) -> int:
        board_id = self._data.get('ApBoardID')
        if board_id is None:
            raise KeyError('Board ID not found in build identity')

        return int(board_id, 16)

    @property
    def chip_id(self) -> int:
        chip_id = self._data.get('ApChipID')
        if chip_id is None:
            raise KeyError('Chip ID not found in build identity')

        return int(chip_id, 16)

    @property
    def pearlcertrootpub(self) -> bytes:
        return self._data.get('PearlCertificationRootPub')

    @property
    def restore_type(self) -> RestoreType:
        info = self._data.get('Info')
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
        security_domain = self._data.get('ApSecurityDomain')
        if security_domain is None:
            raise KeyError('Security domain not found in build identity')

        return int(security_domain, 16)

    @property
    def unique_buildid(self) -> bytes:
        unique_buildid = self._data.get('UniqueBuildID')
        if unique_buildid is None:
            raise KeyError('Unique BuildID not found in build identity')

        return unique_buildid

    def get_component(self, component: str) -> str:
        if component not in self._data['Manifest'].keys():
            raise KeyError(f'Component {component} not found')

        return self._data['Manifest'][component]


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
