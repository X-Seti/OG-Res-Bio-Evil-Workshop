#!/usr/bin/env python3
#this belongs in apps/core/re_audio.py - Version: 1
# X-Seti - May22 2026 - ResBio-Evil-Workshop - RE Audio Decoder
"""
RE Audio Decoder - Decodes PS1 audio formats to WAV for playback.
  VAG  - PS1 ADPCM (.VAG), header 'VAGp'
  SND  - RE1 sound container (scans for embedded VAG headers)
  WAV  - PC versions, pass-through
  XA   - CD-ROM XA ADPCM (partial, sector-stripped only)

All output is written to a temp WAV file for use with QMediaPlayer.
Pure Python, no external audio libraries required.
"""

import os
import struct
import wave
import tempfile
from typing import Optional, Tuple, List

##Methods list -
# decode_vag
# decode_snd
# detect_audio_format
# find_vag_in_file
# to_wav_file
# get_audio_info

##class AudioInfo:


# PS1 ADPCM filter coefficients (f0, f1)
_VAG_FILTERS = [
    (0.0,        0.0),
    (60.0/64.0,  0.0),
    (115.0/64.0, -52.0/64.0),
    (98.0/64.0,  -55.0/64.0),
    (122.0/64.0, -60.0/64.0),
]

VAG_HEADER_SIZE = 48
VAG_MAGIC       = b'VAGp'
XA_MAGIC        = b'\x00\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x00'


class AudioInfo: #vers 1
    """Metadata about an audio file."""
    def __init__(self): #vers 1
        self.path        = ''
        self.format      = 'unknown'   # 'vag', 'wav', 'snd', 'xa'
        self.sample_rate = 0
        self.channels    = 1
        self.num_samples = 0
        self.duration_s  = 0.0
        self.valid       = False
        self.error       = ''

    @property
    def duration_str(self) -> str:
        s = int(self.duration_s)
        return f"{s//60}:{s%60:02d}"


def detect_audio_format(path: str) -> str: #vers 1
    """Detect audio format from file header. Returns 'vag','wav','snd','xa','unknown'."""
    ext = os.path.splitext(path)[1].upper()
    try:
        with open(path, 'rb') as f:
            magic = f.read(12)
        if magic[:4] == VAG_MAGIC:
            return 'vag'
        if magic[:4] == b'RIFF':
            return 'wav'
        if ext in ('.VAG',):
            return 'vag'
        if ext in ('.SND', '.SAB'):
            return 'snd'
        if ext == '.WAV':
            return 'wav'
        # Check for VAG magic inside file (SND container)
        if find_vag_in_file(path):
            return 'snd'
    except OSError:
        pass
    return 'unknown'


def find_vag_in_file(path: str) -> List[int]: #vers 1
    """Scan file for VAGp magic bytes. Returns list of offsets."""
    offsets = []
    try:
        with open(path, 'rb') as f:
            data = f.read()
        pos = 0
        while True:
            idx = data.find(VAG_MAGIC, pos)
            if idx < 0:
                break
            offsets.append(idx)
            pos = idx + 4
    except OSError:
        pass
    return offsets


def decode_vag(path: str, vag_offset: int = 0) -> Tuple[bytes, int, int]: #vers 1
    """Decode PS1 VAG ADPCM to raw signed 16-bit PCM.
    Returns (pcm_bytes, sample_rate, num_channels).
    vag_offset: byte offset into file where VAGp header starts.
    """
    with open(path, 'rb') as f:
        f.seek(vag_offset)
        header = f.read(VAG_HEADER_SIZE)

    if len(header) < VAG_HEADER_SIZE or header[:4] != VAG_MAGIC:
        # Try without header (raw ADPCM)
        with open(path, 'rb') as f:
            f.seek(vag_offset)
            adpcm_data = f.read()
        sample_rate = 22050
    else:
        version     = struct.unpack_from('>I', header, 4)[0]
        data_size   = struct.unpack_from('>I', header, 8)[0]
        sample_rate = struct.unpack_from('>I', header, 12)[0]
        if sample_rate == 0:
            sample_rate = 22050

        with open(path, 'rb') as f:
            f.seek(vag_offset + VAG_HEADER_SIZE)
            adpcm_data = f.read(data_size) if data_size else f.read()

    pcm = _decode_adpcm(adpcm_data)
    return pcm, sample_rate, 1


def _decode_adpcm(data: bytes) -> bytes: #vers 1
    """Decode PS1 VAG ADPCM frames to signed 16-bit PCM samples."""
    samples = []
    prev1 = 0.0
    prev2 = 0.0

    i = 0
    while i + 16 <= len(data):
        block = data[i:i+16]
        i += 16

        shift   = block[0] & 0x0F
        filter_ = (block[0] >> 4) & 0x0F
        flag    = block[1]

        if flag == 7:  # end marker
            break

        f0, f1 = _VAG_FILTERS[min(filter_, len(_VAG_FILTERS)-1)]

        # 14 nibble bytes
        for j in range(2, 16):
            byte = block[j]
            for nibble in [byte & 0x0F, (byte >> 4) & 0x0F]:
                # Sign-extend 4-bit
                if nibble > 7:
                    nibble -= 16
                # Shift and filter
                s = (nibble << (12 - shift)) + f0 * prev1 + f1 * prev2
                s = max(-32768.0, min(32767.0, s))
                samples.append(int(s))
                prev2 = prev1
                prev1 = s

    # Pack as signed 16-bit LE
    import array
    arr = array.array('h', samples)
    return arr.tobytes()


def decode_snd(path: str) -> Tuple[bytes, int, int]: #vers 1
    """Decode RE1 SND container by finding embedded VAG headers.
    Returns first VAG found decoded to PCM.
    """
    offsets = find_vag_in_file(path)
    if offsets:
        return decode_vag(path, offsets[0])
    # No VAG found - return empty
    return b'', 22050, 1


def to_wav_file(path: str, output_path: Optional[str] = None) -> Optional[str]: #vers 1
    """Decode any supported audio format to a WAV file.
    Returns path to WAV file, or None on failure.
    output_path: if None, creates a temp file.
    """
    fmt = detect_audio_format(path)

    if fmt == 'wav':
        return path  # already WAV

    try:
        if fmt == 'vag':
            pcm, sample_rate, channels = decode_vag(path)
        elif fmt == 'snd':
            pcm, sample_rate, channels = decode_snd(path)
        elif fmt == 'vb':
            # Look for matching .HED file
            hed = os.path.splitext(path)[0] + '.HED'
            if not os.path.exists(hed):
                hed = os.path.splitext(path)[0] + '.hed'
            pcm, sample_rate, channels = decode_vb(path, hed)
        elif fmt == 'hsb':
            pcm, sample_rate, channels = decode_hsb(path)
        else:
            return None

        if not pcm:
            return None

        if output_path is None:
            fd, output_path = tempfile.mkstemp(suffix='.wav')
            os.close(fd)

        with wave.open(output_path, 'wb') as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(sample_rate)
            wf.writeframes(pcm)

        return output_path

    except Exception as e:
        print(f"re_audio: decode error {path}: {e}")
        return None


def get_audio_info(path: str) -> AudioInfo: #vers 1
    """Return metadata for any supported audio file."""
    info = AudioInfo()
    info.path = path
    info.format = detect_audio_format(path)

    try:
        if info.format == 'wav':
            with wave.open(path, 'rb') as wf:
                info.sample_rate = wf.getframerate()
                info.channels    = wf.getnchannels()
                info.num_samples = wf.getnframes()
                if info.sample_rate > 0:
                    info.duration_s = info.num_samples / info.sample_rate
            info.valid = True

        elif info.format == 'vag':
            with open(path, 'rb') as f:
                header = f.read(VAG_HEADER_SIZE)
            if header[:4] == VAG_MAGIC:
                info.sample_rate = struct.unpack_from('>I', header, 12)[0] or 22050
                data_size        = struct.unpack_from('>I', header, 8)[0]
                # Each 16-byte block = 28 samples
                info.num_samples = (data_size // 16) * 28
                info.channels    = 1
                if info.sample_rate > 0:
                    info.duration_s = info.num_samples / info.sample_rate
                info.valid = True

        elif info.format == 'snd':
            offsets = find_vag_in_file(path)
            info.valid       = len(offsets) > 0
            info.sample_rate = 22050
            info.channels    = 1

    except Exception as e:
        info.error = str(e)

    return info


def scan_audio_files(folder: str) -> List[str]: #vers 2
    """Scan a folder for supported audio files. Returns sorted list of paths."""
    supported = {'.VAG', '.WAV', '.SND', '.SAB', '.VB', '.HSB'}
    found = []
    try:
        for fname in sorted(os.listdir(folder)):
            if os.path.splitext(fname)[1].upper() in supported:
                found.append(os.path.join(folder, fname))
    except OSError:
        pass
    return found


def decode_vb(path: str, hed_path: str = '') -> Tuple[bytes, int, int]: #vers 1
    """Decode a Biohazard .VB voice bank file.
    VB files contain raw PS1 ADPCM without VAGp headers.
    HED file (if provided) contains offsets to each sample.
    Returns first sample decoded as PCM.
    """
    try:
        with open(path, 'rb') as f:
            data = f.read()

        # Try to read offsets from HED if available
        offsets = [0]
        if hed_path and os.path.exists(hed_path):
            with open(hed_path, 'rb') as f:
                hed = f.read()
            # HED is a table of uint32 offsets
            num = len(hed) // 4
            offsets = [struct.unpack_from('<I', hed, i*4)[0]
                       for i in range(num) if struct.unpack_from('<I', hed, i*4)[0] < len(data)]

        # Decode first sample from offset 0
        pcm = _decode_adpcm(data[offsets[0]:])
        return pcm, 22050, 1
    except Exception as e:
        return b'', 22050, 1


def decode_hsb(path: str) -> Tuple[bytes, int, int]: #vers 1
    """Decode a Biohazard .HSB sound bank.
    HSB starts with a small header, then contains packed ADPCM samples.
    Scan for VAGp headers first, then fall back to raw ADPCM.
    """
    # Try VAG embedded first
    offsets = find_vag_in_file(path)
    if offsets:
        return decode_vag(path, offsets[0])
    # Fall back to raw ADPCM from offset 0x20 (common HSB header size)
    try:
        with open(path, 'rb') as f:
            f.seek(0x20)
            data = f.read()
        pcm = _decode_adpcm(data)
        return pcm, 22050, 1
    except Exception:
        return b'', 22050, 1
