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

    print('Verifying provided information...')
    device = await pytss.Device().init(args.device, args.ecid)

    if args.version or args.buildid:
        print('Fetching firmware information...')
        firmware = await pytss.FirmwareAPI().fetch_firmware(
            device, args.buildid, args.version
        )
        manifest = await firmware.read('BuildManifest.plist')
    else:
        print('Using manually specified build manifest...')
        manifest = await args.manifest.read()

    manifest = pytss.BuildManifest(manifest)

    print('Getting correct BuildIdentity')
    identity = manifest.get_identity(device.board, args.erase)


def main() -> None:
    asyncio.run(_main())


if __name__ == '__main__':
    main()
