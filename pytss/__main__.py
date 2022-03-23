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


def main() -> None:
    asyncio.run(_main())


if __name__ == '__main__':
    main()
