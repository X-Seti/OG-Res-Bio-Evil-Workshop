#!/usr/bin/env python3
#this belongs in apps/core/re1_formats.py - Version: 1
# X-Seti - May22 2026 - ResBio-Evil-Workshop - RE1 File Format Parsers
"""
RE1 File Format Parsers - Binary parsers for RDT, TIM, EMD, SCA formats.
All formats little-endian. Source: reevengi-tools wiki + community research.
"""

import struct
import os
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

##Methods list -
# parse_rdt
# _detect_rdt_version
# _parse_rdt_re1
# _parse_rdt_re2
# _parse_rdt_collision_re2
# _parse_collision_at
# parse_tim
# parse_emd
# parse_sca_header

##class RDTHeader:
##class RDTCamera:
##class RDTItem:
##class RDTEnemy:
##class RDTAot:
##class RDTCameraSwitch:
##class RDTCollisionBoundary:
##class RDTFile:
##class TIMHeader:
##class TIMFile:
##class EMDVertex:
##class EMDTriangle:
##class EMDMesh:
##class EMDFile:
##class SCAHeader:
##class SCAFile:
##class RE1FormatError:

# --- Exceptions ---

class RE1FormatError(Exception): #vers 1
    pass

# --- RDT Structures ---

@dataclass
class RDTCamera: #vers 2
    masks_offset: int     = 0
    tim_masks_offset: int = 0
    from_x: int           = 0
    from_y: int           = 0
    from_z: int           = 0
    to_x: int             = 0
    to_y: int             = 0
    to_z: int             = 0
    camera_index: int     = 0
    view_r: int           = 0   # screen projection height (ViewR from re1.h)
    unknown: List[int] = field(default_factory=list)

    @property
    def from_pos(self) -> Tuple[int, int, int]:
        return (self.from_x, self.from_y, self.from_z)

    @property
    def to_pos(self) -> Tuple[int, int, int]:
        return (self.to_x, self.to_y, self.to_z)


@dataclass
class RDTItem: #vers 1
    item_type: int
    x: int
    y: int
    z: int
    rotation: int
    flags: int
    amount: int = 0

    @property
    def pos(self) -> Tuple[int, int, int]:
        return (self.x, self.y, self.z)


@dataclass
class RDTEnemy: #vers 1
    """Enemy placement entry from RDT enemy table."""
    enemy_type: int    # enemy model/AI type
    x: int
    y: int
    z: int
    rotation: int      # direction (0-0xFFFF)
    id: int            # unique id in room
    num: int           # spawn group / condition number
    floor: int
    sound_bank: int
    effect_bank: int
    flags: int = 0

    @property
    def pos(self) -> tuple:
        return (self.x, self.y, self.z)


@dataclass
class RDTAot: #vers 1
    """Area Of Trigger - rectangles on the floor that trigger actions.
    Types: 0=none, 1=door, 2=item, 3=event, 4=player, 5=auto, 6=message
    """
    aot_type: int      # trigger type
    x: int             # centre x
    z: int             # centre z
    w: int             # width
    d: int             # depth
    floor: int
    super_type: int    # broad category
    data: bytes        # 8 bytes of type-specific data

    @property
    def x1(self) -> int: return self.x - self.w // 2
    @property
    def z1(self) -> int: return self.z - self.d // 2
    @property
    def x2(self) -> int: return self.x + self.w // 2
    @property
    def z2(self) -> int: return self.z + self.d // 2

    @property
    def is_door(self) -> bool:  return self.aot_type == 1
    @property
    def is_item(self) -> bool:  return self.aot_type == 2
    @property
    def is_event(self) -> bool: return self.aot_type == 3


@dataclass
class RDTCameraSwitch: #vers 1
    """Camera switch zone - rectangle that changes active camera."""
    from_cam: int      # camera active when entering this zone
    to_cam: int        # camera to switch to
    x1: int
    z1: int
    x2: int
    z2: int
    floor: int


@dataclass
class RDTCollisionBoundary: #vers 1
    boundary_type: int
    x1: int
    z1: int
    x2: int
    z2: int
    floor: int
    density: int
    sound_attr: int


@dataclass
class RDTHeader: #vers 2
    unknown0: int     = 0
    num_cameras: int  = 0
    num_sound_banks: int = 0
    unknown1: bytes   = b''
    offsets: List[int] = field(default_factory=list)

    OFFSET_COUNT = 19
    HEADER_SIZE  = 0x94  # RE1 camera data starts here (RE2: 0x64)


@dataclass
class RDTFile: #vers 1
    file_path: str
    raw_data: bytes
    header: Optional[RDTHeader] = None
    cameras: List[RDTCamera] = field(default_factory=list)
    items: List[RDTItem] = field(default_factory=list)
    enemies: List[RDTEnemy] = field(default_factory=list)
    aot: List[RDTAot] = field(default_factory=list)
    camera_switches: List[RDTCameraSwitch] = field(default_factory=list)
    collision: List[RDTCollisionBoundary] = field(default_factory=list)
    sca_counts: List[int] = field(default_factory=list)  # [floors, slopes, walls, doors, other]
    sca_ceiling: tuple = field(default_factory=tuple)    # (ceiling_x, ceiling_z)
    game_version: int = 0  # 1=RE1, 2=RE2, 3=RE3
    parse_errors: List[str] = field(default_factory=list)
    valid: bool = False

    @property
    def filename(self) -> str:
        return os.path.basename(self.file_path)

    @property
    def file_size(self) -> int:
        return len(self.raw_data)

    @property
    def room_id(self) -> str:
        name = os.path.basename(self.file_path).upper()
        return name.replace('.RDT', '')


# --- TIM Structures ---

@dataclass
class TIMHeader: #vers 1
    magic: int       # 0x00000010 (byte[0]=0x10, little-endian)
    flags: int
    bpp: int         # derived from flags bits 0-2
    has_clut: bool   # derived from flags bit 3

    COLOR_4BIT  = 0
    COLOR_8BIT  = 1
    COLOR_16BIT = 2
    COLOR_24BIT = 3


@dataclass
class TIMFile: #vers 1
    file_path: str
    header: Optional[TIMHeader] = None
    width: int = 0
    height: int = 0
    rgba_data: Optional[bytes] = None
    valid: bool = False
    parse_errors: List[str] = field(default_factory=list)


# --- EMD Structures ---

@dataclass
class EMDVertex: #vers 1
    x: int
    y: int
    z: int

    def to_float(self) -> Tuple[float, float, float]:
        return (self.x / 4096.0, self.y / 4096.0, self.z / 4096.0)


@dataclass
class EMDTriangle: #vers 1
    v0: int
    v1: int
    v2: int
    n0: int = 0
    n1: int = 0
    n2: int = 0


@dataclass
class EMDMesh: #vers 1
    vertices: List[EMDVertex] = field(default_factory=list)
    normals: List[EMDVertex] = field(default_factory=list)
    triangles: List[EMDTriangle] = field(default_factory=list)


@dataclass
class EMDFile: #vers 1
    file_path: str
    meshes: List[EMDMesh] = field(default_factory=list)
    valid: bool = False
    parse_errors: List[str] = field(default_factory=list)


# --- SCA Structures ---

@dataclass
class SCAHeader: #vers 1
    ceiling_x: int
    ceiling_z: int
    counts: List[int]  # 5 object type counts


@dataclass
class SCAFile: #vers 1
    header: Optional[SCAHeader] = None
    boundaries: List[RDTCollisionBoundary] = field(default_factory=list)
    valid: bool = False


# --- Item type table (RE1) ---

RE1_ITEM_NAMES: dict = {  # from RE1-Mod-SDK xml/item.xml
    0x01: "Combat Knife",  0x02: "Beretta",  0x03: "Shotgun",
    0x04: "Colt Python",  0x05: "Colt Python",  0x06: "Flamethrower",
    0x07: "Grenade Gun",  0x08: "Grenade Gun",  0x09: "Grenade Gun",
    0x0A: "Rocket Launcher",  0x0B: "Hand Gun Bullets",  0x0C: "Shotgun Shells",
    0x0D: "DumDum Bullets",  0x0E: "Magnum Bullets",  0x0F: "Fuel",
    0x10: "Grenade Rounds",  0x11: "Acid Rounds",  0x12: "Flame Rounds",
    0x13: "Empty Bottle",  0x14: "Water",  0x15: "UMB No.2",
    0x16: "UMB No.4",  0x17: "UMB No.7",  0x18: "UMB No.13",
    0x19: "Yellow-6",  0x1A: "NP-003",  0x1B: "V-Jolt",
    0x1C: "Broken Shotgun",  0x1D: "Square Crank",  0x1E: "Hexagonal Crank",
    0x1F: "Emblem",  0x20: "Gold Emblem",  0x21: "Blue Jewel",
    0x22: "Red Jewel",  0x23: "Music Score",  0x24: "Wolf Medal",
    0x25: "Eagle Medal",  0x26: "Herbicide",  0x27: "Battery",
    0x28: "MO-Disk",  0x29: "Wind Crest",  0x2A: "Flare",
    0x2B: "Slides",  0x2C: "Moon Crest",  0x2D: "Star Crest",
    0x2E: "Sun Crest",  0x2F: "Ink Ribbon",  0x30: "Lighter",
    0x31: "Lockpick",  0x33: "Sword Key",  0x34: "Armor Key",
    0x35: "Shield Key",  0x36: "Helmet Key",  0x37: "Master Key",
    0x38: "Closet Key",  0x39: "Key for Room 002",  0x3A: "Key for Room 003",
    0x3B: "Control Room Key",  0x3C: "Power Room Key",  0x3D: "Desk Key",
    0x3E: "Blank Book",  0x3F: "Doom Book 2",  0x40: "Doom Book 1",
    0x41: "First Aid Spray",  0x42: "Serum",  0x43: "Red Herb",
    0x44: "Green Herb",  0x45: "Blue Herb",  0x46: "Mixed Herbs",
    0x47: "Mixed Herbs",  0x48: "Mixed Herbs",  0x49: "Mixed Herbs",
    0x4A: "Mixed Herbs",  0x4B: "Mixed Herbs",  0x4D: "Comm. Radio",
    0x5F: "Researcher's Will",  0x60: "Researcher's Will",  0x61: "Keeper's Diary",
    0x62: "Orders",  0x63: "Pass Number",  0x64: "Plant-42 Report",
    0x65: "Fax",  0x66: "Scrapbook",  0x67: "Security System",
    0x68: "Researcher's Letter",  0x69: "V-Jolt Report",  0x6A: "Barry's Picture",
    0x6B: "Pass Code 01",  0x6C: "Pass Code 02",  0x6D: "Pass Code 03",
    0x6E: "Botany Book",  0x6F: "Ingram",  0x70: "Minimi",
    0x71: "Crank",  0x72: "Crank",  0x73: "Chemical",
    0x74: "Mansion Key",  0x75: "Mansion Key",  0x76: "Mansion Key",
    0x77: "Mansion Key",  0x78: "Laboratory Key",  0x79: "Special Key",
    0x7A: "Guardhouse Key",  0x7B: "Guardhouse Key",  0x7C: "Laboratory Key",
    0x7D: "Small Key",  0x7E: "Red Book",  0x7F: "Doom Book 2",
    0x80: "Doom Book 1",
}

RE1_ITEM_ICONS: dict = {  # item_type -> icon_id in ITEM_ALL.PIX
    0x00: "0",  0x01: "1",  0x02: "2",
    0x03: "3",  0x04: "4",  0x05: "4",
    0x06: "5",  0x07: "6",  0x08: "6",
    0x09: "6",  0x0A: "7",  0x0B: "8",
    0x0C: "9",  0x0D: "10",  0x0E: "11",
    0x0F: "12",  0x10: "13",  0x11: "14",
    0x12: "15",  0x13: "16",  0x14: "17",
    0x15: "18",  0x16: "19",  0x17: "20",
    0x18: "21",  0x19: "22",  0x1A: "23",
    0x1B: "24",  0x1C: "25",  0x1D: "26",
    0x1E: "27",  0x1F: "28",  0x20: "29",
    0x21: "30",  0x22: "31",  0x23: "32",
    0x24: "33",  0x25: "34",  0x26: "35",
    0x27: "36",  0x28: "37",  0x29: "38",
    0x2A: "39",  0x2B: "40",  0x2C: "41",
    0x2D: "42",  0x2E: "43",  0x2F: "44",
    0x30: "45",  0x31: "46",  0x32: "47",
    0x33: "48",  0x34: "49",  0x35: "50",
    0x36: "51",  0x37: "52",  0x38: "53",
    0x39: "54",  0x3A: "55",  0x3B: "56",
    0x3C: "57",  0x3D: "58",  0x3E: "59",
    0x3F: "60",  0x40: "61",  0x41: "62",
    0x42: "63",  0x43: "64",  0x44: "65",
    0x45: "66",  0x46: "67",  0x47: "68",
    0x48: "69",  0x49: "70",  0x4A: "71",
    0x4B: "72",  0x4C: "73",  0x4D: "74",
}

RE1_ITEM_MAX: dict = {  # max ammo/count per item type
    0x02: "15",  0x03: "7",  0x04: "6",
    0x05: "6",  0x06: "240",  0x07: "6",
    0x08: "6",  0x09: "6",  0x0A: "4",
    0x0B: "15",  0x0C: "7",  0x0D: "6",
    0x0E: "6",  0x0F: "240",  0x10: "6",
    0x11: "6",  0x12: "6",  0x13: "1",
    0x14: "1",  0x15: "1",  0x16: "1",
    0x17: "1",  0x18: "1",  0x19: "1",
    0x1A: "1",  0x1B: "1",  0x1C: "1",
    0x1F: "1",  0x20: "1",  0x21: "1",
    0x22: "1",  0x23: "1",  0x24: "1",
    0x25: "1",  0x26: "1",  0x27: "1",
    0x28: "1",  0x29: "1",  0x2A: "1",
    0x2B: "1",  0x2C: "1",  0x2D: "1",
    0x2E: "1",  0x2F: "3",  0x32: "2",
    0x3D: "1",  0x3E: "1",  0x3F: "1",
    0x40: "1",  0x41: "1",  0x42: "1",
    0x43: "1",  0x44: "1",  0x45: "1",
    0x46: "1",  0x47: "1",  0x48: "1",
    0x49: "1",  0x4A: "1",  0x4B: "1",
}

RE2_ITEM_NAMES: dict = {  # from RE2-Mod-tools mod-sdk/xml/item.xml
    0x00: "Nothing",  0x02: "Knife",  0x03: "Hand Gun",
    0x04: "Hand Gun",  0x05: "C. Hand Gun",  0x06: "Magnum",
    0x07: "C. Magnum",  0x08: "Shotgun",  0x09: "C. Shotgun",
    0x0A: "G. Launcher",  0x0B: "G. Launcher",  0x0C: "G. Launcher",
    0x0D: "Bow Gun",  0x0E: "Colt S.A.A.",  0x0F: "Spark Shot",
    0x10: "S. Machine Gun",  0x11: "Flamethrower",  0x12: "R. Launcher",
    0x13: "Gatling Gun",  0x14: "Hand Gun",  0x15: "H. Gun Bullets",
    0x16: "Shotgun Shells",  0x17: "M. Bullets",  0x18: "Fuel",
    0x19: "G. Rounds",  0x1A: "Flame Rounds",  0x1B: "Acid Rounds",
    0x1C: "M.G. Bullets",  0x1D: "S. Shot Bullets",  0x1E: "Bow Gun Bolts",
    0x1F: "Ink Ribbon",  0x20: "Small Key",  0x21: "H. Gun Parts",
    0x22: "Magnum Parts",  0x23: "Shotgun Parts",  0x24: "F. Aid Spray",
    0x25: "Anti-virus bomb",  0x26: "Chemical AC-W24",  0x27: "Green Herb",
    0x28: "Red Herb",  0x29: "Blue Herb",  0x2A: "Mixed Herb",
    0x2B: "Mixed Herb",  0x2C: "Mixed Herb",  0x2D: "Mixed Herb",
    0x2E: "Mixed Herb",  0x2F: "Mixed Herb",  0x30: "Lighter",
    0x31: "Lockpick",  0x32: "Picture",  0x33: "Valve Handle",
    0x34: "Red Jewel",  0x35: "Red Card Key",  0x36: "Blue Card Key",
    0x37: "Serpent Stone",  0x38: "Jaguar Stone",  0x39: "Blue Stone",
    0x3A: "Blue Stone",  0x3B: "Eagle Stone",  0x3C: "Bishop Plug",
    0x3D: "Rook Plug",  0x3E: "Knight Plug",  0x3F: "King Plug",
    0x40: "W. Box Key",  0x41: "Detonator",  0x42: "Plastic Bomb",
    0x43: "Bomb & Det.",  0x44: "Crank",  0x45: "Film",
    0x46: "Film",  0x47: "Film",  0x48: "Unicorn Medal",
    0x49: "Eagle Medal",  0x4A: "Wolf Medal",  0x4B: "G. Cogwheel",
    0x4C: "Manhole Opener",  0x4D: "Main Fuse",  0x4E: "Fuse Case",
    0x4F: "Vaccine",  0x50: "Vaccine Cart.",  0x51: "Film",
    0x52: "Base Vaccine",  0x53: "G-virus",  0x54: "Special Key",
    0x55: "Joint S Plug",  0x56: "Joint N Plug",  0x57: "Cord",
    0x58: "Picture",  0x59: "Cabin Key",  0x5A: "Precinct Key",
    0x5B: "Precinct Key",  0x5C: "Precinct Key",  0x5D: "Precinct Key",
    0x5E: "C. Panel Key",  0x5F: "C. Panel Key",  0x60: "P. Room Key",
    0x61: "MO disk",  0x62: "Lab Card Key",  0x63: "Master Key",
    0x64: "Platform Key",  0x65: "no item",  0x66: "no item",
    0x67: "no item",  0x68: "no item",  0x69: "CHRIS's diary",
    0x6A: "Mail to Chris",  0x6B: "Memo to LEON",  0x6C: "Police memorandum",
    0x6D: "Operation report 1",  0x6E: "Mail to the chief",  0x6F: "Mail to the chief",
    0x70: "Secretary's diary A",  0x71: "Secretary's diary B",  0x72: "Operation report 2",
    0x73: "User registration",  0x74: "Film A",  0x75: "Film B",
    0x76: "Film C",  0x77: "Patrol report",  0x78: "Watchman's diary",
    0x79: "Chief's diary",  0x7A: "Sewer manager diary",  0x7B: "Sewer manager fax",
    0x7C: "Film D",  0x7D: "Vaccine synthesis",  0x7E: "Lab security manual",
    0x7F: "P-epsilon report",  0x80: "Rookie files",  0x81: "Rookie files",
    0x82: "no item",  0x83: "Spade Key",  0x84: "Diamond Key",
    0x85: "Desk Key",  0x86: "Heart Key",  0x87: "Club Key",
    0x88: "Virgin Heart",  0x89: "Square Crank",  0x8A: "Down Key",
    0x8B: "Up Key",  0x8C: "Locker Key",
}

RE3_ITEM_NAMES: dict = {
    0x00: "Nothing",          0x01: "Handgun",           0x02: "Shotgun",
    0x03: "Grenade Launcher", 0x04: "Rocket Launcher",   0x05: "Knife",
    0x06: "Handgun Rounds",   0x07: "Shotgun Shells",    0x08: "Grenade Rounds",
    0x09: "Flame Rounds",     0x0A: "Acid Rounds",       0x0B: "Freeze Rounds",
    0x0C: "Mine Thrower",     0x0D: "Mine Thrower Ammo", 0x0E: "M37 Parts",
    0x0F: "M37 Parts (2)",    0x10: "First Aid Spray",   0x11: "Red Herb",
    0x12: "Green Herb",       0x13: "Blue Herb",          0x14: "Mixed (G+G)",
    0x15: "Mixed (G+G+G)",    0x16: "Mixed (G+B)",       0x17: "Mixed (G+R)",
    0x18: "Mixed (G+R+B)",    0x19: "Ink Ribbon",        0x20: "Emblem Key",
    0x21: "Bronze Compass",   0x22: "Old Key",            0x23: "Rusted Key",
    0x24: "Card Key",         0x25: "Facility Key",       0x26: "Warehouse Key",
    0x27: "Oil Additive",     0x28: "Machine Oil",        0x29: "Gear",
    0x2A: "Chronos Chain",    0x2B: "Chronos Gear",       0x2C: "Sickle",
    0x2D: "Battery",          0x2E: "Detonator",          0x2F: "Powder (A)",
    0x30: "Powder (B)",       0x31: "Powder (C)",         0x32: "Powder (A+A)",
    0x33: "Powder (A+B)",     0x34: "Powder (B+B)",       0x35: "Powder (A+C)",
    0x36: "Powder (B+C)",     0x37: "Vaccine",            0x38: "Vaccine Cart.",
    0x39: "Vaccine Cart. (full)", 0x3A: "Vaccine Media",  0x3B: "System Disk",
    0x3C: "Jewel Box",        0x3D: "Red Jewel",          0x3E: "Blue Jewel",
    0x3F: "Memo",             0x40: "Hospital Map",       0x41: "Park Map",
    0x42: "Downtown Map",
}


def get_item_name(item_type: int, game: str = 're1') -> str: #vers 3
    """Return item name for type and game. game='re1'|'re2'|'re3'."""
    import sys as _sys
    _m = _sys.modules[__name__]
    if game == 're3':
        return getattr(_m, 'RE3_ITEM_NAMES', {}).get(
            item_type, f"Unknown (0x{item_type:02X})")
    if game == 're2':
        return getattr(_m, 'RE2_ITEM_NAMES', {}).get(
            item_type, f"Unknown (0x{item_type:02X})")
    return RE1_ITEM_NAMES.get(item_type, f"Unknown (0x{item_type:02X})")


# --- Parser Functions ---

def _is_prs_compressed(data: bytes) -> bool: #vers 2
    """Check if data is a PRS-compressed RE3 RDT.

    PRS-compressed RE3 RDTs are small (< 150KB uncompressed).
    RE2 PS1 RDTs are large (100KB-500KB) and have valid RE2 headers.
    
    Conditions for PRS:
    - File size < 150KB (RE3 compressed RDTs are 20-100KB)
    - header[1] (nCut) is 0 or > 20 (not a valid camera count)
    - The 23 section offsets at 0x08 don't look valid
    """
    if len(data) < 8:
        return False
    # RE2 PS1 check: nCut in [1..16] AND nBss in [0..16] = uncompressed
    n_cut = data[1]
    n_bss = data[2]
    if 1 <= n_cut <= 16 and 0 <= n_bss <= 20:
        return False
    # RE1 check: nCut in header[1] position
    if 1 <= n_cut <= 12:
        return False
    # Large files are never PRS-compressed
    if len(data) > 150_000:
        return False
    return True


def _detect_version_from_path(file_path: str, data: bytes) -> int: #vers 2
    """Detect RDT version using filename + folder structure + header.
    Most reliable method - uses actual path context.
    
    RE1 PC:  Stage1/ROOM1xxx.RDT   (folder named StageN, no DATA parent)
    RE2 PC:  DATA/ROOMxxxx.RDT     (parent folder = DATA, has .ADT files)
    RE3 PC:  DATA/STAGE/ROOMxx.RDT (STAGE subfolder inside DATA)
    RE1 PS1: PSX/STAGE1/ROOM0xx.RDT
    RE2 PS1: PSX/STAGE1/ROOM11C0.RDT (4-char with scenario digit)
    """
    import os
    path_up  = file_path.upper()
    ext      = os.path.splitext(file_path)[1].upper()
    fname    = os.path.splitext(os.path.basename(file_path))[0].upper()
    folder   = os.path.dirname(file_path)
    folder_n = os.path.basename(folder).upper()
    parent   = os.path.dirname(folder)
    parent_n = os.path.basename(parent).upper()

    # .ARD files = RE2 PS1 shared stage rooms (CD_DATA/STAGE*/Rxxx.ARD)
    # Same binary format as RE2 PS1 RDT. Always version 2.
    if ext == '.ARD':
        return 2

    # CD_DATA/STAGE* path = RE2 PS1 shared stage area (both scenarios)
    # Covers any room file in CD_DATA/STAGEn/ even if extension varies
    if parent_n == 'CD_DATA' and folder_n.startswith('STAGE'):
        return 2
    if 'CD_DATA' in path_up and folder_n.startswith('STAGE'):
        return 2

    # RE3 PC: DATA/STAGE/ subfolder (folder name starts with STAGE, parent is DATA)
    if folder_n.startswith('STAGE') and parent_n == 'DATA':
        return 3

    # RE2 PC: directly in DATA/ folder
    if folder_n == 'DATA' or parent_n == 'DATA':
        # Check siblings for ADT (RE2) or ROFS (RE3)
        check_dir = folder if folder_n == 'DATA' else parent
        try:
            sibs = os.listdir(check_dir)
            if any(s.upper().startswith('ROFS') for s in sibs):
                return 3
            if any(s.upper().endswith('.ADT') for s in sibs):
                return 2
        except OSError:
            pass
        return 2  # DATA folder = RE2 PC

    # Room filename analysis
    if fname.startswith('ROOM'):
        digits = fname[4:]
        # 3 chars = RE1 (ROOM000-ROOM3FF)
        if len(digits) == 3:
            return 1
        # 4 chars ending 0/1: could be RE2 PS1/PC (scenario) or RE1 PC (decimal)
        if len(digits) == 4 and digits[-1] in ('0','1'):
            # RE1 PC uses StageN parent folder, RE2 PS1 uses STAGE1 with PSX above
            if folder_n.startswith('STAGE') and 'PSX' not in path_up:
                # RE1 PC: Stage1/Stage2 etc - no PSX in path
                return 1
            return 2
        # 4 chars NOT ending 0/1 = RE1 PC decimal (ROOM1020 etc)
        if len(digits) == 4:
            return 1

    # Fall back to header analysis
    return _detect_rdt_version(data)


def _detect_rdt_version(data: bytes) -> int: #vers 2
    """Detect RDT game version. Returns 1=RE1, 2=RE2, 3=RE3.
    RE1: byte[1]=num_cameras (typically 1-8), 19 offsets, cameras at 0x94
    RE2: byte[2]=num_cameras, 21 offsets, cameras at 0xA8
    Heuristic: check whether byte[1] or byte[2] gives a sane camera count,
    and whether offset table at 0x20 has plausible values.
    """
    if len(data) < 0xA8 + 4:
        return 1
    # RE2 has num_sprites at byte[1], num_cameras at byte[2]
    # RE1 has num_cameras at byte[1]
    re1_cams = data[1]
    re2_cams = data[2]
    # A plausible camera count is 1-8
    re1_ok = 1 <= re1_cams <= 8
    re2_ok = 1 <= re2_cams <= 8
    if re2_ok and not re1_ok:
        # Distinguish RE2 vs RE3 by checking SYSTEM.CNF or room ID conventions
        # RE3 rooms: ROOM0XXY (second hex digit is always the stage in 0-6)
        # For now: use offset table validity
        offsets_21 = list(struct.unpack_from('<21I', data, 0x20))
        valid_21 = sum(1 for o in offsets_21 if 0 < o < len(data))
        offsets_19 = list(struct.unpack_from('<19I', data, 0x20))
        valid_19 = sum(1 for o in offsets_19 if 0 < o < len(data))
        if valid_21 > valid_19 + 2:
            return 2  # RE2 (RE3 handled by game_from_room_id at higher level)
        return 2
    offsets_21 = list(struct.unpack_from('<21I', data, 0x20))
    valid_21 = sum(1 for o in offsets_21 if 0 < o < len(data))
    offsets_19 = list(struct.unpack_from('<19I', data, 0x20))
    valid_19 = sum(1 for o in offsets_19 if 0 < o < len(data))
    if valid_21 > valid_19 + 2:
        return 2
    return 1


def parse_rdt(file_path: str) -> RDTFile: #vers 4
    """Parse an RDT room file. Uses filename + header heuristics to detect version."""
    rdt = RDTFile(file_path=file_path, raw_data=b'')
    try:
        with open(file_path, 'rb') as f:
            rdt.raw_data = f.read()

        data = rdt.raw_data
        size = len(data)

        if size < 4:
            raise RE1FormatError(f"File too small: {size} bytes")

        # Decompress PRS if needed (RE3 PS1 RDTs are PRS-compressed)
        if _is_prs_compressed(data):
            try:
                from apps.core.re_unpacker import unpack_prs
                decompressed = unpack_prs(data)
                if len(decompressed) > size:
                    data = decompressed
                    size = len(data)
                    rdt.raw_data = data
            except Exception:
                pass

        if size < 0x94:
            raise RE1FormatError(f"File too small: {size} bytes")

        # Use filename to help detect version - much more reliable than heuristics
        game_ver = _detect_version_from_path(file_path, data)
        rdt.game_version = game_ver

        # Always create header object before parsers try to use it
        if rdt.header is None:
            rdt.header = RDTHeader()

        if game_ver == 3:
            _parse_rdt_re3(rdt, data, size)
        elif game_ver == 2:
            _parse_rdt_re2(rdt, data, size)
        else:
            _parse_rdt_re1(rdt, data, size)

        rdt.valid = True

    except RE1FormatError as e:
        rdt.parse_errors.append(str(e))
    except Exception as e:
        rdt.parse_errors.append(f"Unexpected error: {e}")

    return rdt


def _parse_rdt_re1(rdt: RDTFile, data: bytes, size: int): #vers 3
    """Parse RE1 RDT. Exact offsets and structs from re1.h + RoomRE1.h
    (Gemini-Loboto3/RE1-Mod-SDK, GPL).

    Key pointers (re1.h tagRdtHeader):
      0x48 pVcut  -> VCUT array (camera switch zones, NOT collision)
      0x4C pSca   -> SCA_HEAD + SCA_DATA[] (collision geometry)
      0x50 pObj[0]-> MODEL[] item models (TMD/TIM offsets, count=nItem)
      0x54 pObj[1]-> MODEL[] object models (count=nOmodel)
      0x60 pScrl  -> SCD init script (items placed via SCD_OBA opcodes)
      0x64 pScdx  -> SCD exec script
      0x6C pEmr   -> enemy placement
      0x94        -> RCUT Cut[nCut] camera array

    NOTE: RE1 item *positions* are set by SCD scripts (SCD_OBA opcode),
    not a flat placement table like RE2. nItem = number of item *models*.
    """
    if rdt.header is None:
        rdt.header = RDTHeader()
    if size < 0x94:
        rdt.parse_errors.append(f"File too small for RE1: {size} bytes")
        return

    import struct as _s

    n_cameras = data[1]
    n_items   = data[2]   # number of item model slots, not placement count
    n_omodel  = data[3]

    # Read all named pointers from re1.h offsets
    pVcut  = _s.unpack_from('<I', data, 0x48)[0]  # camera switch zones
    pSca   = _s.unpack_from('<I', data, 0x4C)[0]  # collision SCA
    pObj0  = _s.unpack_from('<I', data, 0x50)[0]  # item models
    pObj1  = _s.unpack_from('<I', data, 0x54)[0]  # object models
    pFlr   = _s.unpack_from('<I', data, 0x5C)[0]  # floor data
    pScrl  = _s.unpack_from('<I', data, 0x60)[0]  # SCD init
    pScdx  = _s.unpack_from('<I', data, 0x64)[0]  # SCD exec
    pEmr   = _s.unpack_from('<I', data, 0x6C)[0]  # enemies
    pEdd   = _s.unpack_from('<I', data, 0x70)[0]  # enemy anims
    pTim   = _s.unpack_from('<I', data, 0x84)[0]  # textures
    pVh    = _s.unpack_from('<I', data, 0x8C)[0]  # VAG header
    pVb    = _s.unpack_from('<I', data, 0x90)[0]  # VAG body

    # Store for shared parsers
    rdt.header.offsets = [0] * 19
    rdt.header.offsets[0]  = pVcut
    rdt.header.offsets[1]  = pSca
    rdt.header.offsets[6]  = pObj0
    rdt.header.offsets[7]  = pObj1
    rdt.header.offsets[8]  = pEmr
    rdt.header.offsets[9]  = pScrl
    rdt.header.offsets[10] = pScdx

    # --- Cameras: RCUT Cut[nCut] at 0x94, each 44 bytes ---
    # RCUT: pSp(4)+pTim(4)+View_p[3](12)+View_r[3](12)+Zero[2](8)+ViewR(4)
    cam_off   = 0x94
    RCUT_SIZE = 44
    for i in range(min(n_cameras, 16)):
        if cam_off + RCUT_SIZE > size:
            break
        eye  = _s.unpack_from('<3i', data, cam_off + 8)
        at   = _s.unpack_from('<3i', data, cam_off + 20)
        viewR = _s.unpack_from('<I', data, cam_off + 40)[0]
        rdt.cameras.append(RDTCamera(
            from_x=eye[0], from_y=eye[1], from_z=eye[2],
            to_x=at[0], to_y=at[1], to_z=at[2],
            camera_index=i, view_r=viewR,
        ))
        cam_off += RCUT_SIZE

    # --- Camera switches: VCUT array at pVcut ---
    # VCUT: Tcut(2)+Fcut(2)+Xz[4][2](16) = 20 bytes, 0xFFFF/0xFFFF = end
    if pVcut and 0 < pVcut < size:
        off = pVcut
        while off + 20 <= size:
            tcut, fcut = _s.unpack_from('<HH', data, off)
            if tcut == 0xFFFF and fcut == 0xFFFF:
                break
            if fcut > 16 or tcut > 16:  # sanity: camera index <= 16
                break
            xz = _s.unpack_from('<8h', data, off + 4)
            rdt.camera_switches.append(RDTCameraSwitch(
                from_cam=fcut, to_cam=tcut,
                x1=xz[0], z1=xz[1],
                x2=xz[4], z2=xz[5],
                floor=0,
            ))
            off += 20

    # --- Collision: SCA_HEAD + SCA_DATA[] at pSca ---
    # SCA_HEAD: Cx(2)+Cz(2)+Ptr[5](20) = 24 bytes
    # SCA_DATA: x0(2)+z0(2)+x1(2)+z1(2)+Id(2)+Type(2) = 12 bytes
    if pSca and 0 < pSca < size - 24:
        cx, cz = _s.unpack_from('<HH', data, pSca)
        counts = list(_s.unpack_from('<5I', data, pSca + 4))
        rdt.header.sca_counts = counts
        total = sum(counts)
        if 0 < total < 1000:  # sanity check
            sca_off = pSca + 24
            for _ in range(total):
                if sca_off + 12 > size:
                    break
                x0,z0,x1,z1,sid,stype = _s.unpack_from('<6H', data, sca_off)
                rdt.collision.append(RDTCollisionBoundary(
                    boundary_type=stype, x1=x0, z1=z0, x2=x1, z2=z1,
                    floor=0, density=0, sound_attr=sid,
                ))
                sca_off += 12

    # --- Enemies at pEmr ---
    _parse_rdt_enemies_re1(rdt, data, size)

    # --- Items: extracted from SCD init script ---
    # RE1 items are placed by SCD_OBA opcodes in the init script, not a table.
    # Parse the SCD to extract item placements.
    if pScrl and 0 < pScrl < size:
        _parse_re1_items_from_scd(rdt, data, size, pScrl)


def _parse_re1_items_from_scd(rdt: RDTFile, data: bytes,
                               size: int, scd_off: int): #vers 1
    """Extract item placements from RE1 SCD init script.

    RE1 SCD_OBA opcode (0x22/item set):
      opcode(1) id(1) be_flg(1) flag(1) x(2) y(2) z(2) cdir_y(2) unk[5*2] h(2) w(2) d(2)
      = 28 bytes total

    We scan the SCD for opcode 0x22 (item/object placement).
    """
    import struct as _s

    if scd_off + 2 > size:
        return

    # SCD init script: u16 length, then bytecodes
    script_len = _s.unpack_from('<H', data, scd_off)[0]
    if script_len == 0 or scd_off + 2 + script_len > size:
        return

    scd = data[scd_off + 2: scd_off + 2 + script_len]
    pos = 0
    while pos < len(scd) - 1:
        opcode = scd[pos]
        # 0x22 = OBA_SET (item/obstacle placement in RE1)
        if opcode == 0x22 and pos + 28 <= len(scd):
            vals = _s.unpack_from('<BBBBhhhh', scd, pos)
            item_id = vals[1]
            x, y, z = vals[4], vals[5], vals[6]
            cdir = vals[7]
            rdt.items.append(RDTItem(
                item_type=item_id, x=x, y=y, z=z,
                rotation=cdir, flags=vals[3], amount=1,
            ))
            pos += 28
            continue
        # Advance by 1 if unknown opcode (SCD is complex, we just scan)
        pos += 1



def _parse_rdt_re2(rdt: RDTFile, data: bytes, size: int): #vers 3
    """Parse RE2 PS1 RDT. Confirmed from real RE2 PS1 binaries (RESEVIL2_LEON_PSX).

    Header (8 bytes):
      [0]nSprite [1]nCut [2]nOmodel [3]nItem [4]nDoor [5]nRoom_at [6]Reverb [7]nSpriteMax
    23 section offsets (uint32 LE) at 0x08
    RCUT camera array at 0x64:
      Each RCUT = 32 bytes: pSp(4)+pTim(4)+View_p[3](12)+View_r[3](12)
      NOTE: PS1 = 32 bytes per RCUT, NOT 44 (PC version is 44)

    Sections (confirmed offsets):
      RID[7]=0x64     camera array (same as RCUT start)
      RVD[8]=cam_end  AOT trigger zones: 20-byte entries, 0xFF terminated
                      SCE(1)+SAT(1)+nFloor(1)+super(1)+x(2)+z(2)+w(2)+d(2)+data[8]
      LIT[9]          lighting (after RVD)
      SCA[6]          collision: Cx(s16)+Cz(s16)+8-byte rects to BLK section
      BLK[12]         floor boundaries: count(u32)+count×12-byte rects
      FLR[11]         floor data
      SCD0[15]        init script (AOT_SET places items/doors/triggers)
      SCD1[16]        run script
    """
    import struct as _s

    if rdt.header is None:
        rdt.header = RDTHeader()
    if size < 0x64:
        rdt.parse_errors.append(f"File too small for RE2: {size}")
        return

    n_cameras  = data[1]   # header[1] = nCut (number of camera views)
    n_bss_refs = data[2]   # header[2] = nOmodel = background pointer table entries
    rdt.header.num_cameras = n_cameras

    # 23 section offsets at 0x08
    offsets = list(_s.unpack_from('<23I', data, 0x08))
    rdt.header.offsets = offsets

    sca  = offsets[6]   # SCA collision
    # RVD starts at 0x64 + nCut*32 + header[2]*8 (confirmed from binary)
    rvd  = 0x64 + n_cameras * 32 + n_bss_refs * 8
    blk  = offsets[12]  # BLK floor boundaries
    flr  = offsets[11]  # FLR floor data
    scd0 = offsets[15]  # SCD0 init script
    scd1 = offsets[16]  # SCD1 run script

    # --- Cameras: RCUT at 0x64, each 32 bytes ---
    # View_p[3](12 bytes starting at +8) + View_r[3](12 bytes at +20)
    # pSp(4)+pTim(4) at +0,+4 are background sprite pointers (skip for now)
    RCUT_SIZE = 32
    cam_off = 0x64
    for i in range(min(n_cameras, 16)):
        if cam_off + RCUT_SIZE > size:
            break
        eye = _s.unpack_from('<3i', data, cam_off + 8)
        at  = _s.unpack_from('<3i', data, cam_off + 20)
        rdt.cameras.append(RDTCamera(
            from_x=eye[0], from_y=eye[1], from_z=eye[2],
            to_x=at[0],   to_y=at[1],   to_z=at[2],
            camera_index=i,
        ))
        cam_off += RCUT_SIZE

    # --- Camera trigger zones (RVD): 20-byte AOT entries, 0xFF terminated ---
    # SCE(1)+SAT(1)+nFloor(1)+super(1)+x(2)+z(2)+w(2)+d(2)+data[8] = 20 bytes
    # SCE=1 = camera cut zone (what camera to use in this area)
    if 0 < rvd < size:
        off = rvd
        while off + 20 <= size:
            sce = data[off]
            if sce == 0xFF:
                break
            sat, n_floor, sup = data[off+1], data[off+2], data[off+3]
            x, z, w, d = _s.unpack_from('<4h', data, off+4)
            ex = data[off+12:off+20]
            aot = RDTAot(
                aot_type=sce, x=x, z=z, w=w, d=d,
                floor=n_floor, super_type=sup,
                data=list(ex),
            )
            rdt.aot.append(aot)
            off += 20

    # --- Collision (SCA): Cx+Cz header, then 8-byte x0,z0,x1,z1 rects ---
    # Items run from SCA+4 to BLK start (total = (blk-sca-4)/8)
    if sca and blk and 0 < sca < blk < size:
        cx = _s.unpack_from('<h', data, sca)[0]
        cz = _s.unpack_from('<h', data, sca+2)[0]
        n_col = (blk - sca - 4) // 8
        if 0 < n_col < 500:
            for i in range(n_col):
                off = sca + 4 + i*8
                x0,z0,x1,z1 = _s.unpack_from('<4h', data, off)
                rdt.collision.append(RDTCollisionBoundary(
                    boundary_type=0, x1=x0, z1=z0, x2=x1, z2=z1,
                    floor=0, density=0, sound_attr=0,
                ))

    # --- Enemies ---
    _parse_rdt_enemies_re2(rdt, data, size)

    # --- Camera switches ---
    _parse_rdt_camera_switches(rdt, data, size)


def _parse_rdt_re3(rdt: RDTFile, data: bytes, size: int): #vers 1
    """Parse RE3 format RDT. Same structure as RE2 (21 offsets, cameras at 0xA8).
    RE3 uses same offset layout as RE2 but different item/enemy IDs.
    """
    rdt.game_version = 3
    _parse_rdt_re2(rdt, data, size)  # structure is identical to RE2


def _parse_rdt_items(rdt: RDTFile, data: bytes, size: int): #vers 2
    """Parse item placement data from RDT offset[2] (RE1)."""
    if not rdt.header or len(rdt.header.offsets) < 3:
        return
    item_offset = rdt.header.offsets[2]
    _parse_items_at(rdt, data, size, item_offset)


def _parse_rdt_items_re2(rdt: RDTFile, data: bytes, size: int): #vers 1
    """Parse item placement data from RDT offset[5] (RE2/RE3).
    RE2 AOT/item data is at offset index 5, not 2.
    RE2 item struct adds a scenario byte: x(2)y(2)z(2)rot(2)type(1)flags(1)amount(1)scenario(1)
    """
    if not rdt.header or len(rdt.header.offsets) < 6:
        return
    item_offset = rdt.header.offsets[5]
    _parse_items_at(rdt, data, size, item_offset)


def _parse_items_at(rdt: RDTFile, data: bytes, size: int,
                    item_offset: int): #vers 1
    """Shared item parser at a given offset."""
    if item_offset == 0 or item_offset >= size:
        return

    item_struct_size = 12
    off = item_offset
    max_items = 128  # raised from 64 - RE2 rooms can have many items

    for i in range(max_items):
        if off + item_struct_size > size:
            break
        vals = struct.unpack_from('<hhhHBBBB', data, off)
        item_type = vals[4]
        if item_type == 0xFF:  # terminator
            break
        # Sanity check: item_type 0 with all zeros is padding, not a real item
        if item_type == 0 and vals[0] == 0 and vals[1] == 0 and vals[2] == 0:
            break
        rdt.items.append(RDTItem(
            x=vals[0], y=vals[1], z=vals[2],
            rotation=vals[3],
            item_type=item_type,
            flags=vals[5],
            amount=vals[6],
        ))
        off += item_struct_size


def _parse_rdt_collision(rdt: RDTFile, data: bytes, size: int): #vers 1
    """Parse collision boundary data from RDT offset[1] (RE1)."""
    if not rdt.header or len(rdt.header.offsets) < 2:
        return
    col_offset = rdt.header.offsets[1]
    if col_offset == 0 or col_offset >= size:
        return
    _parse_collision_at(rdt, data, size, col_offset)


def _parse_collision_at(rdt: RDTFile, data: bytes, size: int, col_offset: int): #vers 1
    """Shared collision parser given a known offset."""

    # SCA header: 2+2+5*4 = 24 bytes
    if col_offset + 24 > size:
        return

    ceiling_x, ceiling_z = struct.unpack_from('<HH', data, col_offset)
    counts = list(struct.unpack_from('<5I', data, col_offset + 4))
    rdt.sca_counts = counts
    rdt.sca_ceiling = (ceiling_x, ceiling_z)

    boundary_struct_size = 16
    off = col_offset + 24
    total = sum(counts)
    for i in range(total):
        if off + boundary_struct_size > size:
            break
        vals = struct.unpack_from('<HhhhhBBBB', data, off)
        rdt.collision.append(RDTCollisionBoundary(
            boundary_type=vals[0],
            x1=vals[1], z1=vals[2], x2=vals[3], z2=vals[4],
            floor=vals[5], density=vals[6], sound_attr=vals[7],
        ))
        off += boundary_struct_size


def parse_tim(file_path: str) -> TIMFile: #vers 1
    """Parse a PSX TIM texture file."""
    tim = TIMFile(file_path=file_path)
    try:
        with open(file_path, 'rb') as f:
            data = f.read()

        if len(data) < 8:
            raise RE1FormatError("TIM too small")

        magic, flags = struct.unpack_from('<II', data, 0)
        # TIM magic = 0x10 in byte 0 (little-endian uint32 = 0x00000010)
        # Also accept 0x08 (some PC TIMs use a variant header)
        if magic not in (0x00000010, 0x00000008, 0x00000011):
            raise RE1FormatError(f"Bad TIM magic: 0x{magic:08X} (expected 0x00000010)")

        bpp_mode = flags & 0x07
        has_clut = bool(flags & 0x08)

        header = TIMHeader(magic=magic, flags=flags, bpp=bpp_mode, has_clut=has_clut)
        tim.header = header

        offset = 8
        clut_data = None
        palette = []

        # Read CLUT if present
        if has_clut:
            if offset + 12 > len(data):
                raise RE1FormatError("TIM CLUT truncated")
            clut_size = struct.unpack_from('<I', data, offset)[0]
            clut_x, clut_y, clut_w, clut_h = struct.unpack_from('<4H', data, offset + 4)
            clut_pixels_offset = offset + 12
            clut_count = clut_w * clut_h
            if clut_pixels_offset + clut_count * 2 > len(data):
                raise RE1FormatError("TIM CLUT pixel data truncated")
            for i in range(clut_count):
                c = struct.unpack_from('<H', data, clut_pixels_offset + i * 2)[0]
                palette.append(_tim16_to_rgba(c))
            offset += clut_size

        # Read pixel data block
        if offset + 12 > len(data):
            raise RE1FormatError("TIM pixel block truncated")

        pix_size = struct.unpack_from('<I', data, offset)[0]
        pix_x, pix_y, pix_w, pix_h = struct.unpack_from('<4H', data, offset + 4)
        pix_offset = offset + 12

        if bpp_mode == TIMHeader.COLOR_4BIT:
            tim.width = pix_w * 4
            tim.height = pix_h
            tim.rgba_data = _decode_tim_4bit(data, pix_offset, tim.width, tim.height, palette)
        elif bpp_mode == TIMHeader.COLOR_8BIT:
            tim.width = pix_w * 2
            tim.height = pix_h
            tim.rgba_data = _decode_tim_8bit(data, pix_offset, tim.width, tim.height, palette)
        elif bpp_mode == TIMHeader.COLOR_16BIT:
            tim.width = pix_w
            tim.height = pix_h
            tim.rgba_data = _decode_tim_16bit(data, pix_offset, tim.width, tim.height)
        elif bpp_mode == TIMHeader.COLOR_24BIT:
            tim.width = (pix_w * 2) // 3
            tim.height = pix_h
            tim.rgba_data = _decode_tim_24bit(data, pix_offset, tim.width, tim.height)
        else:
            raise RE1FormatError(f"Unknown TIM bpp mode: {bpp_mode}")

        tim.valid = True

    except RE1FormatError as e:
        tim.parse_errors.append(str(e))
    except Exception as e:
        tim.parse_errors.append(f"Unexpected: {e}")

    return tim


def _tim16_to_rgba(c: int) -> Tuple[int, int, int, int]: #vers 1
    """Convert 16-bit PSX color (5:5:5:1) to RGBA8888."""
    r = (c & 0x001F) << 3
    g = (c & 0x03E0) >> 2
    b = (c & 0x7C00) >> 7
    stp = (c >> 15) & 1
    a = 0 if (c == 0) else (128 if stp else 255)
    return (r, g, b, a)


def _decode_tim_4bit(data, offset, w, h, palette) -> bytes: #vers 1
    out = bytearray(w * h * 4)
    idx = 0
    for y in range(h):
        for x in range(0, w, 2):
            if offset >= len(data):
                break
            byte = data[offset]; offset += 1
            for nibble in [byte & 0x0F, (byte >> 4) & 0x0F]:
                if idx + 3 < len(out) and nibble < len(palette):
                    out[idx:idx+4] = palette[nibble]
                idx += 4
    return bytes(out)


def _decode_tim_8bit(data, offset, w, h, palette) -> bytes: #vers 1
    out = bytearray(w * h * 4)
    for i in range(w * h):
        if offset + i >= len(data):
            break
        p = data[offset + i]
        if p < len(palette):
            out[i*4:i*4+4] = palette[p]
    return bytes(out)


def _decode_tim_16bit(data, offset, w, h) -> bytes: #vers 1
    out = bytearray(w * h * 4)
    for i in range(w * h):
        off = offset + i * 2
        if off + 2 > len(data):
            break
        c = struct.unpack_from('<H', data, off)[0]
        r, g, b, a = _tim16_to_rgba(c)
        out[i*4:i*4+4] = (r, g, b, a)
    return bytes(out)


def _decode_tim_24bit(data, offset, w, h) -> bytes: #vers 1
    out = bytearray(w * h * 4)
    for i in range(w * h):
        off = offset + i * 3
        if off + 3 > len(data):
            break
        r, g, b = data[off], data[off+1], data[off+2]
        out[i*4:i*4+4] = (r, g, b, 255)
    return bytes(out)


def parse_emd(file_path: str) -> EMDFile: #vers 1
    """Parse an EMD model file (RE1 format)."""
    emd = EMDFile(file_path=file_path)
    try:
        with open(file_path, 'rb') as f:
            data = f.read()

        size = len(data)
        if size < 16:
            raise RE1FormatError("EMD too small")

        # Directory is at end - last 16 bytes = 4 offsets
        dir_offset = size - 16
        offsets = list(struct.unpack_from('<4I', data, dir_offset))

        sec0_offset = offsets[0]
        if sec0_offset == 0 or sec0_offset >= size:
            raise RE1FormatError("EMD section 0 offset invalid")

        # Section 0: mesh data
        # Read model entry header (28 bytes)
        if sec0_offset + 28 > size:
            raise RE1FormatError("EMD section 0 too small")

        v_off, v_cnt, n_off, n_cnt, t_off, t_cnt, dummy = struct.unpack_from('<7I', data, sec0_offset)

        mesh = EMDMesh()

        # Vertices: 8 bytes each (x,y,z,pad - signed short)
        for i in range(v_cnt):
            off = sec0_offset + v_off + i * 8
            if off + 6 > size:
                break
            x, y, z = struct.unpack_from('<3h', data, off)
            mesh.vertices.append(EMDVertex(x=x, y=y, z=z))

        # Normals: same format
        for i in range(n_cnt):
            off = sec0_offset + n_off + i * 8
            if off + 6 > size:
                break
            x, y, z = struct.unpack_from('<3h', data, off)
            mesh.normals.append(EMDVertex(x=x, y=y, z=z))

        # Triangles: variable, read t_cnt entries of 12 bytes (basic)
        for i in range(t_cnt):
            off = sec0_offset + t_off + i * 12
            if off + 6 > size:
                break
            v0, v1, v2 = struct.unpack_from('<3H', data, off)
            mesh.triangles.append(EMDTriangle(v0=v0, v1=v1, v2=v2))

        emd.meshes.append(mesh)
        emd.valid = True

    except RE1FormatError as e:
        emd.parse_errors.append(str(e))
    except Exception as e:
        emd.parse_errors.append(f"Unexpected: {e}")

    return emd


def parse_sca_header(data: bytes, offset: int = 0) -> SCAHeader: #vers 1
    """Parse SCA collision header from raw bytes at offset."""
    if offset + 24 > len(data):
        raise RE1FormatError("SCA header out of bounds")
    cx, cz = struct.unpack_from('<HH', data, offset)
    counts = list(struct.unpack_from('<5I', data, offset + 4))
    return SCAHeader(ceiling_x=cx, ceiling_z=cz, counts=counts)


# --- Enemy and AOT name tables ---

RE1_ENEMY_NAMES: dict = {
    0x00: "Zombie (Normal)",    0x01: "Zombie (Naked)",
    0x02: "Zombie (Lab)",       0x03: "Zombie (Researcher)",
    0x04: "Zombie Dog",         0x05: "Crow",
    0x06: "Hunter Alpha",       0x07: "Tarantula",
    0x08: "Plant 42",           0x09: "Chimera",
    0x0A: "Yawn (Small)",       0x0B: "Shark",
    0x0C: "Neptune",            0x0D: "Tyrant T-002",
    0x0E: "Yawn (Large)",       0x0F: "Plant 42 (Root)",
    0x10: "Plant 42 (Vine)",    0x11: "Zombie (Keeper)",
    0x40: "Cerberus",           0x41: "Spider",
    0x42: "Black Tiger",
}

RE2_ENEMY_NAMES: dict = {
    0x00: "Zombie (Normal)",    0x01: "Zombie (Naked)",
    0x02: "Zombie (Fat)",       0x03: "Zombie (Police)",
    0x04: "Zombie (Child)",     0x05: "Zombie Dog",
    0x06: "Crow",               0x07: "Licker (Normal)",
    0x08: "Licker (Red)",       0x09: "Crocodile",
    0x0A: "Web Spinner",        0x0B: "Black Tiger",
    0x0C: "G-Adult",            0x0D: "G-Adult (2nd)",
    0x0E: "Ivy",                0x0F: "Ivy (Purple)",
    0x10: "G-Embryo",           0x11: "G-Monster",
    0x12: "G-Monster (2nd)",    0x13: "G-Monster (3rd)",
    0x14: "G-Monster (4th)",    0x15: "G-Monster (5th)",
    0x40: "Marvin Branagh",     0x41: "Ada Wong",
    0x42: "Sherry",             0x43: "Robert Kendo",
    0x50: "Tyrant T-103",       0x51: "Super Tyrant",
}

RE3_ENEMY_NAMES: dict = {
    0x00: "Zombie (Normal)",    0x01: "Zombie (Naked)",
    0x02: "Zombie (Fat)",       0x03: "Zombie (Police)",
    0x04: "Zombie (Gail)",      0x05: "Zombie Dog",
    0x06: "Crow",               0x07: "Hunter Beta",
    0x08: "Hunter Gamma",       0x09: "Drain Deimos",
    0x0A: "Drain Deimos (Frog)",0x0B: "Brain Sucker",
    0x0C: "Nemesis (Stage 1)",  0x0D: "Nemesis (Tentacle)",
    0x0E: "Nemesis (Stage 2)",  0x0F: "Nemesis (Stage 3)",
    0x10: "Grave Digger",       0x11: "Giant Spider",
    0x12: "Sliding Worm",       0x13: "Nemesis (Final)",
    0x40: "Carlos Oliveira",    0x41: "Mikhail Victor",
    0x42: "Nikolai Zinoviev",
}

AOT_TYPE_NAMES: dict = {
    0: "None", 1: "Door", 2: "Item", 3: "Event",
    4: "Player", 5: "Auto", 6: "Message", 7: "Water",
}


def get_enemy_name(enemy_type: int, game: str = 're1') -> str: #vers 2
    """Return enemy name for given type and game version."""
    if game == 're3':
        table = RE3_ENEMY_NAMES
    elif game == 're2':
        table = RE2_ENEMY_NAMES
    else:
        table = RE1_ENEMY_NAMES
    return table.get(enemy_type, f"Unknown (0x{enemy_type:02X})")


# --- Enemy parsers ---

def _parse_items_re2_from_scd(rdt: RDTFile, data: bytes,
                               size: int, off: int): #vers 1
    """Parse RE2 item placements from SCD-adjacent data.
    Called as fallback when AOT parsing finds nothing.
    Item struct (RE2): type(2) x(2) z(2) w(2) d(2) floor(1) super(1) data[8] = 20 bytes
    """
    if off == 0 or off >= size:
        return
    _parse_aot_at(rdt, data, size, off)


def _parse_rdt_enemies_re1(rdt: RDTFile, data: bytes, size: int): #vers 1
    """Parse RE1 enemy placement from offset[8]."""
    if not rdt.header or len(rdt.header.offsets) < 9:
        return
    off = rdt.header.offsets[8]
    if off == 0 or off >= size:
        return
    struct_size = 14
    for _ in range(32):
        if off + struct_size > size:
            break
        vals = struct.unpack_from('<BhhhHHHH', data, off)
        if vals[0] == 0xFF:
            break
        rdt.enemies.append(RDTEnemy(
            enemy_type=vals[0], x=vals[1], y=vals[2], z=vals[3],
            rotation=vals[4], id=vals[5], num=vals[6],
            floor=0, sound_bank=0, effect_bank=0,
        ))
        off += struct_size


def _parse_rdt_enemies_re2(rdt: RDTFile, data: bytes, size: int): #vers 3
    """Parse RE2 PS1 enemy placement.
    RE2 enemies are placed by SCD scripts (ENEMY_SET opcode 0x44/0x4E).
    The ETIM section (offsets[20]) contains the enemy model texture index table.
    Full SCD parsing required for enemy positions - placeholder until SCD parser done.
    """
    pass  # TODO: parse ENEMY_SET from SCD0/SCD1


# --- AOT parsers ---

def _parse_rdt_aot_re1(rdt: RDTFile, data: bytes, size: int): #vers 1
    """Parse RE1 AOT from offset[6]."""
    if not rdt.header or len(rdt.header.offsets) < 7:
        return
    off = rdt.header.offsets[6]
    if off == 0 or off >= size:
        return
    _parse_aot_at(rdt, data, size, off)


def _parse_rdt_aot_re2(rdt: RDTFile, data: bytes, size: int): #vers 1
    """Parse RE2/RE3 AOT from offset[5]."""
    if not rdt.header or len(rdt.header.offsets) < 6:
        return
    off = rdt.header.offsets[5]
    if off == 0 or off >= size:
        return
    _parse_aot_at(rdt, data, size, off)


def _parse_aot_at(rdt: RDTFile, data: bytes, size: int, off: int): #vers 1
    """Shared AOT parser. Each entry is 20 bytes."""
    struct_size = 20
    for _ in range(64):
        if off + struct_size > size:
            break
        vals = struct.unpack_from('<HhhHHBB', data, off)
        aot_type = vals[0]
        if aot_type == 0xFFFF:
            break
        aot_data = data[off + 12: off + 20]
        rdt.aot.append(RDTAot(
            aot_type=aot_type & 0xFF,
            x=vals[1], z=vals[2],
            w=vals[3], d=vals[4],
            floor=vals[5], super_type=vals[6],
            data=aot_data,
        ))
        off += struct_size


def _parse_rdt_camera_switches(rdt: RDTFile, data: bytes, size: int): #vers 1
    """Parse camera switch zones from offset[3] or [4]."""
    if not rdt.header or len(rdt.header.offsets) < 4:
        return
    for idx in [3, 4, 5]:
        if idx >= len(rdt.header.offsets):
            continue
        off = rdt.header.offsets[idx]
        if off == 0 or off >= size or off + 12 > size:
            continue
        first = struct.unpack_from('<HH', data, off)
        if first[0] > 16 or first[1] > 16:
            continue
        struct_size = 12
        switches = []
        for _ in range(32):
            if off + struct_size > size:
                break
            vals = struct.unpack_from('<HHhhhh', data, off)
            if vals[0] == 0xFFFF:
                break
            switches.append(RDTCameraSwitch(
                from_cam=vals[0], to_cam=vals[1],
                x1=vals[2], z1=vals[3],
                x2=vals[4], z2=vals[5],
                floor=0,
            ))
            off += struct_size
        if switches:
            rdt.camera_switches = switches
            return
