#!/usr/bin/env python3
#this belongs in apps/methods/rdt_loader.py - Version: 1
# X-Seti - May22 2026 - ResBio-Evil-Workshop - RDT Loader
"""
RDT Loader - Loads RDT files and populates the GUI table and info panels.
Called by ResBio_Evil_Workshop._open_file and _on_room_selected.
"""

import os
from apps.debug.debug_functions import img_debugger
from typing import Optional, TYPE_CHECKING

from PyQt6.QtWidgets import (
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QLabel
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont

from apps.core.re1_formats import (
    parse_rdt, RDTFile, RDTCamera, RDTItem, get_item_name, RE1FormatError
)

if TYPE_CHECKING:
    from apps.components.ResBio_Evil_Workshop.ResBio_Evil_Workshop import ResBioEvilWorkshop

##Methods list -
# load_rdt_file
# populate_room_table
# populate_items_table
# populate_cameras_table
# populate_info_panel
# get_room_summary_text
# setup_middle_table_columns

def load_rdt_file(main_window: 'ResBioEvilWorkshop', file_path: str) -> Optional[RDTFile]: #vers 2
    """Load an RDT/ARD file and update the main window UI."""
    if not os.path.exists(file_path):
        print(f"RDT Loader: File not found: {file_path}")
        return None

    ext = os.path.splitext(file_path)[1].upper()
    if ext not in ('.RDT', '.ARD'):
        print(f"RDT Loader: Not an RDT file: {file_path}")
        return None

    rdt = parse_rdt(file_path)

    if not rdt.valid:
        errors = '\n'.join(rdt.parse_errors)
        print(f"RDT Loader: Parse errors in {file_path}:\n{errors}")

    # Store on main window
    main_window.current_rdt = rdt
    main_window.current_file_path = file_path

    # Update window title
    try:
        from apps.version import title_string
        main_window.setWindowTitle(title_string(rdt.room_id))
    except ImportError:
        main_window.setWindowTitle(f"ResBio-Evil Workshop: {rdt.room_id}")

    # Populate middle table
    populate_room_table(main_window, rdt)

    # Show summary in text display
    if hasattr(main_window, 'text_display'):
        main_window.text_display.setText(get_room_summary_text(rdt))

    # Populate info panel
    if hasattr(main_window, 'info_name'):
        main_window.info_name.setText(rdt.room_id)

    # Enable save button
    if hasattr(main_window, 'save_btn'):
        main_window.save_btn.setEnabled(rdt.valid)

    # Trigger floor plan update
    if hasattr(main_window, 'floor_plan') and main_window.floor_plan:
        main_window.floor_plan.load_rdt(rdt, rdt.room_id)

    # Trigger SCD browser update
    if hasattr(main_window, 'scd_browser') and main_window.scd_browser:
        main_window.scd_browser.load_rdt(rdt)

    # Enable export button
    if hasattr(main_window, 'export_btn'):
        main_window.export_btn.setEnabled(rdt.valid)

    # Enable scripts button
    if hasattr(main_window, 'scripts_btn'):
        main_window.scripts_btn.setEnabled(rdt.valid)

    # Init item icon cache once (walk is expensive, only do it once per session)
    from apps.core.re_item_icons import is_cache_loaded, init_icon_cache
    if not is_cache_loaded() and not getattr(main_window, '_icon_cache_searched', False):
        main_window._icon_cache_searched = True  # don't retry on every RDT
        folder = rdt.file_path
        roots = set()
        for _ in range(4):  # walk up max 4 levels
            folder = os.path.dirname(folder)
            if folder and folder not in roots:
                roots.add(folder)
        if init_icon_cache(list(roots)):
            img_debugger.debug("Item icon cache loaded from STATUS.TIM")

    # Load audio - only scan folder if it changed since last load
    if hasattr(main_window, 'audio_player') and main_window.audio_player:
        room_dir = os.path.dirname(rdt.file_path)
        last_dir = getattr(main_window, '_last_audio_scan_dir', None)
        if room_dir != last_dir:
            from apps.core.re_audio import scan_audio_files
            audio_files = scan_audio_files(room_dir)
            main_window._last_audio_scan_dir = room_dir
            main_window._last_audio_files = audio_files
        else:
            audio_files = getattr(main_window, '_last_audio_files', [])
        if audio_files:
            main_window.audio_player.load_file(audio_files[0])

    # Trigger map editor update
    if hasattr(main_window, 'room_map_editor'):
        img_debugger.debug(
            f"RDT Loader: {rdt.room_id} -> "
            f"cams={len(rdt.cameras)} items={len(rdt.items)} "
            f"col={len(rdt.collision)} enemies={len(rdt.enemies)} "
            f"aot={len(rdt.aot)}"
        )
        if rdt.cameras:
            c = rdt.cameras[0]
            img_debugger.debug(f"  cam0: from=({c.from_x},{c.from_z}) to=({c.to_x},{c.to_z})")
        main_window.room_map_editor.load_rdt(rdt)
        if hasattr(main_window, 'display_mode_combo'):
            main_window.display_mode_combo.setCurrentIndex(1)  # Switch to map view

    print(f"RDT Loader: Loaded {rdt.room_id} - "
          f"{len(rdt.cameras)} cameras, "
          f"{len(rdt.items)} items, "
          f"{len(rdt.collision)} collision boundaries")

    return rdt


def setup_middle_table_columns(table: QTableWidget): #vers 1
    """Configure middle panel table for RDT section display."""
    table.setColumnCount(3)
    table.setHorizontalHeaderLabels(["Section", "Count", "Info"])
    table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    table.setAlternatingRowColors(True)
    table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    table.horizontalHeader().setStretchLastSection(True)
    table.setColumnWidth(0, 140)
    table.setColumnWidth(1, 60)


def populate_room_table(main_window: 'ResBioEvilWorkshop', rdt: RDTFile): #vers 1
    """Populate the middle table with RDT section overview."""
    table = main_window.middle_list
    setup_middle_table_columns(table)

    sections = [
        ("Room ID",       rdt.room_id,                    ""),
        ("File Size",     f"{rdt.file_size} bytes",       ""),
        ("Cameras",       str(len(rdt.cameras)),          _camera_summary(rdt)),
        ("Items",         str(len(rdt.items)),            _item_summary(rdt)),
        ("Collision",     str(len(rdt.collision)),        _collision_summary(rdt)),
        ("Sound Banks",   str(rdt.header.num_sound_banks if rdt.header else 0), ""),
        ("Offsets",       "19",                           _offset_summary(rdt)),
        ("Parse Errors",  str(len(rdt.parse_errors)),    '; '.join(rdt.parse_errors) if rdt.parse_errors else "None"),
    ]

    table.setRowCount(len(sections))

    for row, (label, value, info) in enumerate(sections):
        table.setItem(row, 0, QTableWidgetItem(label))
        table.setItem(row, 1, QTableWidgetItem(value))
        table.setItem(row, 2, QTableWidgetItem(info))

        # Highlight errors in red
        if label == "Parse Errors" and rdt.parse_errors:
            for col in range(3):
                item = table.item(row, col)
                if item:
                    item.setForeground(QColor(220, 80, 80))

    table.resizeRowsToContents()


def populate_items_table(main_window: 'ResBioEvilWorkshop', rdt: RDTFile): #vers 2
    """Populate table with item placement data, icons and correct game names."""
    from apps.core.re_room_names import get_game_from_room_id
    from apps.core.re_item_icons import get_item_icon, is_cache_loaded

    # Detect game for correct item names
    game = get_game_from_room_id(rdt.room_id)

    table = main_window.middle_list
    use_icons = is_cache_loaded()

    table.setColumnCount(6 if use_icons else 5)
    if use_icons:
        table.setHorizontalHeaderLabels(["", "Item", "Type", "X", "Y", "Z"])
        table.setColumnWidth(0, 32)
    else:
        table.setHorizontalHeaderLabels(["Item", "Type", "X", "Y", "Z"])
    table.setRowCount(len(rdt.items))
    table.setRowCount(len(rdt.items))
    table.verticalHeader().setDefaultSectionSize(28)

    for row, item in enumerate(rdt.items):
        name = get_item_name(item.item_type, game)
        col = 0

        if use_icons:
            icon_item = QTableWidgetItem()
            px = get_item_icon(item.item_type, 24)
            if px:
                icon_item.setData(Qt.ItemDataRole.DecorationRole, px)
            table.setItem(row, col, icon_item)
            col += 1

        table.setItem(row, col,   QTableWidgetItem(name))
        table.setItem(row, col+1, QTableWidgetItem(f"0x{item.item_type:02X}"))
        table.setItem(row, col+2, QTableWidgetItem(str(item.x)))
        table.setItem(row, col+3, QTableWidgetItem(str(item.y)))
        table.setItem(row, col+4, QTableWidgetItem(str(item.z)))

    table.resizeColumnsToContents()
    if use_icons:
        table.setColumnWidth(0, 32)
    table.horizontalHeader().setStretchLastSection(True)


def populate_cameras_table(main_window: 'ResBioEvilWorkshop', rdt: RDTFile): #vers 1
    """Populate table with camera data."""
    table = main_window.middle_list
    table.setColumnCount(4)
    table.setHorizontalHeaderLabels(["Cam", "From (X,Y,Z)", "To (X,Y,Z)", "Mask Offset"])
    table.setRowCount(len(rdt.cameras))

    for row, cam in enumerate(rdt.cameras):
        table.setItem(row, 0, QTableWidgetItem(f"Camera {row}"))
        table.setItem(row, 1, QTableWidgetItem(f"{cam.from_x}, {cam.from_y}, {cam.from_z}"))
        table.setItem(row, 2, QTableWidgetItem(f"{cam.to_x}, {cam.to_y}, {cam.to_z}"))
        table.setItem(row, 3, QTableWidgetItem(f"0x{cam.masks_offset:08X}"))

    table.resizeColumnsToContents()
    table.horizontalHeader().setStretchLastSection(True)


def populate_info_panel(main_window: 'ResBioEvilWorkshop', rdt: RDTFile): #vers 1
    """Update right panel info fields from RDT data."""
    if hasattr(main_window, 'info_name'):
        main_window.info_name.setText(rdt.room_id)
        main_window.info_name.setReadOnly(True)

    if hasattr(main_window, 'info_format'):
        cam_count  = len(rdt.cameras)
        item_count = len(rdt.items)
        col_count  = len(rdt.collision)
        main_window.info_format.setText(
            f"Cams:{cam_count}  Items:{item_count}  Col:{col_count}")


def get_room_summary_text(rdt: RDTFile) -> str: #vers 1
    """Return a text summary of the RDT file for the text display panel."""
    lines = []
    lines.append(f"Room: {rdt.room_id}")
    lines.append(f"File: {rdt.file_path}")
    lines.append(f"Size: {rdt.file_size} bytes")
    lines.append("")

    if rdt.header:
        lines.append(f"Cameras: {rdt.header.num_cameras}")
        lines.append(f"Sound Banks: {rdt.header.num_sound_banks}")
        lines.append("")
        lines.append("Offset Table:")
        offset_names = [
            "Camera switches", "Collision (SCA)", "Items/obstacles",
            "TMD/TIM pairs", "Unknown4", "Unknown5",
            "Init script (SCD)", "Exec script (SCD)", "Event scripts (EVT)",
            "Skeleton", "Skel anim steps", "Unknown11", "Unknown12",
            "Room animations", "Unknown14", "Unknown15",
            "Unknown16", "Unknown17", "Unknown18",
        ]
        for i, off in enumerate(rdt.header.offsets):
            name = offset_names[i] if i < len(offset_names) else f"Offset{i}"
            lines.append(f"  [{i:02d}] 0x{off:08X}  {name}")

    lines.append("")
    lines.append(f"Cameras ({len(rdt.cameras)}):")
    for i, cam in enumerate(rdt.cameras):
        lines.append(f"  [{i}] From ({cam.from_x}, {cam.from_y}, {cam.from_z})"
                     f"  To ({cam.to_x}, {cam.to_y}, {cam.to_z})")

    lines.append("")
    lines.append(f"Items ({len(rdt.items)}):")
    for item in rdt.items:
        lines.append(f"  {get_item_name(item.item_type):30s} "
                     f"pos ({item.x:6d}, {item.y:6d}, {item.z:6d})")

    lines.append("")
    lines.append(f"Collision boundaries: {len(rdt.collision)}")

    if rdt.parse_errors:
        lines.append("")
        lines.append("Parse errors:")
        for e in rdt.parse_errors:
            lines.append(f"  ! {e}")

    return '\n'.join(lines)


# --- Internal helpers ---

def populate_enemies_table(main_window, rdt: RDTFile): #vers 1
    """Populate middle table with enemy placement data."""
    from apps.core.re_room_names import get_game_from_room_id
    from apps.core.re1_formats import get_enemy_name
    game  = get_game_from_room_id(rdt.room_id)
    table = main_window.middle_list
    table.setColumnCount(6)
    table.setHorizontalHeaderLabels(
        ["Enemy", "Type", "X", "Y", "Z", "Floor"])
    table.setRowCount(len(rdt.enemies))
    for row, enemy in enumerate(rdt.enemies):
        name = get_enemy_name(enemy.enemy_type, game)
        table.setItem(row, 0, QTableWidgetItem(name))
        table.setItem(row, 1, QTableWidgetItem(f"0x{enemy.enemy_type:02X}"))
        table.setItem(row, 2, QTableWidgetItem(str(enemy.x)))
        table.setItem(row, 3, QTableWidgetItem(str(enemy.y)))
        table.setItem(row, 4, QTableWidgetItem(str(enemy.z)))
        table.setItem(row, 5, QTableWidgetItem(str(enemy.floor)))
    table.resizeColumnsToContents()
    table.horizontalHeader().setStretchLastSection(True)


def populate_aot_table(main_window, rdt: RDTFile): #vers 1
    """Populate middle table with AOT trigger data."""
    from apps.core.re1_formats import AOT_TYPE_NAMES
    table = main_window.middle_list
    table.setColumnCount(6)
    table.setHorizontalHeaderLabels(
        ["Type", "X", "Z", "W", "D", "Floor"])
    table.setRowCount(len(rdt.aot))
    for row, aot in enumerate(rdt.aot):
        type_name = AOT_TYPE_NAMES.get(aot.aot_type, f"0x{aot.aot_type:02X}")
        table.setItem(row, 0, QTableWidgetItem(type_name))
        table.setItem(row, 1, QTableWidgetItem(str(aot.x)))
        table.setItem(row, 2, QTableWidgetItem(str(aot.z)))
        table.setItem(row, 3, QTableWidgetItem(str(aot.w)))
        table.setItem(row, 4, QTableWidgetItem(str(aot.d)))
        table.setItem(row, 5, QTableWidgetItem(str(aot.floor)))
    table.resizeColumnsToContents()
    table.horizontalHeader().setStretchLastSection(True)


def _camera_summary(rdt: RDTFile) -> str: #vers 1
    if not rdt.cameras:
        return ""
    cam = rdt.cameras[0]
    return f"First: From ({cam.from_x},{cam.from_y},{cam.from_z})"


def _item_summary(rdt: RDTFile) -> str: #vers 1
    if not rdt.items:
        return ""
    names = [get_item_name(i.item_type) for i in rdt.items[:3]]
    suffix = "..." if len(rdt.items) > 3 else ""
    return ', '.join(names) + suffix


def _collision_summary(rdt: RDTFile) -> str: #vers 1
    if not rdt.collision:
        return ""
    types = set(b.boundary_type for b in rdt.collision)
    return f"Types: {sorted(types)}"


def _offset_summary(rdt: RDTFile) -> str: #vers 1
    if not rdt.header:
        return ""
    nonzero = sum(1 for o in rdt.header.offsets if o != 0)
    return f"{nonzero}/19 active"


def extract_embedded_tims(rdt: RDTFile) -> list: #vers 1
    """Extract TIM textures embedded in RDT offset[3] (TMD/TIM pairs).
    Returns list of TIMFile objects.
    """
    from apps.core.re1_formats import parse_tim
    import tempfile, os, struct

    tims = []
    if not rdt.header or not rdt.raw_data:
        return tims

    # RE1: offset[3] = TMD/TIM table. Each entry is 8 bytes: tmd_offset(4) + tim_offset(4)
    offsets = rdt.header.offsets
    if len(offsets) < 4:
        return tims

    tim_table_offset = offsets[3]
    if tim_table_offset == 0 or tim_table_offset >= len(rdt.raw_data):
        return tims

    data = rdt.raw_data
    size = len(data)
    off  = tim_table_offset

    # Scan for TIM magic (0x10 0x00 0x00 0x00) from this offset
    TIM_MAGIC = b'\x10\x00\x00\x00'
    search_end = min(off + 65536, size - 4)

    found_offsets = []
    pos = off
    while pos < search_end:
        idx = data.find(TIM_MAGIC, pos, search_end)
        if idx < 0:
            break
        found_offsets.append(idx)
        pos = idx + 4

    for tim_off in found_offsets:
        try:
            with tempfile.NamedTemporaryFile(suffix='.tim', delete=False) as f:
                f.write(data[tim_off:])
                tmp = f.name
            tim = parse_tim(tmp)
            os.unlink(tmp)
            if tim.valid:
                tims.append(tim)
        except Exception:
            pass

    return tims


def export_room_to_json(rdt: RDTFile, output_path: str): #vers 1
    """Export room data to JSON for external editing."""
    import json
    from apps.core.re1_formats import get_item_name

    doc = {
        "room_id":    rdt.room_id,
        "file":       rdt.file_path,
        "file_size":  rdt.file_size,
        "cameras": [
            {
                "index": i,
                "from":  list(cam.from_pos),
                "to":    list(cam.to_pos),
                "masks_offset": cam.masks_offset,
            }
            for i, cam in enumerate(rdt.cameras)
        ],
        "items": [
            {
                "index":      i,
                "type_id":    f"0x{item.item_type:02X}",
                "name":       get_item_name(item.item_type),
                "x": item.x, "y": item.y, "z": item.z,
                "rotation":   item.rotation,
                "amount":     item.amount,
                "flags":      item.flags,
            }
            for i, item in enumerate(rdt.items)
        ],
        "collision": [
            {
                "index":         i,
                "boundary_type": b.boundary_type,
                "x1": b.x1, "z1": b.z1,
                "x2": b.x2, "z2": b.z2,
                "floor":         b.floor,
            }
            for i, b in enumerate(rdt.collision)
        ],
        "offsets": [f"0x{o:08X}" for o in (rdt.header.offsets if rdt.header else [])],
        "sca_counts": rdt.sca_counts,
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(doc, f, indent=2)
    return output_path
