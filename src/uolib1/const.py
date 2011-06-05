# -*- coding: utf-8 -*-

TD_BACKGROUND =     0x00000001
TD_WEAPON =         0x00000002
TD_TRANSPARENT =    0x00000004
TD_TRANSLUCENT =    0x00000008
TD_WALL =           0x00000010
TD_DAMAGING =       0x00000020
TD_IMPASSABLE =     0x00000040
TD_WET =            0x00000080
TD_UNKNOWN =        0x00000100
TD_SURFACE =        0x00000200
TD_BRIDGE =         0x00000400
TD_STACKABLE =      0x00000800
TD_WINDOW =         0x00001000
TD_NOSHOOT =        0x00002000
TD_PREFIX_A =       0x00004000
TD_PREFIX_AN =      0x00008000
TD_INTERNAL =       0x00010000
TD_FOLIAGE =        0x00020000
TD_PARTIAL_HUE =    0x00040000
TD_UNKNOWN1 =       0x00080000
TD_MAP =            0x00100000
TD_CONTAINER =      0x00200000
TD_WEARABLE =       0x00400000
TD_LIGHTSOURCE =    0x00800000
TD_ANIMATED =       0x01000000
TD_NODIAGONAL =     0x02000000
TD_UNKNOWN2 =       0x04000000
TD_ARMOR =          0x08000000
TD_ROOF =           0x10000000
TD_DOOR =           0x20000000
TD_STAIR_BACK =     0x40000000
TD_STAIR_RIGHT =    0x80000000

tiledata_flags = { 
        TD_BACKGROUND: 'Background',
        TD_WEAPON: 'Weapon',
        TD_TRANSPARENT: 'Transparent',
        TD_TRANSLUCENT: 'Translucent',
        TD_WALL: 'Wall',
        TD_DAMAGING: 'Damaging',
        TD_IMPASSABLE: 'Impassable',
        TD_WET: 'Wet',
        TD_UNKNOWN: 'Unknown',
        TD_SURFACE: 'Surface',
        TD_BRIDGE: 'Bridge',
        TD_STACKABLE: 'Generic/Stackable',
        TD_WINDOW: 'Window',
        TD_NOSHOOT: 'No Shoot',
        TD_PREFIX_A: 'Prefix A',
        TD_PREFIX_AN: 'Prefix An',
        TD_INTERNAL: 'Internal (things like hair, beards, etc)',
        TD_FOLIAGE: 'Foliage',
        TD_PARTIAL_HUE: 'Partial Hue',
        TD_UNKNOWN1: 'Unknown 1',
        TD_MAP: 'Map',
        TD_CONTAINER: 'Container',
        TD_WEARABLE: 'Wearable',
        TD_LIGHTSOURCE: 'LightSource',
        TD_ANIMATED: 'Animated',
        TD_NODIAGONAL: 'No Diagonal',
        TD_UNKNOWN2: 'Unknown 2',
        TD_ARMOR: 'Armor',
        TD_ROOF: 'Roof',
        TD_DOOR: 'Door',
        TD_STAIR_BACK: 'StairBack',
        TD_STAIR_RIGHT: 'StairRight',
}