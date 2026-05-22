#!/usr/bin/env python3
#this belongs in apps/methods/rdt_loader.py - Version: 1
# X-Seti - May22 2026 - ResBio-Evil-Workshop - RDT Loader
"""
RDT Loader - Loads RDT files and populates the GUI table and info panels.
Called by ResBio_Evil_Workshop._open_file and _on_room_selected.
"""

import os
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

def load_rdt_file(main_window: 'ResBioEvilWorkshop', file_path: str) -> Optional[RDTFile]: #vers 1
    """Load an RDT file and update the main window UI."""
    if not os.path.exists(file_path):
        print(f"RDT Loader: File not found: {file_path}")
        return None

    rdt = parse_rdt(file_path)

    if not rdt.valid:
        errors = '\n'.join(rdt.parse_errors)
        print(f"RDT Loader: Parse errors in {file_path}:\n{errors}")

    # Store on main window
    main_window.current_rdt = rdt
    main_window.current_file_path = file_path

    # Update window title
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

    # Trigger map editor update
    if hasattr(main_window, 'room_map_editor'):
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


def populate_items_table(main_window: 'ResBioEvilWorkshop', rdt: RDTFile): #vers 1
    """Populate table with item placement data."""
    table = main_window.middle_list
    table.setColumnCount(5)
    table.setHorizontalHeaderLabels(["Item", "Type", "X", "Y", "Z"])
    table.setRowCount(len(rdt.items))

    for row, item in enumerate(rdt.items):
        table.setItem(row, 0, QTableWidgetItem(get_item_name(item.item_type)))
        table.setItem(row, 1, QTableWidgetItem(f"0x{item.item_type:02X}"))
        table.setItem(row, 2, QTableWidgetItem(str(item.x)))
        table.setItem(row, 3, QTableWidgetItem(str(item.y)))
        table.setItem(row, 4, QTableWidgetItem(str(item.z)))

    table.resizeColumnsToContents()
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
        cam_count = len(rdt.cameras)
        item_count = len(rdt.items)
        main_window.info_format.setText(f"Cams: {cam_count}  Items: {item_count}")


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
