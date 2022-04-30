import argparse
import asyncio

import pytss


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
    tss = await pytss.TSS.create_request(
        device,
        firmware,
        restore_type=pytss.RestoreType.ERASE
        if args.erase
        else pytss.RestoreType.UPDATE,
    )

    print('Sending TSS request...')
    response = await tss.send()

    print(f'ApTicket length: {len(response.data)}')


def main() -> None:
    asyncio.run(_main())


if __name__ == '__main__':
    main()
