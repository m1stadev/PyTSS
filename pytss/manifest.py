import plistlib

from pytss.errors import DeviceError


class BuildIdentity:
    def __init__(self, identity: dict) -> None:
        self._identity = identity

    @property
    def board(self) -> str:
        return self._identity['Info']['DeviceClass']

    @property
    def restore_behavior(self) -> str:
        return self._identity['Info']['RestoreBehavior']

    def get_component(self, component: str) -> str:
        if component not in self._identity['Manifest'].keys():
            raise DeviceError(f'Component {component} not found')

        return self._identity['Manifest'][component]


class BuildManifest:
    def __init__(self, manifest: bytes) -> None:
        self._manifest = manifest
        self.manifest = plistlib.loads(manifest)
        self.identities = [
            BuildIdentity(identity) for identity in self.manifest['BuildIdentities']
        ]

    def get_identity(self, board: str, erase: bool) -> BuildIdentity:
        try:
            return next(
                identity
                for identity in self.identities
                if identity['Info']['DeviceClass'].casefold() == board.casefold()
                and identity['Info']['RestoreBehavior']
                == ('Erase' if erase else 'Update')
            )

        except StopIteration:
            raise DeviceError('Build identity not found')
