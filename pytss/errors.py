class PyTSSError(Exception):
    pass


class DeviceError(PyTSSError):
    pass


class APIError(PyTSSError):
    def __init__(self, message: str, status: int) -> None:
        super().__init__(f'{message} Please try again later.\nError code: {status}.')
