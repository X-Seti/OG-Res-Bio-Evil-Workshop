#!/usr/bin/env python3
#this belongs in apps/core/re_backgrounds.py - Version: 1
# X-Seti - May22 2026 - ResBio-Evil-Workshop - Background Image Loader
"""
RE Background Image Loader
Finds and decodes room background images alongside RDT files.

PS1:  room000.BSS  (one BSS per room, raw MDEC/ADPCM)
PC:   ROOM0000.PAK (one PAK per camera angle)
      ROOM0001.PAK, ROOM0002.PAK ... etc

Naming: ROOMsrrC.ext  s=stage, rr=room hex, C=camera index
e.g. ROOM1000.PAK = stage 1, room 00, camera 0
     ROOM1001.PAK = stage 1, room 00, camera 1

Returns RGBA bytes + dimensions for use with QImage.
"""

import os
import struct
from typing import Optional, List, Tuple, Dict
from dataclasses import dataclass, field

from apps.core.re1_formats import parse_tim, TIMFile
from apps.core.re_unpacker import unpack_pak, unpack_bss_re2, unpack_bss_re3

##Methods list -
# find_backgrounds_for_rdt
# load_background
# load_background_pak
# load_background_bss
# _find_files_by_stem
# _room_stem_from_rdt
# get_thumbnail_rgba

##class BackgroundImage:


@dataclass
class BackgroundImage: #vers 1
    """A decoded room background image ready for display."""
    path: str
    camera_index: int
    width: int
    height: int
    rgba_data: bytes
    valid: bool = False
    error: str = ""

    @property
    def name(self) -> str:
        return os.path.basename(self.path)


def _room_stem_from_rdt(rdt_path: str) -> str: #vers 1
    """Extract the room stem from an RDT filename.
    ROOM000.RDT  -> ROOM000
    ROOM11C1.RDT -> ROOM11C  (strip trailing scenario digit)
    room1000.rdt -> ROOM100
    """
    name = os.path.splitext(os.path.basename(rdt_path))[0].upper()
    if not name.startswith('ROOM'):
        return name
    digits = name[4:]  # everything after "ROOM"
    # RE2/RE3: trailing 0 or 1 is scenario selector, not part of room ID
    # If last char is 0 or 1 and stem is 4+ chars, strip it
    if len(digits) >= 4 and digits[-1] in ('0', '1'):
        digits = digits[:-1]
    return 'ROOM' + digits


def _find_files_by_stem(folder: str, stem: str,
                        extensions: List[str]) -> List[str]: #vers 1
    """Find files in folder matching stem (case-insensitive) with given extensions."""
    results = []
    try:
        for fname in sorted(os.listdir(folder)):
            name_up = fname.upper()
            base_up = os.path.splitext(name_up)[0]
            ext_up  = os.path.splitext(name_up)[1]
            if ext_up in [e.upper() for e in extensions]:
                # Exact match or stem match (stem + camera digit)
                if base_up == stem.upper() or base_up.startswith(stem.upper()):
                    results.append(os.path.join(folder, fname))
    except OSError:
        pass
    return results


def find_backgrounds_for_rdt(rdt_path: str) -> List[str]: #vers 1
    """Return list of background file paths for a given RDT file.
    Searches in the same folder as the RDT.
    Returns paths sorted by camera index.
    """
    folder = os.path.dirname(rdt_path)
    stem   = _room_stem_from_rdt(rdt_path)

    # Try PAK first (PC), then BSS (PS1)
    paths = _find_files_by_stem(folder, stem, ['.PAK', '.pak'])
    if not paths:
        paths = _find_files_by_stem(folder, stem, ['.BSS', '.bss'])

    return sorted(paths)


def load_background(path: str, camera_index: int = 0) -> BackgroundImage: #vers 1
    """Load a single background file (PAK or BSS). Returns BackgroundImage."""
    ext = os.path.splitext(path)[1].upper()

    if ext == '.PAK':
        return load_background_pak(path, camera_index)
    elif ext == '.BSS':
        return load_background_bss(path, camera_index)
    else:
        bg = BackgroundImage(path=path, camera_index=camera_index,
                             width=0, height=0, rgba_data=b'')
        bg.error = f"Unknown background format: {ext}"
        return bg


def load_background_pak(path: str, camera_index: int = 0) -> BackgroundImage: #vers 1
    """Load a RE1 PC PAK background file.
    PAK files decompress to a TIM image.
    """
    bg = BackgroundImage(path=path, camera_index=camera_index,
                         width=0, height=0, rgba_data=b'')
    try:
        with open(path, 'rb') as f:
            raw = f.read()

        # Decompress PAK -> TIM bytes
        tim_bytes = unpack_pak(raw)
        if not tim_bytes:
            bg.error = "PAK decompression returned empty data"
            return bg

        # Parse the TIM
        tim = _parse_tim_from_bytes(tim_bytes, path)
        if not tim.valid:
            bg.error = f"TIM parse failed: {'; '.join(tim.parse_errors)}"
            return bg

        bg.width      = tim.width
        bg.height     = tim.height
        bg.rgba_data  = tim.rgba_data
        bg.valid      = True

    except Exception as e:
        bg.error = str(e)

    return bg


def load_background_bss(path: str, camera_index: int = 0,
                        game: str = 're1') -> BackgroundImage: #vers 1
    """Load a RE1/RE2 PS1 BSS background file.
    BSS is raw MDEC-compressed video frame. We extract the TIM mask portion.
    For full MDEC decoding a hardware decoder is needed - we extract what we can.
    game: 're1', 're2', 're3'
    """
    bg = BackgroundImage(path=path, camera_index=camera_index,
                         width=0, height=0, rgba_data=b'')
    try:
        with open(path, 'rb') as f:
            raw = f.read()

        # BSS file: starts with MDEC video data, TIM mask follows
        # For RE1 BSS the TIM is embedded after the MDEC frame
        # Try to find TIM magic (0x10 0x00 0x00 0x00)
        TIM_MAGIC = b'\x10\x00\x00\x00'
        tim_offset = raw.find(TIM_MAGIC)

        if tim_offset >= 0:
            tim_bytes = raw[tim_offset:]
            tim = _parse_tim_from_bytes(tim_bytes, path)
            if tim.valid:
                bg.width     = tim.width
                bg.height    = tim.height
                bg.rgba_data = tim.rgba_data
                bg.valid     = True
                return bg

        # No TIM found in raw - try BSS decompression
        try:
            if game == 're3':
                decompressed = unpack_bss_re3(raw)
            else:
                decompressed = unpack_bss_re2(raw)

            tim_offset2 = decompressed.find(TIM_MAGIC)
            if tim_offset2 >= 0:
                tim = _parse_tim_from_bytes(decompressed[tim_offset2:], path)
                if tim.valid:
                    bg.width     = tim.width
                    bg.height    = tim.height
                    bg.rgba_data = tim.rgba_data
                    bg.valid     = True
                    return bg
        except Exception:
            pass

        bg.error = "No TIM data found in BSS file (MDEC-only, decoder not implemented)"

    except Exception as e:
        bg.error = str(e)

    return bg


def _parse_tim_from_bytes(data: bytes, source_path: str = '') -> TIMFile: #vers 1
    """Parse a TIM from raw bytes (not a file path)."""
    import tempfile, os as _os
    # Write to temp file and parse
    try:
        with tempfile.NamedTemporaryFile(suffix='.tim', delete=False) as f:
            f.write(data)
            tmp = f.name
        tim = parse_tim(tmp)
        _os.unlink(tmp)
        return tim
    except Exception as e:
        tim = TIMFile(file_path=source_path)
        tim.parse_errors.append(str(e))
        return tim


def get_thumbnail_rgba(rdt_path: str,
                       max_width: int = 130,
                       max_height: int = 36) -> Optional[BackgroundImage]: #vers 1
    """Load the camera-0 background for a room and scale to thumbnail size.
    Returns None if no background found or decode failed.
    """
    paths = find_backgrounds_for_rdt(rdt_path)
    if not paths:
        return None

    bg = load_background(paths[0], camera_index=0)
    if not bg.valid or not bg.rgba_data:
        return None

    # Scale down to thumbnail dimensions using simple nearest-neighbour
    if bg.width <= 0 or bg.height <= 0:
        return None

    scale = min(max_width / bg.width, max_height / bg.height)
    tw = max(1, int(bg.width  * scale))
    th = max(1, int(bg.height * scale))

    scaled = _scale_rgba(bg.rgba_data, bg.width, bg.height, tw, th)
    return BackgroundImage(
        path=bg.path, camera_index=0,
        width=tw, height=th,
        rgba_data=scaled, valid=True
    )


def _scale_rgba(data: bytes, src_w: int, src_h: int,
                dst_w: int, dst_h: int) -> bytes: #vers 1
    """Nearest-neighbour scale of RGBA8888 data."""
    out = bytearray(dst_w * dst_h * 4)
    for dy in range(dst_h):
        sy = int(dy * src_h / dst_h)
        for dx in range(dst_w):
            sx = int(dx * src_w / dst_w)
            src_off = (sy * src_w + sx) * 4
            dst_off = (dy * dst_w + dx) * 4
            out[dst_off:dst_off+4] = data[src_off:src_off+4]
    return bytes(out)
