#!/usr/bin/env python3
#this belongs in apps/core/mdec_decoder.py - Version: 1
# X-Seti - May22 2026 - ResBio-Evil-Workshop - PS1 MDEC Decoder
"""
PS1 MDEC (Motion DECoder) - pure Python port of reevengi-tools depack_mdec.c
Original: Patrice Mandin, Bero, Psxdev project (GPL v2+)

Decodes PS1 BS (Bit Stream) compressed images to RGB888.
Used for RE1/RE2/RE3 BSS background files.

Algorithm:
  1. Read VLC (variable-length codes) Huffman-compressed DCT coefficients
  2. Run IDCT on 8x8 macroblocks (Cb, Cr, Y1, Y2, Y3, Y4)
  3. Convert YCbCr -> RGB
  4. Assemble 16x16 macroblocks into final image
"""

import struct
import math
from typing import Optional, Tuple

##Methods list -
# decode_bs
# decode_bss_background
# _decode_macroblock
# _idct_block
# _vlc_decode
# _ycbcr_to_rgb

# --- Constants (from depack_mdec.c) ---

_DCTSIZE = 8
_DCTSIZE2 = 64
_VLC_ID  = 0x3800
_EOB     = 0xFE00
_SHIFT   = 12

def _to_fix(a: float) -> int:
    return int(a * (1 << _SHIFT))

def _to_int(a: int) -> int:
    return a >> _SHIFT

_MULR  = lambda a: _to_int(a * _to_fix(1.402))
_MULG  = lambda a: _to_int(a * _to_fix(-0.3437))
_MULG2 = lambda a: _to_int(a * _to_fix(-0.7143))
_MULB  = lambda a: _to_int(a * _to_fix(1.772))

# AAN DCT scales (precomputed * 2^14)
_AAN_SCALES = [
    16384, 22725, 21407, 19266, 16384, 12873,  8867,  4520,
    22725, 31521, 29692, 26722, 22725, 17855, 12299,  6270,
    21407, 29692, 27969, 25172, 21407, 16819, 11585,  5906,
    19266, 26722, 25172, 22654, 19266, 15137, 10426,  5315,
    16384, 22725, 21407, 19266, 16384, 12873,  8867,  4520,
    12873, 17855, 16819, 15137, 12873, 10114,  6967,  3552,
     8867, 12299, 11585, 10426,  8867,  6967,  4799,  2446,
     4520,  6270,  5906,  5315,  4520,  3552,  2446,  1247,
]

# Zigzag scan order
_ZSCAN = [
     0,  1,  8, 16,  9,  2,  3, 10,
    17, 24, 32, 25, 18, 11,  4,  5,
    12, 19, 26, 33, 40, 48, 41, 34,
    27, 20, 13,  6,  7, 14, 21, 28,
    35, 42, 49, 56, 57, 50, 43, 36,
    29, 22, 15, 23, 30, 37, 44, 51,
    58, 59, 52, 45, 38, 31, 39, 46,
    53, 60, 61, 54, 47, 55, 62, 63,
]

# Quantisation table
_IQTAB = [
     2, 16, 19, 22, 26, 27, 29, 34,
    16, 16, 22, 24, 27, 29, 34, 37,
    19, 22, 26, 27, 29, 34, 34, 38,
    22, 22, 26, 27, 29, 34, 37, 40,
    22, 26, 27, 29, 32, 35, 40, 48,
    26, 27, 29, 32, 35, 40, 48, 58,
    26, 27, 29, 34, 38, 46, 56, 69,
    27, 29, 35, 38, 46, 56, 69, 83,
]

# Round table: maps -256..255 + 256 offset
_ROUND_TABLE = [max(0, min(255, i)) for i in range(-256, 512)]


class _BitReader:
    """Read bits from a byte buffer."""

    def __init__(self, data: bytes): #vers 1
        self._data = data
        self._pos = 0
        self._bits = 0
        self._nbits = 0

    def read_bits(self, n: int) -> int: #vers 1
        while self._nbits < n:
            if self._pos >= len(self._data):
                return 0
            self._bits = (self._bits << 8) | self._data[self._pos]
            self._pos += 1
            self._nbits += 8
        self._nbits -= n
        return (self._bits >> self._nbits) & ((1 << n) - 1)

    def read_u16(self) -> int: #vers 1
        """Read next 16-bit little-endian word."""
        if self._pos + 2 > len(self._data):
            return 0
        val = struct.unpack_from('<H', self._data, self._pos)[0]
        self._pos += 2
        self._nbits = 0
        self._bits = 0
        return val

    @property
    def pos(self) -> int:
        return self._pos


def _idct_row(blk: list, off: int): #vers 1
    """1D IDCT on a row of 8 values in place."""
    # Fast 1D IDCT (AAN algorithm)
    s = blk
    o = off

    d0 = s[o+0] + s[o+4]
    d1 = s[o+0] - s[o+4]
    d2 = (s[o+2] >> 1) - s[o+6]
    d3 = s[o+2] + (s[o+6] >> 1)

    tmp0 = d0 + d3
    tmp1 = d1 + d2
    tmp2 = d1 - d2
    tmp3 = d0 - d3

    d4 = s[o+5] - s[o+3] - s[o+7] - (s[o+7] >> 1)
    d5 = s[o+1] + s[o+7] - s[o+3] - (s[o+3] >> 1)
    d6 = s[o+7] - s[o+1] + s[o+5] + (s[o+5] >> 1)
    d7 = s[o+3] + s[o+5] + s[o+1] + (s[o+1] >> 1)

    tmp4 = d7 + d4
    tmp5 = d6 + d5
    tmp6 = d6 - d5
    tmp7 = d7 - d4

    tmp6a = (tmp6 * 181 + 128) >> 8
    tmp7a = (tmp7 * 181 + 128) >> 8
    tmp4a = tmp4 + tmp6a
    tmp5a = tmp5 + tmp7a
    tmp6b = tmp4 - tmp6a
    tmp7b = tmp5 - tmp7a

    s[o+0] = tmp0 + tmp5a
    s[o+1] = tmp1 + tmp4a
    s[o+2] = tmp2 + tmp7b
    s[o+3] = tmp3 + tmp6b
    s[o+4] = tmp3 - tmp6b
    s[o+5] = tmp2 - tmp7b
    s[o+6] = tmp1 - tmp4a
    s[o+7] = tmp0 - tmp5a


def _idct_block(blk: list) -> list: #vers 1
    """Full 8x8 IDCT. blk is 64 ints, returns 64 ints."""
    result = list(blk)
    # Row IDCT
    for i in range(8):
        _idct_row(result, i * 8)
    # Column IDCT (transpose, row, transpose)
    for x in range(8):
        col = [result[x + y*8] for y in range(8)]
        _idct_row(col, 0)
        for y in range(8):
            result[x + y*8] = col[y]
    return result


def _vlc_decode(reader: _BitReader, iqscale: int,
                block: list, is_chroma: bool) -> bool: #vers 1
    """Decode one 8x8 DCT block via VLC. Fills block[64]."""
    for i in range(64):
        block[i] = 0

    # Read quantized DC coefficient
    val = reader.read_u16()
    if val == _VLC_ID:
        return False  # end of stream marker

    # DC
    dc = val & 0x3FF
    if dc & 0x200:
        dc |= ~0x3FF
    block[0] = (dc * iqscale * _IQTAB[0]) >> 3

    # AC coefficients
    k = 0
    while True:
        val = reader.read_u16()
        if val == _EOB:
            break
        if val == 0:
            break

        run  = (val >> 10) & 0x3F
        coef = val & 0x3FF
        if coef & 0x200:
            coef |= ~0x3FF

        k += run + 1
        if k >= 64:
            break

        zk = _ZSCAN[k]
        block[zk] = (coef * iqscale * _IQTAB[zk]) >> 3

    # Dequantize with AAN scales
    for i in range(64):
        block[i] = (block[i] * _AAN_SCALES[i]) >> 14

    return True


def _ycbcr_to_rgb(y: int, cb: int, cr: int) -> Tuple[int, int, int]: #vers 1
    """Convert YCbCr to RGB8. y/cb/cr are -128..127."""
    r = _ROUND_TABLE[y + _MULR(cr) + 256]
    g = _ROUND_TABLE[y + _MULG(cb) + _MULG2(cr) + 256]
    b = _ROUND_TABLE[y + _MULB(cb) + 256]
    return r, g, b


def decode_bs(data: bytes, width: int, height: int) -> Optional[bytes]: #vers 1
    """Decode a PS1 BS (bit stream) MDEC image.
    Returns RGBA bytes (width*height*4) or None on failure.
    """
    try:
        return _decode_bs_impl(data, width, height)
    except Exception as e:
        print(f"MDEC decode error: {e}")
        return None


def _decode_bs_impl(data: bytes, width: int, height: int) -> bytes: #vers 1
    """Internal BS decoder implementation."""
    # BS header: version(2) + zero(2) + length(4) + iqscale(2) + version2(2)
    if len(data) < 8:
        raise ValueError("BS data too small")

    version  = struct.unpack_from('<H', data, 0)[0]
    iqscale  = struct.unpack_from('<H', data, 4)[0] if len(data) >= 6 else 8
    bs_start = 8  # skip 8-byte header

    reader = _BitReader(data[bs_start:])

    out = bytearray(width * height * 4)

    mb_w = (width  + 15) // 16
    mb_h = (height + 15) // 16

    cb_blk = [0] * 64
    cr_blk = [0] * 64
    y1_blk = [0] * 64
    y2_blk = [0] * 64
    y3_blk = [0] * 64
    y4_blk = [0] * 64

    for mby in range(mb_h):
        for mbx in range(mb_w):
            # Decode 6 blocks: Cr, Cb, Y1, Y2, Y3, Y4
            if not _vlc_decode(reader, iqscale, cr_blk, True):
                break
            if not _vlc_decode(reader, iqscale, cb_blk, True):
                break
            _vlc_decode(reader, iqscale, y1_blk, False)
            _vlc_decode(reader, iqscale, y2_blk, False)
            _vlc_decode(reader, iqscale, y3_blk, False)
            _vlc_decode(reader, iqscale, y4_blk, False)

            # IDCT
            cr = _idct_block(cr_blk)
            cb = _idct_block(cb_blk)
            y1 = _idct_block(y1_blk)
            y2 = _idct_block(y2_blk)
            y3 = _idct_block(y3_blk)
            y4 = _idct_block(y4_blk)

            # Assemble 16x16 macroblock into output
            # Y blocks: y1=top-left, y2=top-right, y3=bottom-left, y4=bottom-right
            # Cb/Cr blocks are half-resolution (subsampled 2x2)
            for py in range(16):
                for px in range(16):
                    out_x = mbx * 16 + px
                    out_y = mby * 16 + py
                    if out_x >= width or out_y >= height:
                        continue

                    # Select Y block and pixel within it
                    if py < 8 and px < 8:
                        yval = y1[py * 8 + px]
                        y_blk_idx = py * 8 + px
                    elif py < 8:
                        yval = y2[py * 8 + (px - 8)]
                        y_blk_idx = py * 8 + (px - 8)
                    elif px < 8:
                        yval = y3[(py - 8) * 8 + px]
                        y_blk_idx = (py - 8) * 8 + px
                    else:
                        yval = y4[(py - 8) * 8 + (px - 8)]
                        y_blk_idx = (py - 8) * 8 + (px - 8)

                    # Cb/Cr are subsampled: use (py//2, px//2)
                    c_idx = (py // 2) * 8 + (px // 2)
                    cbval = cb[c_idx]
                    crval = cr[c_idx]

                    r, g, b = _ycbcr_to_rgb(yval, cbval, crval)

                    off = (out_y * width + out_x) * 4
                    out[off]   = r
                    out[off+1] = g
                    out[off+2] = b
                    out[off+3] = 255

    return bytes(out)


def decode_bss_background(path: str) -> Optional[Tuple[bytes, int, int]]: #vers 2
    """Decode a RE BSS background file (PS1 MDEC/BS frames).

    BSS format: N × 0x10000-byte frames (one per camera angle).
    Each frame: quant_scale(2) + 0x3800(2) + num_words(4) + BS bitstream.
    Decodes to 320×240 RGBA using ffmpeg mdec codec.

    Returns list of (rgba_bytes, 320, 240) tuples — one per camera.
    First tuple returned directly for single-frame compatibility.
    """
    import subprocess, struct, os, tempfile

    try:
        with open(path, 'rb') as f:
            data = f.read()
    except Exception as e:
        print(f"BSS load error {path}: {e}")
        return None

    FRAME_SIZE = 0x10000
    if len(data) < FRAME_SIZE:
        # Try treating whole file as one frame
        frames_data = [data]
    else:
        frames_data = [data[i*FRAME_SIZE:(i+1)*FRAME_SIZE]
                       for i in range(len(data) // FRAME_SIZE)]

    results = []
    tmp_dir = tempfile.mkdtemp()

    try:
        for i, frame in enumerate(frames_data):
            # Validate BS frame header
            if len(frame) < 8:
                continue
            ver = struct.unpack_from('<H', frame, 2)[0]
            if ver != 0x3800:
                continue

            tmp_in  = os.path.join(tmp_dir, f'frame_{i}.bs')
            tmp_out = os.path.join(tmp_dir, f'frame_{i}.ppm')

            with open(tmp_in, 'wb') as f:
                f.write(frame)

            result = subprocess.run([
                'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
                '-f', 'image2', '-vcodec', 'mdec', '-s', '320x240',
                '-i', tmp_in, tmp_out
            ], capture_output=True, timeout=10)

            if result.returncode == 0 and os.path.exists(tmp_out):
                # Parse PPM → RGBA
                rgba = _ppm_to_rgba(tmp_out)
                if rgba:
                    results.append((rgba, 320, 240))

    except Exception as e:
        print(f"BSS decode error: {e}")
    finally:
        import shutil
        shutil.rmtree(tmp_dir, ignore_errors=True)

    if not results:
        return None
    # Return first frame (backward compat), store all on second call
    return results[0]


def decode_bss_all_frames(path: str) -> list: #vers 1
    """Decode all camera frames from a BSS file.
    Returns list of (rgba_bytes, 320, 240) tuples.
    """
    import subprocess, struct, os, tempfile

    results = []
    try:
        with open(path, 'rb') as f:
            data = f.read()
    except Exception as e:
        print(f"BSS load error {path}: {e}")
        return results

    FRAME_SIZE = 0x10000
    frames_data = [data[i*FRAME_SIZE:(i+1)*FRAME_SIZE]
                   for i in range(len(data) // FRAME_SIZE)]
    tmp_dir = tempfile.mkdtemp()
    try:
        for i, frame in enumerate(frames_data):
            if len(frame) < 8: continue
            ver = struct.unpack_from('<H', frame, 2)[0]
            if ver != 0x3800: continue

            tmp_in  = os.path.join(tmp_dir, f'f{i}.bs')
            tmp_out = os.path.join(tmp_dir, f'f{i}.ppm')
            with open(tmp_in, 'wb') as f:
                f.write(frame)
            r = subprocess.run([
                'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
                '-f', 'image2', '-vcodec', 'mdec', '-s', '320x240',
                '-i', tmp_in, tmp_out
            ], capture_output=True, timeout=10)
            if r.returncode == 0 and os.path.exists(tmp_out):
                rgba = _ppm_to_rgba(tmp_out)
                if rgba:
                    results.append((rgba, 320, 240))
    finally:
        import shutil
        shutil.rmtree(tmp_dir, ignore_errors=True)
    return results


def _ppm_to_rgba(path: str) -> Optional[bytes]: #vers 1
    """Read a PPM file and return RGBA bytes."""
    try:
        with open(path, 'rb') as f:
            raw = f.read()
        # Parse PPM header: P6\nW H\n255\n<pixels>
        lines = raw.split(b'\n', 3)
        if lines[0] != b'P6': return None
        w, h = map(int, lines[1].split())
        pixels = lines[3]  # RGB bytes
        rgba = bytearray(w * h * 4)
        for i in range(w * h):
            rgba[i*4]   = pixels[i*3]
            rgba[i*4+1] = pixels[i*3+1]
            rgba[i*4+2] = pixels[i*3+2]
            rgba[i*4+3] = 255
        return bytes(rgba)
    except Exception as e:
        print(f"PPM parse error {path}: {e}")
        return None


