class TSSError(Exception):
    pass


class DeviceError(TSSError):
    pass


class APIError(TSSError):
    def __init__(self, message: str, status: int) -> None:
        super().__init__(f'{message} Please try again later.\nError code: {status}.')
