#!/usr/bin/env python3
#this belongs in apps/core/disc_image.py - Version: 1
# X-Seti - May22 2026 - ResBio-Evil-Workshop - Disc Image Handler
"""
Disc Image Handler - Read and write PS1 CD image formats:
  ISO          - standard ISO9660, read/write via pycdlib
  BIN/CUE      - CDRWin raw sectors, read only
  CCD/IMG/SUB  - CloneCD raw sectors, read only
  7z/RAR/ZIP   - compressed archives containing the above

Provides:
  - open_disc()         detect format and mount
  - list_files()        walk ISO9660 filesystem
  - extract_file()      pull a single file out by path
  - extract_all()       dump entire filesystem to a folder
  - build_iso()         create a new ISO from a folder tree
  - detect_format()     return format string without opening
"""

import os
import io
import struct
import zipfile
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict, Iterator
from enum import Enum

##Methods list -
# detect_format
# open_disc
# build_iso

##class DiscFormat:
##class DiscFile:
##class DiscImage:
##class RawSectorReader:
##class ISOImage:
##class BinCueImage:
##class CcdImgImage:


class DiscFormat(Enum): #vers 1
    UNKNOWN = "Unknown"
    ISO     = "ISO9660 (.iso)"
    BIN_CUE = "BIN/CUE (CDRWin)"
    CCD_IMG = "CCD/IMG/SUB (CloneCD)"
    ARCHIVE_7Z  = "7-Zip Archive"
    ARCHIVE_RAR = "RAR Archive"
    ARCHIVE_ZIP = "ZIP Archive"


@dataclass
class DiscFile: #vers 1
    """A file entry inside a disc image."""
    path: str           # ISO path e.g. /STAGE/ROOM000.RDT
    size: int
    sector: int = 0     # LBA sector on disc
    is_dir: bool = False

    @property
    def name(self) -> str:
        return os.path.basename(self.path)

    @property
    def ext(self) -> str:
        return os.path.splitext(self.name)[1].upper()


# --- PS1 raw sector constants ---
_SECTOR_RAW  = 2352
_SECTOR_DATA = 2048
_SYNC = bytes([0x00,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0x00])


def _read_sector_data(raw: bytes) -> bytes: #vers 1
    """Strip PS1 sector header/ECC to get 2048 bytes of data."""
    if len(raw) < _SECTOR_RAW:
        return raw[:_SECTOR_DATA]
    if raw[:12] == _SYNC:
        mode = raw[15]
        if mode == 1:
            return raw[16:16 + _SECTOR_DATA]
        elif mode == 2:
            return raw[24:24 + _SECTOR_DATA]   # skip 8-byte sub-header
    return raw[:_SECTOR_DATA]


class RawSectorReader: #vers 2
    """Read a raw-sector CD image (BIN or IMG).
    Handles PS1 Mode2 Form1, Mode1, and 150-sector pregap offset.
    Scans for the ISO9660 PVD to find the true track start.
    """

    _PVD_SIG = b'\x01CD001'

    def __init__(self, path: str): #vers 1
        self._f = open(path, 'rb')
        self._f.seek(0, 2)
        raw_size = self._f.tell()
        self._num_sectors = raw_size // _SECTOR_RAW
        self._track_offset = self._find_track_offset()

    def _find_track_offset(self) -> int: #vers 1
        """Scan for ISO9660 PVD to find where the data track starts.
        Returns sector offset (track_start = pvd_sector - 16).
        PS1 discs often have a 150-sector pregap before the data track.
        """
        # Scan first 300 sectors for PVD signature
        for lba in range(min(self._num_sectors, 300)):
            payload = self._read_raw_sector(lba)
            if payload[:5] == self._PVD_SIG:
                # PVD is always at LBA 16 from track start
                offset = max(0, lba - 16)
                return offset
        return 0  # no offset found, assume starts at 0

    def _read_raw_sector(self, physical_lba: int) -> bytes: #vers 1
        """Read and strip one raw sector at physical_lba."""
        self._f.seek(physical_lba * _SECTOR_RAW)
        raw = self._f.read(_SECTOR_RAW)
        if len(raw) < _SECTOR_RAW:
            return bytes(_SECTOR_DATA)
        return _read_sector_data(raw)

    def close(self): #vers 1
        self._f.close()

    def _sector_at_lba(self, lba: int) -> bytes: #vers 1
        """Read logical LBA (relative to track start) as 2048-byte data."""
        return self._read_raw_sector(self._track_offset + lba)

    def read_lba(self, lba: int, count: int) -> bytes: #vers 1
        out = bytearray()
        for i in range(count):
            out += self._sector_at_lba(lba + i)
        return bytes(out)

    def as_iso_bytes(self) -> bytes: #vers 1
        """Return complete ISO data track as 2048-byte/sector stream for pycdlib."""
        out = bytearray()
        iso_sectors = self._num_sectors - self._track_offset
        for lba in range(iso_sectors):
            out += self._sector_at_lba(lba)
        return bytes(out)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


class DiscImage: #vers 1
    """Base class for all disc image types."""

    def __init__(self): #vers 1
        self._files: List[DiscFile] = []
        self.format: DiscFormat = DiscFormat.UNKNOWN
        self.path: str = ''

    def list_files(self) -> List[DiscFile]: #vers 1
        return self._files

    def extract_file(self, disc_path: str, output_path: str): #vers 1
        raise NotImplementedError

    def extract_all(self, output_dir: str,
                    filter_ext: Optional[List[str]] = None) -> List[str]: #vers 1
        """Extract all (or filtered) files to output_dir."""
        extracted = []
        for f in self._files:
            if f.is_dir:
                continue
            if filter_ext and f.ext not in filter_ext:
                continue
            dest = os.path.join(output_dir,
                                f.path.lstrip('/').replace('/', os.sep))
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            try:
                self.extract_file(f.path, dest)
                extracted.append(dest)
            except Exception as e:
                print(f"Extract error {f.path}: {e}")
        return extracted

    def close(self): #vers 1
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


class ISOImage(DiscImage): #vers 1
    """ISO9660 image via pycdlib."""

    def __init__(self, path: str): #vers 1
        super().__init__()
        self.format = DiscFormat.ISO
        self.path = path
        import pycdlib
        self._iso = pycdlib.PyCdlib()
        self._iso.open(path)
        self._scan()

    def _scan(self): #vers 1
        self._files = []
        try:
            facade = self._iso.get_iso9660_facade()
            for dirpath, dirnames, filenames in self._iso.walk(iso_path='/'):
                for fname in filenames:
                    iso_path = dirpath.rstrip('/') + '/' + fname
                    try:
                        rec = self._iso.get_record(iso_path=iso_path)
                        size = rec.data_length
                    except Exception:
                        size = 0
                    # Strip version number ;1
                    clean = iso_path.split(';')[0]
                    self._files.append(DiscFile(path=clean, size=size))
        except Exception as e:
            print(f"ISO scan error: {e}")

    def extract_file(self, disc_path: str, output_path: str): #vers 1
        iso_path = disc_path if disc_path.startswith('/') else '/' + disc_path
        # pycdlib needs ;1 suffix
        if ';' not in iso_path:
            iso_path += ';1'
        self._iso.get_file_from_iso(local_path=output_path, iso_path=iso_path)

    def close(self): #vers 1
        try:
            self._iso.close()
        except Exception:
            pass


class BinCueImage(DiscImage): #vers 1
    """BIN/CUE CDRWin image. Parses CUE to find data track, reads raw BIN."""

    def __init__(self, cue_path: str): #vers 1
        super().__init__()
        self.format = DiscFormat.BIN_CUE
        self.path = cue_path
        self._bin_path = self._find_bin(cue_path)
        self._reader: Optional[RawSectorReader] = None
        self._iso_bytes: Optional[bytes] = None
        self._pyiso = None
        self._mount()
        self._scan()

    def _find_bin(self, cue_path: str) -> str: #vers 1
        """Find the first data track BIN from the CUE file."""
        folder = os.path.dirname(cue_path)
        try:
            with open(cue_path, 'r', errors='replace') as f:
                for line in f:
                    line = line.strip()
                    if line.upper().startswith('FILE'):
                        # FILE "filename.bin" BINARY
                        parts = line.split('"')
                        if len(parts) >= 2:
                            name = parts[1]
                            return os.path.join(folder, name)
        except OSError:
            pass
        # Fallback: same name as cue with .bin
        base = os.path.splitext(cue_path)[0]
        return base + '.bin'

    def _mount(self): #vers 2
        """Convert raw sectors to ISO bytes and mount via pycdlib."""
        if not os.path.exists(self._bin_path):
            return
        self._reader = RawSectorReader(self._bin_path)
        print(f"BIN/CUE: {self._reader._num_sectors} sectors, "
              f"track offset={self._reader._track_offset}")
        try:
            import pycdlib
            iso_bytes = self._reader.as_iso_bytes()
            print(f"BIN/CUE: ISO stream {len(iso_bytes)} bytes")
            self._pyiso = pycdlib.PyCdlib()
            self._pyiso.open_fp(io.BytesIO(iso_bytes))
            print(f"BIN/CUE: mounted OK")
        except Exception as e:
            print(f"BIN/CUE mount error: {e}")

    def _scan(self): #vers 1
        self._files = []
        if not self._pyiso:
            return
        try:
            for dirpath, dirnames, filenames in self._pyiso.walk(iso_path='/'):
                for fname in filenames:
                    iso_path = dirpath.rstrip('/') + '/' + fname
                    try:
                        rec = self._pyiso.get_record(iso_path=iso_path)
                        size = rec.data_length
                    except Exception:
                        size = 0
                    clean = iso_path.split(';')[0]
                    self._files.append(DiscFile(path=clean, size=size))
        except Exception as e:
            print(f"BIN/CUE scan error: {e}")

    def extract_file(self, disc_path: str, output_path: str): #vers 1
        if not self._pyiso:
            raise RuntimeError("Disc not mounted")
        iso_path = disc_path if disc_path.startswith('/') else '/' + disc_path
        if ';' not in iso_path:
            iso_path += ';1'
        self._pyiso.get_file_from_iso(local_path=output_path, iso_path=iso_path)

    def close(self): #vers 1
        if self._pyiso:
            try: self._pyiso.close()
            except Exception: pass
        if self._reader:
            self._reader.close()


class CcdImgImage(DiscImage): #vers 1
    """CloneCD CCD/IMG/SUB image. IMG is the raw sector file, CCD is the index."""

    def __init__(self, ccd_path: str): #vers 1
        super().__init__()
        self.format = DiscFormat.CCD_IMG
        self.path = ccd_path
        base = os.path.splitext(ccd_path)[0]
        self._img_path = base + '.img'
        if not os.path.exists(self._img_path):
            self._img_path = base + '.IMG'
        self._reader: Optional[RawSectorReader] = None
        self._pyiso = None
        self._mount()
        self._scan()

    def _mount(self): #vers 2
        if not os.path.exists(self._img_path):
            print(f"CCD/IMG: no IMG file found at {self._img_path}")
            return
        self._reader = RawSectorReader(self._img_path)
        print(f"CCD/IMG: {self._reader._num_sectors} sectors, "
              f"track offset={self._reader._track_offset}")
        try:
            import pycdlib
            iso_bytes = self._reader.as_iso_bytes()
            print(f"CCD/IMG: ISO stream {len(iso_bytes)} bytes")
            self._pyiso = pycdlib.PyCdlib()
            self._pyiso.open_fp(io.BytesIO(iso_bytes))
            print(f"CCD/IMG: mounted OK")
        except Exception as e:
            print(f"CCD/IMG mount error: {e}")
            # Try Joliet/Rock Ridge fallback
            try:
                import pycdlib
                self._pyiso = pycdlib.PyCdlib()
                self._pyiso.open_fp(io.BytesIO(iso_bytes))
            except Exception as e2:
                print(f"CCD/IMG mount fallback also failed: {e2}")

    def _scan(self): #vers 1
        self._files = []
        if not self._pyiso:
            return
        try:
            for dirpath, dirnames, filenames in self._pyiso.walk(iso_path='/'):
                for fname in filenames:
                    iso_path = dirpath.rstrip('/') + '/' + fname
                    try:
                        rec = self._pyiso.get_record(iso_path=iso_path)
                        size = rec.data_length
                    except Exception:
                        size = 0
                    clean = iso_path.split(';')[0]
                    self._files.append(DiscFile(path=clean, size=size))
        except Exception as e:
            print(f"CCD/IMG scan error: {e}")

    def extract_file(self, disc_path: str, output_path: str): #vers 1
        if not self._pyiso:
            raise RuntimeError("Disc not mounted")
        iso_path = disc_path if disc_path.startswith('/') else '/' + disc_path
        if ';' not in iso_path:
            iso_path += ';1'
        self._pyiso.get_file_from_iso(local_path=output_path, iso_path=iso_path)

    def close(self): #vers 1
        if self._pyiso:
            try: self._pyiso.close()
            except Exception: pass
        if self._reader:
            self._reader.close()


# --- Archive wrappers ---

class ArchiveImage(DiscImage): #vers 1
    """ZIP/7z/RAR archive containing a disc image. Extracts to temp, then mounts."""

    def __init__(self, archive_path: str): #vers 1
        super().__init__()
        self.path = archive_path
        ext = os.path.splitext(archive_path)[1].upper()
        self._inner: Optional[DiscImage] = None
        self._tmp_dir: Optional[str] = None

        if ext == '.ZIP':
            self.format = DiscFormat.ARCHIVE_ZIP
        elif ext in ('.7Z',):
            self.format = DiscFormat.ARCHIVE_7Z
        elif ext == '.RAR':
            self.format = DiscFormat.ARCHIVE_RAR

        self._contents = self._list_archive(archive_path)

    def _list_archive(self, path: str) -> List[str]: #vers 1
        """List filenames inside archive without extracting."""
        ext = os.path.splitext(path)[1].upper()
        try:
            if ext == '.ZIP':
                with zipfile.ZipFile(path) as z:
                    return z.namelist()
            elif ext in ('.7Z',):
                import py7zr
                with py7zr.SevenZipFile(path) as z:
                    return z.getnames()
            elif ext == '.RAR':
                import rarfile
                with rarfile.RarFile(path) as z:
                    return z.namelist()
        except Exception as e:
            print(f"Archive list error {path}: {e}")
        return []

    def list_archive_contents(self) -> List[str]: #vers 1
        return self._contents

    def extract_archive_to(self, output_dir: str) -> List[str]: #vers 1
        """Extract archive contents to output_dir. Returns list of extracted paths."""
        os.makedirs(output_dir, exist_ok=True)
        ext = os.path.splitext(self.path)[1].upper()
        try:
            if ext == '.ZIP':
                with zipfile.ZipFile(self.path) as z:
                    z.extractall(output_dir)
            elif ext == '.7Z':
                import py7zr
                with py7zr.SevenZipFile(self.path) as z:
                    z.extractall(output_dir)
            elif ext == '.RAR':
                import rarfile
                with rarfile.RarFile(self.path) as z:
                    z.extractall(output_dir)
        except Exception as e:
            print(f"Archive extract error: {e}")
            return []
        return [os.path.join(output_dir, f) for f in self._contents]

    def extract_file(self, disc_path: str, output_path: str): #vers 1
        pass  # archives need full extraction first

    def close(self): #vers 1
        if self._inner:
            self._inner.close()


# --- Format detection ---

def detect_format(path: str) -> DiscFormat: #vers 1
    """Detect disc image format from file extension and magic bytes."""
    ext = os.path.splitext(path)[1].upper()

    if ext == '.ISO':
        return DiscFormat.ISO
    if ext in ('.CUE',):
        return DiscFormat.BIN_CUE
    if ext == '.CCD':
        return DiscFormat.CCD_IMG
    if ext == '.IMG':
        # Could be CCD/IMG (if .ccd exists) or standalone
        ccd = os.path.splitext(path)[0] + '.ccd'
        if os.path.exists(ccd) or os.path.exists(ccd.upper()):
            return DiscFormat.CCD_IMG
        return DiscFormat.CCD_IMG   # treat as raw anyway
    if ext == '.BIN':
        cue = os.path.splitext(path)[0] + '.cue'
        if os.path.exists(cue) or os.path.exists(cue.upper()):
            return DiscFormat.BIN_CUE
        return DiscFormat.BIN_CUE
    if ext == '.7Z':
        return DiscFormat.ARCHIVE_7Z
    if ext == '.RAR':
        return DiscFormat.ARCHIVE_RAR
    if ext in ('.ZIP',):
        return DiscFormat.ARCHIVE_ZIP

    return DiscFormat.UNKNOWN


def open_disc(path: str) -> Optional[DiscImage]: #vers 1
    """Open a disc image of any supported format. Returns DiscImage or None."""
    fmt = detect_format(path)

    if fmt == DiscFormat.ISO:
        return ISOImage(path)
    if fmt == DiscFormat.BIN_CUE:
        # If given a .bin, look for matching .cue
        if path.upper().endswith('.BIN'):
            cue = os.path.splitext(path)[0] + '.cue'
            if not os.path.exists(cue):
                cue = os.path.splitext(path)[0] + '.CUE'
            if os.path.exists(cue):
                return BinCueImage(cue)
        return BinCueImage(path)
    if fmt == DiscFormat.CCD_IMG:
        if path.upper().endswith('.IMG'):
            ccd = os.path.splitext(path)[0] + '.ccd'
            if not os.path.exists(ccd):
                ccd = os.path.splitext(path)[0] + '.CCD'
            if os.path.exists(ccd):
                return CcdImgImage(ccd)
        return CcdImgImage(path)
    if fmt in (DiscFormat.ARCHIVE_7Z, DiscFormat.ARCHIVE_RAR, DiscFormat.ARCHIVE_ZIP):
        return ArchiveImage(path)

    return None


# --- ISO builder ---

def build_iso(source_folder: str, output_path: str,
              volume_label: str = 'REBIOHAZARD',
              publisher: str = 'ResBio-Evil-Workshop') -> bool: #vers 1
    """Build a new ISO9660 image from a source folder.
    Returns True on success.
    Does not add raw sectors / PS1 licensing data - produces a data ISO only.
    """
    import pycdlib
    iso = pycdlib.PyCdlib()
    iso.new(
        interchange_level=1,
        vol_ident=volume_label[:32],
        sys_ident='PLAYSTATION',
        publisher=publisher[:128],
    )

    for dirpath, dirnames, filenames in os.walk(source_folder):
        rel_dir = os.path.relpath(dirpath, source_folder)
        iso_dir = '/' + rel_dir.replace(os.sep, '/').lstrip('./')

        # Create directory if not root
        if iso_dir and iso_dir != '/' and iso_dir != '/.':
            try:
                iso.add_directory(iso_path=iso_dir)
            except Exception:
                pass

        for fname in filenames:
            src_path = os.path.join(dirpath, fname)
            iso_fname = fname.upper()
            # ISO9660 level 1: 8.3 filenames
            name, ext = os.path.splitext(iso_fname)
            iso_fname = name[:8] + ext[:4]
            iso_file_path = iso_dir.rstrip('/') + '/' + iso_fname + ';1'
            try:
                iso.add_file(src_path, iso_path=iso_file_path)
            except Exception as e:
                print(f"  Skipping {fname}: {e}")

    try:
        iso.write(output_path)
        iso.close()
        return True
    except Exception as e:
        print(f"ISO write error: {e}")
        iso.close()
        return False
