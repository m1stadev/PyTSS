from collections import UserDict
from pytss.errors import DeviceError

import plistlib


class BuildIdentity(UserDict):
    @property
    def board(self) -> str:
        return self['Info']['DeviceClass']

    @property
    def restore_behavior(self) -> str:
        return self['Info']['RestoreBehavior']

    def get_component(self, component: str) -> str:
        if component not in self['Manifest'].keys():
            raise DeviceError(f'Component {component} not found')

        return self['Manifest'][component]


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
