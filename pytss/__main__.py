import argparse
import asyncio
from random import getrandbits

import pytss

from .soc import BasebandSoC


async def _main() -> None:
    parser = argparse.ArgumentParser(
        usage='pytss [options]',
    )
    parser.add_argument(
        '-d',
        '--device',
        help='Device identifier (e.g. iPod7,1)',
        required=True,
    )
    parser.add_argument(
        '-e',
        '--ecid',
        help='Device ECID (e.g. abcdef01234567)',
        required=True,
    )
    parser.add_argument(
        '-u',
        '--update',
        help='Save update blobs (disabled by default)',
        action='store_false',
        dest='erase',
    )

    build = parser.add_mutually_exclusive_group(required=True)
    build.add_argument('-v', '--version', help='Firmware version')
    build.add_argument('-b', '--buildid', help='Firmware buildid')
    build.add_argument(
        '-m',
        '--buildmanifest',
        help='Firmware build manifest',
        type=argparse.FileType('rb'),
        dest='manifest',
    )

    args = parser.parse_args()

    print(f'pytss {pytss.__version__}')

    print('Fetching device information...')
    device = await pytss.fetch_device(args.device)
    device.ecid = args.ecid

    print('Fetching firmware information...')
    firmware = await device.fetch_firmware(version=args.version, buildid=args.buildid)

    print('Creating TSS request...')
    tss = await pytss.TSS.new(
        device,
        firmware,
        restore_type=pytss.RestoreType.ERASE
        if args.erase
        else pytss.RestoreType.UPDATE,
    )

    baseband = BasebandSoC(
        gold_cert_id=0x1D8FB8F9,  # iPhone14,3
        nonce=bytes(getrandbits(8) for _ in range(20)),
        serial=bytes(getrandbits(8) for _ in range(4)),
    )

    tss.add_image(pytss.FirmwareImage.Baseband, baseband)

    print('Sending TSS request...')
    response = await tss.send()

    print(response.data)


def main() -> None:
    asyncio.run(_main())


if __name__ == '__main__':
    main()
