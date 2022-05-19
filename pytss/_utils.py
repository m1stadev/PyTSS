from collections import UserDict
from typing import Any, NoReturn


class FrozenUserDict(UserDict):
    def __setitem__(self, _: Any, __: Any) -> NoReturn:
        raise TypeError(f'{self.__class__.__name__} is read-only')

    __delitem__ = __setitem__
