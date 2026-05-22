#!/usr/bin/env python3
#this belongs in apps/methods/rdt_writer.py - Version: 1
# X-Seti - May22 2026 - ResBio-Evil-Workshop - RDT Writer
"""
RDT Writer - Write modified RDT data back to binary file.
Only rewrites sections that changed (items, collision).
All other bytes preserved verbatim from original raw_data.
"""

import struct
import os
import shutil
from apps.core.re1_formats import RDTFile, RDTItem, RDTCollisionBoundary

##Methods list -
# write_rdt
# _write_items_section
# _write_collision_section
# _backup_file

def write_rdt(rdt: RDTFile, output_path: str): #vers 1
    """Write RDT back to disk, patching only items and collision sections."""
    if not rdt.raw_data:
        raise ValueError("RDT has no raw data to write")

    _backup_file(output_path)

    data = bytearray(rdt.raw_data)

    if rdt.header and len(rdt.header.offsets) >= 3:
        item_offset = rdt.header.offsets[2]
        if item_offset and item_offset < len(data):
            _write_items_section(data, item_offset, rdt.items)

        col_offset = rdt.header.offsets[1]
        if col_offset and col_offset < len(data):
            _write_collision_section(data, col_offset, rdt.collision)

    with open(output_path, 'wb') as f:
        f.write(data)

    # Update raw_data to reflect saved state
    rdt.raw_data = bytes(data)
    rdt.file_path = output_path


def _write_items_section(data: bytearray, offset: int, items: list): #vers 1
    """Patch item placement bytes in-place. Terminates with 0xFF entry."""
    item_struct_size = 12
    off = offset
    for item in items:
        if off + item_struct_size > len(data):
            break
        packed = struct.pack('<hhhHBBBB',
            item.x, item.y, item.z,
            item.rotation,
            item.item_type,
            item.flags,
            item.amount,
            0  # pad
        )
        data[off:off + item_struct_size] = packed
        off += item_struct_size

    # Write terminator
    if off + item_struct_size <= len(data):
        term = struct.pack('<hhhHBBBB', 0, 0, 0, 0, 0xFF, 0, 0, 0)
        data[off:off + item_struct_size] = term


def _write_collision_section(data: bytearray, offset: int, boundaries: list): #vers 1
    """Patch collision boundary bytes in-place after the SCA header (24 bytes)."""
    boundary_struct_size = 16
    off = offset + 24  # skip SCA header
    for b in boundaries:
        if off + boundary_struct_size > len(data):
            break
        packed = struct.pack('<HhhhhBBBB',
            b.boundary_type,
            b.x1, b.z1, b.x2, b.z2,
            b.floor, b.density, b.sound_attr,
            0  # pad
        )
        data[off:off + boundary_struct_size] = packed
        off += boundary_struct_size


def _backup_file(path: str): #vers 1
    """Create a .bak backup before overwriting, only if file exists."""
    if os.path.exists(path):
        backup = path + '.bak'
        if not os.path.exists(backup):
            shutil.copy2(path, backup)
