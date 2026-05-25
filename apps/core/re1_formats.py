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
class RDTCamera: #vers 1
    masks_offset: int
    tim_masks_offset: int
    from_x: int
    from_y: int
    from_z: int
    to_x: int
    to_y: int
    to_z: int
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
class RDTHeader: #vers 1
    unknown0: int
    num_cameras: int
    num_sound_banks: int
    unknown1: bytes
    offsets: List[int] = field(default_factory=list)  # 19 absolute offsets

    OFFSET_COUNT = 19
    HEADER_SIZE = 0x94  # Camera data starts here


@dataclass
class RDTFile: #vers 1
    file_path: str
    raw_data: bytes
    header: Optional[RDTHeader] = None
    cameras: List[RDTCamera] = field(default_factory=list)
    items: List[RDTItem] = field(default_factory=list)
    collision: List[RDTCollisionBoundary] = field(default_factory=list)
    sca_counts: List[int] = field(default_factory=list)  # [floors, slopes, walls, doors, other]
    sca_ceiling: tuple = field(default_factory=tuple)    # (ceiling_x, ceiling_z)
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
    magic: int       # 0x10000000
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

RE1_ITEM_NAMES = { #vers 1
    0x00: "Nothing",
    0x01: "Combat Knife",
    0x02: "Beretta",
    0x03: "Shotgun",
    0x04: "Magnum",
    0x05: "Flamethrower",
    0x06: "Bazooka",
    0x07: "Acid Rounds",
    0x08: "Flame Rounds",
    0x09: "Beretta Rounds",
    0x0A: "Shotgun Shells",
    0x0B: "Magnum Rounds",
    0x0C: "Keys",
    0x0D: "Herb (Green)",
    0x0E: "Herb (Red)",
    0x0F: "Herb (Blue)",
    0x10: "First Aid Spray",
    0x11: "Mixed Herbs (G+R)",
    0x12: "Mixed Herbs (G+B)",
    0x13: "Mixed Herbs (G+G)",
    0x14: "Mixed Herbs (G+G+G)",
    0x15: "Mixed Herbs (G+R+B)",
    0x20: "Ink Ribbon",
    0x28: "Wooden Emblem",
    0x29: "Gold Emblem",
    0x2A: "Blue Jewel",
    0x2B: "Red Jewel",
    0x2C: "Music Notes",
    0x30: "Armor Key",
    0x31: "Sheild Key",
    0x32: "Helmet Key",
    0x33: "Sword Key",
    0x36: "Battery",
    0x37: "MO Disk",
    0x38: "Wind Crest",
    0x39: "Flamethrower Part",
    0x3A: "Slides",
    0x3B: "Moon Crest",
    0x3C: "Star Crest",
    0x3D: "Sun Crest",
    0x3E: "Lighter",
    0x3F: "Lockpick",
    0x41: "Doom Book Vol 2",
    0x48: "Dagger",
    0x49: "Clip (Empty)",
    0x4A: "Clip (Full)",
    0x4B: "Clip (Infinite)",
    0x50: "Document",
}

def get_item_name(item_type: int) -> str: #vers 1
    return RE1_ITEM_NAMES.get(item_type, f"Unknown (0x{item_type:02X})")


# --- Parser Functions ---

def _detect_rdt_version(data: bytes) -> int: #vers 1
    """Detect RDT game version. Returns 1=RE1, 2=RE2/RE3.
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
        return 2
    # Both plausible - check offset[0] at 0x20+8*4=0x40 for RE2
    # RE2 has 21 offsets so offset[4] (camera switches) is at different slot
    # Cross-check: read 21 offsets and see if any non-zero values are file-range valid
    offsets_21 = list(struct.unpack_from('<21I', data, 0x20))
    valid_21 = sum(1 for o in offsets_21 if 0 < o < len(data))
    offsets_19 = list(struct.unpack_from('<19I', data, 0x20))
    valid_19 = sum(1 for o in offsets_19 if 0 < o < len(data))
    # More valid offsets in 21-count suggests RE2
    if valid_21 > valid_19 + 2:
        return 2
    return 1


def parse_rdt(file_path: str) -> RDTFile: #vers 2
    """Parse an RDT room file. Auto-detects RE1 vs RE2/RE3 format."""
    rdt = RDTFile(file_path=file_path, raw_data=b'')
    try:
        with open(file_path, 'rb') as f:
            rdt.raw_data = f.read()

        data = rdt.raw_data
        size = len(data)

        if size < 0x94:
            raise RE1FormatError(f"File too small: {size} bytes")

        game_ver = _detect_rdt_version(data)

        if game_ver == 2:
            _parse_rdt_re2(rdt, data, size)
        else:
            _parse_rdt_re1(rdt, data, size)

        rdt.valid = True

    except RE1FormatError as e:
        rdt.parse_errors.append(str(e))
    except Exception as e:
        rdt.parse_errors.append(f"Unexpected error: {e}")

    return rdt


def _parse_rdt_re1(rdt: RDTFile, data: bytes, size: int): #vers 1
    """Parse RE1 format RDT. 19 offsets, cameras at 0x94."""
    unknown0, num_cameras, num_sound_banks = struct.unpack_from('<BBB', data, 0)
    header = RDTHeader(
        unknown0=unknown0,
        num_cameras=num_cameras,
        num_sound_banks=num_sound_banks,
        unknown1=data[3:6],
    )
    if size < 0x20 + 19 * 4:
        raise RE1FormatError("File too small for RE1 offset table")
    header.offsets = list(struct.unpack_from('<19I', data, 0x20))
    rdt.header = header

    cam_offset = 0x94
    cam_struct_size = 44
    for i in range(num_cameras):
        off = cam_offset + i * cam_struct_size
        if off + cam_struct_size > size:
            rdt.parse_errors.append(f"Camera {i}: out of bounds")
            break
        vals = struct.unpack_from('<11i', data, off)
        rdt.cameras.append(RDTCamera(
            masks_offset=vals[0], tim_masks_offset=vals[1],
            from_x=vals[2], from_y=vals[3], from_z=vals[4],
            to_x=vals[5],   to_y=vals[6],   to_z=vals[7],
            unknown=list(vals[8:11]),
        ))

    _parse_rdt_items(rdt, data, size)
    _parse_rdt_collision(rdt, data, size)


def _parse_rdt_re2(rdt: RDTFile, data: bytes, size: int): #vers 1
    """Parse RE2/RE3 format RDT. 21 offsets, cameras at 0xA8.
    RE2 header: byte[0]=flags, byte[1]=num_sprites, byte[2]=num_cameras,
                byte[3]=num_sound_banks
    """
    num_sprites, num_cameras, num_sound_banks = data[1], data[2], data[3]
    header = RDTHeader(
        unknown0=data[0],
        num_cameras=num_cameras,
        num_sound_banks=num_sound_banks,
        unknown1=data[4:7],
    )
    if size < 0x20 + 21 * 4:
        raise RE1FormatError("File too small for RE2 offset table")
    header.offsets = list(struct.unpack_from('<21I', data, 0x20))
    # Pad to 21 if needed for shared code
    while len(header.offsets) < 21:
        header.offsets.append(0)
    rdt.header = header

    # RE2 cameras start at 0xA8 (header 8 + 21 offsets*4 = 8+84=92... 
    # Actually: 0x20 + 21*4 = 0x74, but there's extra header data up to 0xA8)
    cam_offset = 0xA8
    cam_struct_size = 44
    for i in range(num_cameras):
        off = cam_offset + i * cam_struct_size
        if off + cam_struct_size > size:
            rdt.parse_errors.append(f"Camera {i}: out of bounds (RE2)")
            break
        vals = struct.unpack_from('<11i', data, off)
        rdt.cameras.append(RDTCamera(
            masks_offset=vals[0], tim_masks_offset=vals[1],
            from_x=vals[2], from_y=vals[3], from_z=vals[4],
            to_x=vals[5],   to_y=vals[6],   to_z=vals[7],
            unknown=list(vals[8:11]),
        ))

    # RE2 offset table (21 entries):
    #  [2]=collision(SCA), [5]=items/AOT, [2]=cameras already handled
    _parse_rdt_items_re2(rdt, data, size)
    _parse_rdt_collision_re2(rdt, data, size)


def _parse_rdt_collision_re2(rdt: RDTFile, data: bytes, size: int): #vers 2
    """Parse collision from RE2 RDT.
    RE2 offset table: [2]=collision(SCA), not [3] as previously assumed.
    Tries offset[2] first, then [1] and [3] as fallbacks.
    """
    if not rdt.header or len(rdt.header.offsets) < 3:
        return
    # Try offset[2] (correct for RE2)
    for idx in [2, 1, 3]:
        if idx >= len(rdt.header.offsets):
            continue
        col_offset = rdt.header.offsets[idx]
        if col_offset == 0 or col_offset >= size:
            continue
        # Quick sanity: SCA header starts with ceiling_x, ceiling_z (2 bytes each)
        # followed by 5 uint32 counts - check total looks plausible
        if col_offset + 24 > size:
            continue
        counts = list(struct.unpack_from('<5I', data, col_offset + 4))
        total = sum(counts)
        if total > 500:  # unreasonable boundary count
            continue
        _parse_collision_at(rdt, data, size, col_offset)
        if rdt.collision:  # parsed something valid
            return


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
        if magic != 0x10000000:
            raise RE1FormatError(f"Bad TIM magic: 0x{magic:08X}")

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
