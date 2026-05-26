#!/usr/bin/env python3
#this belongs in apps/core/depack_adt.py - Version: 1
# X-Seti - May26 2026 - ResBio-Evil-Workshop - ADT Decompressor
"""
ADT file depacker for RE2 PC backgrounds.
Python port of depack_adt.cpp by Patrice Mandin (GPL v2+).
Source: https://github.com/Gemini-Loboto3/RE2-Mod-tools

ADT = Adaptive Delta Transform - a Huffman+LZ77 compressed format
used for background images in RE2 PC. Each .ADT file contains
one room background (320x240 pixels, 16bpp RGB555).

The decompressed data is raw 16bpp pixels arranged as:
  - 256x256 block  (top-left and top-right of screen)
  - 128x128 block  (bottom portion, split as two 64x128 chunks)
Total decompressed = 256*256*2 + 128*128*2 = 163840 bytes

adt_depack(data)      -> bytes (raw 16bpp pixels)
adt_to_rgba(data)     -> bytes (RGBA8888 320x240)
load_adt(path)        -> Optional[Tuple[bytes, int, int]]
"""

from typing import Optional, Tuple

##Methods list -
# adt_depack
# adt_to_rgba
# load_adt

##class _BitReader:
##class _ADTDecoder:


class _BitReader: #vers 1
    """Read individual bits and multi-bit values from a byte buffer."""

    def __init__(self, data: bytes, pos: int = 0): #vers 1
        self._data   = data
        self._pos    = pos
        self._byte   = 0
        self._nbits  = 0  # valid bits remaining in _byte

    def read_one_bit(self) -> int: #vers 1
        self._nbits -= 1
        if self._nbits < 0:
            self._nbits = 7
            self._byte  = self._data[self._pos] if self._pos < len(self._data) else 0
            self._pos  += 1
        return (self._byte >> self._nbits) & 1

    def read_bits(self, n: int) -> int: #vers 1
        """Read n bits, MSB first."""
        or_mask   = 0
        final_val = self._byte
        while n > self._nbits:
            n        -= self._nbits
            and_mask  = (1 << self._nbits) - 1
            and_mask &= final_val
            and_mask <<= n
            self._byte   = self._data[self._pos] if self._pos < len(self._data) else 0
            self._pos   += 1
            final_val    = self._byte
            self._nbits  = 8
            or_mask     |= and_mask
        self._nbits  -= n
        final_val   >>= self._nbits
        return (final_val & ((1 << n) - 1)) | or_mask

    def read_bitfield(self) -> int: #vers 1
        """Read variable-length Elias gamma-like code."""
        num_zeros = 0
        value     = 1
        while self.read_one_bit() == 0:
            num_zeros += 1
        while num_zeros > 0:
            value     = self.read_one_bit() + (value << 1)
            num_zeros -= 1
        return value

    @property
    def pos(self) -> int:
        return self._pos


class _ADTDecoder: #vers 1
    """Internal Huffman tree decoder for ADT blocks."""

    def __init__(self, start: int, length: int): #vers 1
        self.start  = start
        self.length = length
        # Huffman tree: nodes[i] = [left, right]
        self.tree   = [[-1, -1] for _ in range(length * 2 + 2)]
        self.ptr8   = [[0, 0] for _ in range(length)]  # [start, length]
        self.ptr4   = [0] * length

    def init_data(self): #vers 1
        for i in range(self.length):
            self.ptr4[i] = 0
            self.ptr8[i] = [0, 0]
            self.tree[i] = [-1, -1]
        for i in range(self.length, self.length * 2 + 2):
            self.tree[i] = [-1, -1]

    def build_huffman(self, freq: list) -> int: #vers 1
        """Build Huffman start codes from frequency array (like initUnpackBlockArray)."""
        tmp = [0] * 18
        for i in range(16):
            tmp[i + 2] = (tmp[i + 1] + freq[i + 1]) << 1
        for i in range(18):
            for j in range(self.length):
                if self.ptr8[j][1] == i:
                    self.ptr8[j][0] = tmp[i] & 0xFFFF
                    tmp[i] += 1
        return 0

    def build_tree(self) -> int: #vers 1
        """Build binary tree from code lengths (like initUnpackBlockArray2)."""
        cur_len   = self.length
        cur_idx   = self.length + 1
        self.tree[self.length] = [-1, -1]
        self.tree[cur_idx]     = [-1, -1]

        for i in range(self.length):
            code_start  = self.ptr8[i][0]
            code_length = self.ptr8[i][1]
            cur_len     = self.length

            for j in range(code_length):
                mask   = 1 << (code_length - j - 1)
                branch = 1 if (mask & code_start) else 0
                if j + 1 == code_length:
                    self.tree[cur_len][branch] = i
                    break
                if self.tree[cur_len][branch] == -1:
                    self.tree[cur_len][branch] = cur_idx
                    self.tree[cur_idx]         = [-1, -1]
                    cur_len                    = cur_idx
                    cur_idx                   += 1
                else:
                    cur_len = self.tree[cur_len][branch]
        return self.length

    def decode_symbol(self, br: _BitReader, root: int) -> int: #vers 1
        """Decode one symbol by walking the Huffman tree."""
        cur = root
        while cur >= self.length:
            bit = br.read_one_bit()
            cur = self.tree[cur][bit]
        return cur


def _read_block_header(br: _BitReader,
                       d1: _ADTDecoder, d2: _ADTDecoder,
                       d3: _ADTDecoder) -> None: #vers 1
    """Read one block's Huffman table definitions (like initUnpackBlock)."""
    # Array 1: direct delta-coded lengths
    prev = 0
    for i in range(d1.length):
        if br.read_one_bit():
            d1.ptr8[i][1] = br.read_bitfield() ^ prev
        else:
            d1.ptr8[i][1] = prev
        prev = d1.ptr8[i][1]

    freq = [0] * 17
    for i in range(d1.length):
        v = d1.ptr8[i][1]
        if v <= 16:
            freq[v] += 1
    d1.build_huffman(freq)
    root1 = d1.build_tree()

    # Array 2: run-length + Huffman coded lengths
    tmp  = [0] * d2.length
    bit  = br.read_one_bit()
    j    = 0
    while j < d2.length:
        if bit:
            run = br.read_bitfield()
            for _ in range(run):
                if j < d2.length:
                    tmp[j] = d2.decode_symbol(br, root1)
                    j += 1
            bit = 0
        else:
            run = br.read_bitfield()
            for _ in range(run):
                if j < d2.length:
                    tmp[j] = 0
                    j += 1
            bit = 1

    xor_val = 0
    for i in range(d2.length):
        xor_val         ^= tmp[i]
        d2.ptr8[i][1]    = xor_val

    freq = [0] * 17
    for i in range(d2.length):
        v = d2.ptr8[i][1]
        if v <= 16:
            freq[v] += 1
    d2.build_huffman(freq)
    # don't call build_tree yet - caller does it

    # Array 3: direct delta-coded lengths
    prev = 0
    for i in range(d3.length):
        if br.read_one_bit():
            d3.ptr8[i][1] = br.read_bitfield() ^ prev
        else:
            d3.ptr8[i][1] = prev
        prev = d3.ptr8[i][1]

    freq = [0] * 17
    for i in range(d3.length):
        v = d3.ptr8[i][1]
        if v <= 16:
            freq[v] += 1
    d3.build_huffman(freq)


def adt_depack(data: bytes) -> Optional[bytes]: #vers 1
    """Depack an ADT compressed buffer. Returns raw 16bpp pixels or None."""
    try:
        if len(data) < 8:
            return None

        # Skip first 4 bytes (archive offset, handled by caller)
        br = _BitReader(data, 4)

        d1 = _ADTDecoder(8, 16)
        d2 = _ADTDecoder(8, 512)
        d3 = _ADTDecoder(8, 16)
        d1.init_data()
        d2.init_data()
        d3.init_data()

        tmp16k   = bytearray(16384)
        tmp16off = 0
        dst      = bytearray()

        block_len = br.read_bits(8) | (br.read_bits(8) << 8)
        while block_len > 0:
            _read_block_header(br, d1, d2, d3)
            root2 = d2.build_tree()
            root3 = d3.build_tree()

            cur = 0
            while cur < block_len:
                sym = d2.decode_symbol(br, root2)
                if sym < 256:
                    dst.append(sym)
                    tmp16k[tmp16off] = sym
                    tmp16off         = (tmp16off + 1) & 0x3FFF
                else:
                    num_vals  = sym - 0xFD
                    back_sym  = d3.decode_symbol(br, root3)
                    if back_sym != 0:
                        nb        = back_sym - 1
                        back_sym  = br.read_bits(nb) & 0xFFFF
                        back_sym += 1 << nb
                    start_off = (tmp16off - back_sym - 1) & 0x3FFF
                    for _ in range(num_vals):
                        b = tmp16k[start_off]
                        dst.append(b)
                        tmp16k[tmp16off] = b
                        tmp16off         = (tmp16off + 1) & 0x3FFF
                        start_off        = (start_off  + 1) & 0x3FFF
                cur += 1

            d1.init_data()
            d2.init_data()
            d3.init_data()
            block_len = br.read_bits(8) | (br.read_bits(8) << 8)

        return bytes(dst)
    except Exception as e:
        print(f"ADT depack error: {e}")
        return None


def adt_to_rgba(raw: bytes) -> Optional[Tuple[bytes, int, int]]: #vers 1
    """Convert depacked ADT raw pixels to RGBA8888 320x240.

    ADT pixel layout (from adt_surface in depack_adt.cpp):
      - 256x256 block at offset 0  -> blit to output (0,0)-(256,256)
      - 128x128 block at offset 256*256*2 -> split as:
          left 64x128  -> output (256,0)-(320,128)
          right 64x128 -> output (256,128)-(320,256)  [y clipped to 240]
    """
    expected = 256 * 256 * 2 + 128 * 128 * 2
    if not raw or len(raw) < expected:
        return None

    W, H = 320, 240
    rgba = bytearray(W * H * 4)

    def rgb555_to_rgba(word: int) -> tuple:
        r = ((word >>  0) & 0x1F) << 3
        g = ((word >>  5) & 0x1F) << 3
        b = ((word >> 10) & 0x1F) << 3
        return r | (r >> 5), g | (g >> 5), b | (b >> 5), 255

    def put_pixel(x: int, y: int, r: int, g: int, b: int, a: int):
        if 0 <= x < W and 0 <= y < H:
            off = (y * W + x) * 4
            rgba[off] = r; rgba[off+1] = g; rgba[off+2] = b; rgba[off+3] = a

    import struct
    # Block 1: 256x256
    off1 = 0
    for py in range(256):
        for px in range(256):
            word = struct.unpack_from('<H', raw, off1)[0]
            off1 += 2
            put_pixel(px, py, *rgb555_to_rgba(word))

    # Block 2: 128x128, split into two 64x128 halves
    off2 = 256 * 256 * 2
    # Left half: source (0,0)-(64,128) -> output (256,0)-(320,128)
    for py in range(128):
        for px in range(64):
            word = struct.unpack_from('<H', raw, off2 + (py * 128 + px) * 2)[0]
            put_pixel(256 + px, py, *rgb555_to_rgba(word))
    # Right half: source (64,0)-(128,128) -> output (256,128)-(320,240)
    for py in range(128):
        for px in range(64):
            word = struct.unpack_from('<H', raw, off2 + (py * 128 + 64 + px) * 2)[0]
            put_pixel(256 + px, 128 + py, *rgb555_to_rgba(word))

    return bytes(rgba), W, H


def load_adt(path: str) -> Optional[Tuple[bytes, int, int]]: #vers 1
    """Load and decode an ADT background file.
    Returns (rgba_bytes, width, height) or None.
    """
    try:
        with open(path, 'rb') as f:
            data = f.read()
        raw = adt_depack(data)
        if not raw:
            return None
        return adt_to_rgba(raw)
    except Exception as e:
        print(f"ADT load error {path}: {e}")
        return None
