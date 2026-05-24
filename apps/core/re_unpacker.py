#!/usr/bin/env python3
#this belongs in apps/core/re_unpacker.py - Version: 1
# X-Seti - May22 2026 - ResBio-Evil-Workshop - RE File Unpacker
"""
RE File Unpacker - Identifies and extracts game files from all
Resident Evil / Biohazard releases: RE1, RE2, RE3 on PS1 and PC.

Compression formats (ported from reevengi-tools by Patrice Mandin):
  PAK  - RE1 PC background images (LZW variant)
  PRS  - RE3 Saturn/PC (SEGA LZS variant)
  BSS  - RE1/RE2 PS1 background images (raw MDEC)
  SLD  - RE2/RE3 PS1 TIM mask (RE2 or RE3 algorithm)
  ADT  - RE2 PC background images (Huffman+LZ)
  ROFS - RE3 PC archive (ROFSxx.DAT)
  BIN  - RE2 PS1 DAT/*.BIN archive

Platform/version detection:
  RE1 PS1  - STAGE/ROOM*.RDT + ENEMY/*.EMD + *.BSS backgrounds
  RE1 PC   - ROOM*.RDT + *.PAK backgrounds + *.PLD models
  RE2 PS1  - ROOM/*.RDT in BIN archives + *.BSS
  RE2 PC   - ROOM*.RDT + *.ADT backgrounds
  RE3 PS1  - ROOM*.RDT (PRS compressed) + *.BSS
  RE3 PC   - ROFS*.DAT archives -> RDT + *.PAK backgrounds
"""

import os
import struct
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict
from enum import Enum

##Methods list -
# detect_game_version
# unpack_pak
# unpack_prs
# unpack_bss_re2
# unpack_bss_re3
# scan_game_folder
# extract_rofs
# extract_bin_re2
# list_rofs_contents
# list_bin_contents

##class GameVersion:
##class GameFile:
##class GameFolder:


class GameVersion(Enum): #vers 1
    UNKNOWN  = "Unknown"
    RE1_PS1  = "Biohazard / RE1 (PS1)"
    RE1_PC   = "Resident Evil 1 (PC)"
    RE2_PS1  = "Biohazard 2 / RE2 (PS1)"
    RE2_PC   = "Resident Evil 2 (PC)"
    RE3_PS1  = "Biohazard 3 / RE3 (PS1)"
    RE3_PC   = "Resident Evil 3 (PC)"


@dataclass
class GameFile: #vers 1
    path: str
    file_type: str        # "RDT", "TIM", "EMD", "PAK", "BSS", "ADT", "PLD", etc.
    compressed: bool
    size: int
    game: GameVersion = GameVersion.UNKNOWN

    @property
    def name(self) -> str:
        return os.path.basename(self.path)


@dataclass
class GameFolder: #vers 1
    root_path: str
    version: GameVersion = GameVersion.UNKNOWN
    rdt_files: List[GameFile] = field(default_factory=list)
    texture_files: List[GameFile] = field(default_factory=list)
    model_files: List[GameFile] = field(default_factory=list)
    archive_files: List[GameFile] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    @property
    def total_files(self) -> int:
        return (len(self.rdt_files) + len(self.texture_files) +
                len(self.model_files) + len(self.archive_files))


# --- Game version detection ---

def detect_game_version(folder_path: str) -> GameVersion: #vers 1
    """Detect which RE game/platform from folder contents."""
    if not os.path.isdir(folder_path):
        return GameVersion.UNKNOWN

    files_upper = [f.upper() for f in os.listdir(folder_path)]
    subdirs_upper = [
        d.upper() for d in os.listdir(folder_path)
        if os.path.isdir(os.path.join(folder_path, d))
    ]

    # RE3 PC: has ROFS*.DAT archives
    rofs = [f for f in files_upper if f.startswith('ROFS') and f.endswith('.DAT')]
    if rofs:
        return GameVersion.RE3_PC

    # RE3 PS1: PRS-compressed RDTs, folder often named STAGE or ROOM
    rdts = [f for f in files_upper if f.endswith('.RDT')]
    if rdts:
        # Check first RDT for PRS signature
        for f in os.listdir(folder_path):
            if f.upper().endswith('.RDT'):
                full = os.path.join(folder_path, f)
                with open(full, 'rb') as fh:
                    magic = fh.read(4)
                if magic[:2] == b'\x10\x00':
                    return GameVersion.RE3_PS1
                if magic[:2] == b'\x00\x01' or magic[:2] == b'\x01\x00':
                    return GameVersion.RE1_PS1

    # RE2 PS1: BIN archives in DAT/
    bins = [f for f in files_upper if f.endswith('.BIN')]
    dat_dir = 'DAT' in subdirs_upper or 'DATBIO' in subdirs_upper
    if bins and dat_dir:
        return GameVersion.RE2_PS1

    # RE2 PC: ADT background files
    adts = [f for f in files_upper if f.endswith('.ADT')]
    if adts:
        return GameVersion.RE2_PC

    # RE1 PC: PAK background files
    paks = [f for f in files_upper if f.endswith('.PAK')]
    if paks and rdts:
        return GameVersion.RE1_PC

    # RE1 PC: STAGE/ subdir with RDTs
    if 'STAGE' in subdirs_upper:
        stage_path = os.path.join(folder_path,
            next(d for d in os.listdir(folder_path) if d.upper() == 'STAGE'))
        stage_rdts = [f for f in os.listdir(stage_path) if f.upper().endswith('.RDT')]
        if stage_rdts:
            return GameVersion.RE1_PS1

    if rdts:
        return GameVersion.RE1_PC

    return GameVersion.UNKNOWN


def scan_game_folder(folder_path: str) -> GameFolder: #vers 1
    """Walk a game folder and categorise all known file types."""
    gf = GameFolder(root_path=folder_path)
    gf.version = detect_game_version(folder_path)

    ext_map = {
        # Room files
        '.RDT': 'rdt_files',
        # Textures / backgrounds
        '.TIM': 'texture_files',
        '.PAK': 'texture_files',
        '.ADT': 'texture_files',
        '.BSS': 'texture_files',
        '.SLD': 'texture_files',
        '.PIX': 'texture_files',
        '.RGB': 'texture_files',
        # 3D models
        '.EMD': 'model_files',
        '.PLD': 'model_files',
        '.EDD': 'model_files',
        '.IVM': 'model_files',
        '.DOR': 'model_files',
        '.EMW': 'model_files',
        '.TMD': 'model_files',
        # Audio
        '.VAG': 'archive_files',
        '.VB':  'archive_files',
        '.HED': 'archive_files',
        '.HSB': 'archive_files',
        '.XAS': 'archive_files',
        # Video
        '.STR': 'archive_files',
        # Archives/data
        '.DAT': 'archive_files',
        '.BIN': 'archive_files',
    }

    rofs_exts = {'.DAT'}

    for dirpath, dirnames, filenames in os.walk(folder_path):
        dirnames.sort()
        for fname in sorted(filenames):
            ext = os.path.splitext(fname)[1].upper()
            full = os.path.join(dirpath, fname)
            size = os.path.getsize(full)

            target = ext_map.get(ext)
            if not target:
                continue

            compressed = _is_compressed(full, ext)
            gfile = GameFile(
                path=full,
                file_type=ext.lstrip('.'),
                compressed=compressed,
                size=size,
                game=gf.version,
            )
            getattr(gf, target).append(gfile)

    return gf


def _is_compressed(path: str, ext: str) -> bool: #vers 1
    """Quick check if file appears compressed."""
    try:
        with open(path, 'rb') as f:
            magic = f.read(4)
        if ext == '.PAK':
            return True  # always LZW
        if ext == '.ADT':
            return True  # always Huffman+LZ
        if ext in ('.BSS', '.SLD'):
            return True  # always compressed
        if ext == '.RDT' and magic[:2] == b'\x10\x00':
            return True  # PRS compressed (RE3)
    except OSError:
        pass
    return False


# --- PAK decompressor (RE1 PC backgrounds) ---
# Ported from reevengi-tools depack_pak.c (Patrice Mandin / ScummVM team)
# LZW variant with 9-bit initial code width

def unpack_pak(data: bytes) -> bytes: #vers 1
    """Decompress RE1 PC PAK file. Returns raw bytes."""
    DECODE_SIZE = 35024

    flags  = [0xFFFFFFFF] * DECODE_SIZE
    index  = [0] * DECODE_SIZE
    values = [0] * DECODE_SIZE

    decode_stack = bytearray(DECODE_SIZE)
    out = bytearray()

    src_pos = 0
    src_byte = 0
    tmp_mask = 0x80

    def read_bit() -> int:
        nonlocal src_byte, tmp_mask, src_pos
        if tmp_mask == 0x80:
            src_byte = data[src_pos] if src_pos < len(data) else 0
            src_pos += 1
        bit = 1 if (tmp_mask & src_byte) else 0
        tmp_mask >>= 1
        if tmp_mask == 0:
            tmp_mask = 0x80
        return bit

    def read_bits(n: int) -> int:
        val = 0
        mask = 1 << (n - 1)
        while mask > 0:
            if read_bit():
                val |= mask
            mask >>= 1
        return val

    def decode_string(stack_off: int, code: int) -> int:
        while code > 255:
            decode_stack[stack_off] = values[code]
            stack_off += 1
            code = index[code]
        decode_stack[stack_off] = code
        return stack_off

    stop = False
    while not stop:
        for i in range(DECODE_SIZE):
            flags[i] = 0xFFFFFFFF
        lzwnext = 0x103
        num_bits = 9

        c = lzwold = read_bits(num_bits)
        if lzwold == 0x100:
            break
        out.append(c)

        while True:
            lzwnew = read_bits(num_bits)
            if lzwnew == 0x100:
                stop = True
                break
            if lzwnew == 0x102:
                break
            if lzwnew == 0x101:
                num_bits += 1
                continue

            if lzwnew >= lzwnext:
                decode_stack[0] = c
                i = decode_string(1, lzwold)
            else:
                i = decode_string(0, lzwnew)

            c = decode_stack[i]
            while i >= 0:
                out.append(decode_stack[i])
                i -= 1

            index[lzwnext]  = lzwold
            values[lzwnext] = c
            lzwnext += 1
            lzwold = lzwnew

    return bytes(out)


# --- PRS decompressor (RE3 PC/Saturn, SEGA LZS variant) ---
# Ported from reevengi-tools depack_prs.c (Patrice Mandin)

def unpack_prs(data: bytes) -> bytes: #vers 1
    """Decompress SEGA PRS file (RE3 PC/Saturn). Returns raw bytes."""
    src = memoryview(data)
    src_pos = 0
    src_bit = 0
    cmd = 0
    out = bytearray()

    def read_bit() -> int:
        nonlocal cmd, src_bit, src_pos
        if src_bit == 0:
            cmd = src[src_pos]
            src_pos += 1
            src_bit = 8
        ret = cmd & 1
        cmd >>= 1
        src_bit -= 1
        return ret

    while src_pos < len(data):
        if read_bit():
            out.append(src[src_pos])
            src_pos += 1
            continue

        local_t = read_bit()
        if local_t:
            if src_pos + 1 >= len(data):
                break
            a = src[src_pos]; src_pos += 1
            b = src[src_pos]; src_pos += 1
            offset = ((b << 8) | a) >> 3
            amount = a & 7
            if src_pos < len(data):
                if amount == 0:
                    amount = src[src_pos] + 1
                    src_pos += 1
                else:
                    amount += 2
            start = len(out) - 0x2000 + offset
        else:
            amount = 0
            for _ in range(2):
                amount = (amount << 1) | read_bit()
            if src_pos >= len(data):
                break
            offset = src[src_pos]; src_pos += 1
            amount += 2
            start = len(out) - 0x100 + offset

        for _ in range(amount):
            out.append(out[start] if 0 <= start < len(out) else 0)
            start += 1

    return bytes(out)


# --- BSS RE2 decompressor (PS1 background mask) ---
# Ported from reevengi-tools depack_bsssld.c bsssld_depack_re2()

def unpack_bss_re2(data: bytes) -> bytes: #vers 1
    """Decompress RE2 PS1 BSS/SLD mask data. Returns raw bytes."""
    if len(data) < 6:
        return b''
    buflen = struct.unpack_from('<I', data, 0)[0]
    out = bytearray(buflen)
    src_pos = 6
    dst_pos = 0

    while src_pos < len(data) and dst_pos < buflen:
        while src_pos < len(data) and (data[src_pos] & 0x10) == 0:
            count = data[src_pos] & 0x0F
            src_offset = ((-256 | (data[src_pos] & 0xE0)) << 3) | data[src_pos + 1]
            if count == 0x0F:
                count += data[src_pos + 2]
                src_pos += 3
            else:
                src_pos += 2
            count += 3
            src = dst_pos + src_offset
            for i in range(count):
                if dst_pos < buflen and 0 <= src + i < buflen:
                    out[dst_pos] = out[src + i]
                dst_pos += 1

        if src_pos >= len(data) or data[src_pos] == 0xFF:
            break

        count = ((data[src_pos] | 0xFFE0) ^ 0xFFFF) + 1
        src_pos += 1
        if count == 0x10:
            count += data[src_pos]
            src_pos += 1

        for i in range(count):
            if dst_pos < buflen and src_pos + i < len(data):
                out[dst_pos] = data[src_pos + i]
            dst_pos += 1
        src_pos += count

    return bytes(out)


# --- BSS RE3 decompressor ---
# Ported from reevengi-tools depack_bsssld.c bsssld_depack_re3()

def unpack_bss_re3(data: bytes) -> bytes: #vers 1
    """Decompress RE3 PS1 BSS/SLD mask data. Returns raw bytes."""
    if len(data) < 4:
        return b''
    num_blocks = struct.unpack_from('<I', data, 0)[0]
    out = bytearray(65536)
    src_pos = 4
    dst_pos = 0

    for _ in range(num_blocks):
        if src_pos >= len(data):
            break
        if (data[src_pos] & 0x80) != 0:
            count = data[src_pos] & 0x7F
            src_pos += 1
            if dst_pos + count > len(out):
                out += bytearray(65536)
            out[dst_pos:dst_pos + count] = data[src_pos:src_pos + count]
            src_pos += count
            dst_pos += count
        else:
            offset = (data[src_pos] << 8) | data[src_pos + 1]
            src_pos += 2
            count = (offset >> 11) + 2
            offset &= 0x7FF
            if dst_pos + count > len(out):
                out += bytearray(65536)
            src = dst_pos - (offset + 4)
            for i in range(count):
                out[dst_pos + i] = out[src + i] if 0 <= src + i < dst_pos else 0
            dst_pos += count

    return bytes(out[:dst_pos])


# --- ROFS archive extractor (RE3 PC) ---

def list_rofs_contents(data: bytes) -> List[Dict]: #vers 1
    """List files in a RE3 PC ROFSxx.DAT archive."""
    entries = []
    if len(data) < 21:
        return entries

    # ROFS header: 5*4+1 = 21 bytes unknown header
    # Then directory entries
    off = 21
    while off + 8 < len(data):
        entry_offset = struct.unpack_from('<I', data, off)[0]
        entry_length = struct.unpack_from('<I', data, off + 4)[0]
        if entry_offset == 0 and entry_length == 0:
            break
        # Filename follows as null-terminated string
        name_start = off + 8
        name_end = data.find(b'\x00', name_start)
        if name_end < 0:
            break
        name = data[name_start:name_end].decode('ascii', errors='replace')
        entries.append({
            'name': name,
            'offset': entry_offset,
            'length': entry_length,
        })
        off = name_end + 1
        # Align to 4 bytes
        if off % 4:
            off += 4 - (off % 4)

    return entries


def extract_rofs(data: bytes, output_dir: str) -> List[str]: #vers 1
    """Extract all files from a RE3 PC ROFSxx.DAT archive."""
    os.makedirs(output_dir, exist_ok=True)
    entries = list_rofs_contents(data)
    extracted = []

    for entry in entries:
        offset = entry['offset']
        length = entry['length']
        name   = entry['name']

        if offset + length > len(data):
            continue

        file_data = data[offset:offset + length]
        out_path = os.path.join(output_dir, os.path.basename(name))

        with open(out_path, 'wb') as f:
            f.write(file_data)
        extracted.append(out_path)

    return extracted


# --- BIN archive extractor (RE2 PS1 DAT/*.BIN) ---

def list_bin_contents(data: bytes) -> List[Dict]: #vers 1
    """List files in a RE2 PS1 BIN archive."""
    entries = []
    if len(data) < 0x800:
        return entries

    # BIN header is 0x800 bytes
    # id(4) length(4) blocks1(4) unknown(52) filename(0x7C0)
    file_id     = struct.unpack_from('<I', data, 0)[0]
    file_length = struct.unpack_from('<I', data, 4)[0]
    blocks1     = struct.unpack_from('<I', data, 8)[0]

    name_bytes = data[0x40:0x800]
    name_end   = name_bytes.find(b'\x00')
    name       = name_bytes[:name_end].decode('ascii', errors='replace') if name_end >= 0 else ''

    entries.append({
        'name': name or 'data',
        'id': file_id,
        'offset': 0x800,
        'length': file_length,
        'blocks': blocks1,
    })
    return entries


def extract_bin_re2(data: bytes, output_dir: str) -> List[str]: #vers 1
    """Extract and decompress files from RE2 PS1 BIN archive."""
    os.makedirs(output_dir, exist_ok=True)
    entries = list_bin_contents(data)
    extracted = []

    for entry in entries:
        offset = entry['offset']
        length = entry['length']
        name   = entry['name'] or 'extracted'

        if offset >= len(data):
            continue

        file_data = data[offset:offset + length]

        # Check if BSS-SLD compressed
        if len(file_data) >= 6 and file_data[4:6] == b'\x00\x02':
            file_data = unpack_bss_re2(file_data)

        out_path = os.path.join(output_dir, os.path.basename(name))
        with open(out_path, 'wb') as f:
            f.write(file_data)
        extracted.append(out_path)

    return extracted


# --- High-level unpack entry point ---

def unpack_file(path: str, output_dir: str) -> Tuple[bool, str, bytes]: #vers 1
    """Auto-detect format and decompress a single file.
    Returns (success, format_name, decompressed_data).
    """
    ext = os.path.splitext(path)[1].upper()

    try:
        with open(path, 'rb') as f:
            data = f.read()
    except OSError as e:
        return False, '', b''

    if ext == '.PAK':
        return True, 'PAK (RE1 PC LZW)', unpack_pak(data)

    if ext in ('.PRS',) or (ext == '.RDT' and data[:2] == b'\x10\x00'):
        return True, 'PRS (RE3 SEGA LZS)', unpack_prs(data)

    if ext in ('.BSS', '.SLD'):
        # Try RE2 first (has 4-byte length header at offset 0)
        try:
            result = unpack_bss_re2(data)
            if result:
                return True, 'BSS/SLD RE2', result
        except Exception:
            pass
        result = unpack_bss_re3(data)
        return True, 'BSS/SLD RE3', result

    if ext == '.ADT':
        # ADT is Huffman+LZ, complex - return raw for now with note
        return True, 'ADT (RE2 PC raw)', data

    if ext == '.DAT' and os.path.basename(path).upper().startswith('ROFS'):
        entries = list_rofs_contents(data)
        return True, f'ROFS (RE3 PC archive, {len(entries)} files)', data

    if ext == '.BIN':
        entries = list_bin_contents(data)
        return True, f'BIN (RE2 PS1, {len(entries)} files)', data

    # Unknown / uncompressed
    return True, f'{ext} (no decompression)', data
