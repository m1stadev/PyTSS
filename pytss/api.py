import aiohttp

from .device import Device
from .errors import APIError


async def fetch_device(identifier: str, boardconfig: str = None) -> Device:
    async with aiohttp.ClientSession() as session, session.get(
        'https://api.ipsw.me/v4/devices'
    ) as resp:
        if resp.status != 200:
            raise APIError(
                'Failed to request device information from IPSW.me.', resp.status
            )

        data = await resp.json()

    device = next(
        (d for d in data if d['identifier'].casefold() == identifier.casefold()), None
    )
    if device is None:
        raise ValueError(f"Invalid device identifier provided: '{identifier}'")

    valid_boards = [
        board
        for board in device['boards']
        if board['boardconfig']
        .lower()
        .endswith('ap')  # Exclude development boards that may pop up
    ]

    if len(valid_boards) == 1:
        board = valid_boards[0]
    else:
        if boardconfig is None:
            raise ValueError(
                'Board config is required with devices that have multiple boards.'
            )

        board = next(
            (
                b
                for b in valid_boards
                if b['boardconfig'].casefold() == boardconfig.casefold()
            ),
            None,
        )

        if board is None:
            raise ValueError(f"Invalid board config provided: '{boardconfig}'")

    return Device(
        identifier=device['identifier'], chip_id=board['cpid'], board_id=board['bdid']
    )
