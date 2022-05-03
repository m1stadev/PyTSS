from collections import namedtuple

from .device import Device

BasebandData = namedtuple('BasebandData', ['identifier', 'bbgcid', 'bbslen'])

CELLULAR_DEVICES = (
    # iPhone
    BasebandData(identifier='iPhone3,1', bbgcid=257, bbslen=12),
    BasebandData(identifier='iPhone3,2', bbgcid=257, bbslen=12),
    BasebandData(identifier='iPhone3,3', bbgcid=2, bbslen=4),
    BasebandData(identifier='iPhone4,1', bbgcid=2, bbslen=4),
    BasebandData(identifier='iPhone5,1', bbgcid=3255536192, bbslen=4),
    BasebandData(identifier='iPhone5,2', bbgcid=3255536192, bbslen=4),
    BasebandData(identifier='iPhone5,3', bbgcid=3554301762, bbslen=4),
    BasebandData(identifier='iPhone5,4', bbgcid=3554301762, bbslen=4),
    BasebandData(identifier='iPhone6,1', bbgcid=3554301762, bbslen=4),
    BasebandData(identifier='iPhone6,2', bbgcid=3554301762, bbslen=4),
    BasebandData(identifier='iPhone7,1', bbgcid=3840149528, bbslen=4),
    BasebandData(identifier='iPhone7,2', bbgcid=3840149528, bbslen=4),
    BasebandData(identifier='iPhone8,1', bbgcid=3840149528, bbslen=4),
    BasebandData(identifier='iPhone8,2', bbgcid=3840149528, bbslen=4),
    BasebandData(identifier='iPhone8,4', bbgcid=3840149528, bbslen=4),
    BasebandData(identifier='iPhone9,1', bbgcid=2315222105, bbslen=4),
    BasebandData(identifier='iPhone9,2', bbgcid=2315222105, bbslen=4),
    BasebandData(identifier='iPhone9,3', bbgcid=1421084145, bbslen=12),
    BasebandData(identifier='iPhone9,4', bbgcid=1421084145, bbslen=12),
    BasebandData(identifier='iPhone10,1', bbgcid=2315222105, bbslen=4),
    BasebandData(identifier='iPhone10,2', bbgcid=2315222105, bbslen=4),
    BasebandData(identifier='iPhone10,3', bbgcid=2315222105, bbslen=4),
    BasebandData(identifier='iPhone10,4', bbgcid=524245983, bbslen=12),
    BasebandData(identifier='iPhone10,5', bbgcid=524245983, bbslen=12),
    BasebandData(identifier='iPhone10,6', bbgcid=524245983, bbslen=12),
    BasebandData(identifier='iPhone11,2', bbgcid=165673526, bbslen=12),
    BasebandData(identifier='iPhone11,4', bbgcid=165673526, bbslen=12),
    BasebandData(identifier='iPhone11,6', bbgcid=165673526, bbslen=12),
    BasebandData(identifier='iPhone11,8', bbgcid=165673526, bbslen=12),
    BasebandData(identifier='iPhone12,1', bbgcid=524245983, bbslen=12),
    BasebandData(identifier='iPhone12,3', bbgcid=524245983, bbslen=12),
    BasebandData(identifier='iPhone12,5', bbgcid=524245983, bbslen=12),
    BasebandData(identifier='iPhone12,8', bbgcid=524245983, bbslen=12),
    BasebandData(identifier='iPhone13,1', bbgcid=3095201109, bbslen=4),
    BasebandData(identifier='iPhone13,2', bbgcid=3095201109, bbslen=4),
    BasebandData(identifier='iPhone13,3', bbgcid=3095201109, bbslen=4),
    BasebandData(identifier='iPhone13,4', bbgcid=3095201109, bbslen=4),
    BasebandData(identifier='iPhone14,2', bbgcid=495958265, bbslen=4),
    BasebandData(identifier='iPhone14,3', bbgcid=495958265, bbslen=4),
    BasebandData(identifier='iPhone14,4', bbgcid=495958265, bbslen=4),
    BasebandData(identifier='iPhone14,5', bbgcid=495958265, bbslen=4),
    BasebandData(identifier='iPhone14,6', bbgcid=2241363181, bbslen=4),
    # iPad
    BasebandData(identifier='iPad2,2', bbgcid=257, bbslen=12),
    BasebandData(identifier='iPad2,3', bbgcid=257, bbslen=12),
    BasebandData(identifier='iPad2,6', bbgcid=3255536192, bbslen=4),
    BasebandData(identifier='iPad2,7', bbgcid=3255536192, bbslen=4),
    BasebandData(identifier='iPad3,2', bbgcid=4, bbslen=4),
    BasebandData(identifier='iPad3,3', bbgcid=4, bbslen=4),
    BasebandData(identifier='iPad3,5', bbgcid=3255536192, bbslen=4),
    BasebandData(identifier='iPad3,6', bbgcid=3255536192, bbslen=4),
    BasebandData(identifier='iPad4,2', bbgcid=3554301762, bbslen=4),
    BasebandData(identifier='iPad4,3', bbgcid=3554301762, bbslen=4),
    BasebandData(identifier='iPad4,5', bbgcid=3554301762, bbslen=4),
    BasebandData(identifier='iPad4,6', bbgcid=3554301762, bbslen=4),
    BasebandData(identifier='iPad4,8', bbgcid=3554301762, bbslen=4),
    BasebandData(identifier='iPad4,9', bbgcid=3554301762, bbslen=4),
    BasebandData(identifier='iPad5,2', bbgcid=3840149528, bbslen=4),
    BasebandData(identifier='iPad5,4', bbgcid=3840149528, bbslen=4),
    BasebandData(identifier='iPad6,12', bbgcid=3840149528, bbslen=4),
    BasebandData(identifier='iPad6,4', bbgcid=3840149528, bbslen=4),
    BasebandData(identifier='iPad6,8', bbgcid=3840149528, bbslen=4),
    BasebandData(identifier='iPad7,12', bbgcid=165673526, bbslen=12),
    BasebandData(identifier='iPad7,2', bbgcid=2315222105, bbslen=4),
    BasebandData(identifier='iPad7,4', bbgcid=2315222105, bbslen=4),
    BasebandData(identifier='iPad7,6', bbgcid=3840149528, bbslen=4),
    BasebandData(identifier='iPad8,10', bbgcid=524245983, bbslen=12),
    BasebandData(identifier='iPad8,12', bbgcid=524245983, bbslen=12),
    BasebandData(identifier='iPad8,3', bbgcid=165673526, bbslen=12),
    BasebandData(identifier='iPad8,4', bbgcid=165673526, bbslen=12),
    BasebandData(identifier='iPad8,7', bbgcid=165673526, bbslen=12),
    BasebandData(identifier='iPad8,8', bbgcid=165673526, bbslen=12),
    BasebandData(identifier='iPad11,2', bbgcid=165673526, bbslen=12),
    BasebandData(identifier='iPad11,4', bbgcid=165673526, bbslen=12),
    BasebandData(identifier='iPad11,7', bbgcid=165673526, bbslen=12),
    BasebandData(identifier='iPad12,2', bbgcid=165673526, bbslen=12),
    BasebandData(identifier='iPad13,10', bbgcid=3095201109, bbslen=4),
    BasebandData(identifier='iPad13,11', bbgcid=3095201109, bbslen=4),
    BasebandData(identifier='iPad13,17', bbgcid=495958265, bbslen=4),
    BasebandData(identifier='iPad13,2', bbgcid=524245983, bbslen=12),
    BasebandData(identifier='iPad13,6', bbgcid=3095201109, bbslen=4),
    BasebandData(identifier='iPad13,7', bbgcid=3095201109, bbslen=4),
    BasebandData(identifier='iPad14,2', bbgcid=495958265, bbslen=4),
    # Apple Watch
    BasebandData(identifier='Watch3,1', bbgcid=3840149528, bbslen=4),
    BasebandData(identifier='Watch3,2', bbgcid=3840149528, bbslen=4),
    BasebandData(identifier='Watch4,3', bbgcid=744114402, bbslen=12),
    BasebandData(identifier='Watch4,4', bbgcid=744114402, bbslen=12),
    BasebandData(identifier='Watch4,4', bbgcid=744114402, bbslen=12),
    BasebandData(identifier='Watch4,4', bbgcid=744114402, bbslen=12),
    BasebandData(identifier='Watch5,3', bbgcid=744114402, bbslen=12),
    BasebandData(identifier='Watch5,4', bbgcid=744114402, bbslen=12),
    BasebandData(identifier='Watch5,4', bbgcid=744114402, bbslen=12),
    BasebandData(identifier='Watch5,4', bbgcid=744114402, bbslen=12),
    BasebandData(identifier='Watch5,4', bbgcid=744114402, bbslen=12),
    BasebandData(identifier='Watch5,4', bbgcid=744114402, bbslen=12),
)


def get_baseband_data(device: Device) -> BasebandData:
    baseband_data = next(
        (
            b
            for b in CELLULAR_DEVICES
            if b.identifier.casefold() == device.identifier.casefold()
        ),
        None,
    )

    if baseband_data is None:
        raise ValueError(
            f"No baseband data was found for device: '{device.identifier}'"
        )

    return baseband_data
