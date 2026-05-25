#!/usr/bin/env python3
#this belongs in apps/gui/item_edit_dialog.py - Version: 2
# X-Seti - May25 2026 - ResBio-Evil-Workshop - Item Edit Dialog
"""
Item Edit Dialog - Edit all fields of an RDT item placement entry.
Shows icon, name dropdown, position, rotation, amount, flags.
Writes changes back to the RDT via rdt_writer.
"""

import os
from typing import Optional

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,
    QPushButton, QSpinBox, QComboBox, QGroupBox, QCheckBox,
    QFrame, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap

from apps.core.re1_formats import RDTFile, RDTItem, get_item_name
from apps.core.re1_formats import RE2_ITEM_NAMES

##Methods list -
# load_item
# _populate_type_combo
# _on_type_changed
# _apply_changes
# _accept

##class ItemEditDialog:


# RE1 item names (from re1_formats)
RE1_ITEM_NAMES = {
    0x00: "Nothing",        0x01: "Combat Knife",
    0x02: "Handgun",        0x03: "Shotgun",
    0x04: "Magnum",         0x05: "Rocket Launcher",
    0x06: "Flamethrower",   0x07: "Acid Rounds",
    0x08: "Handgun Rounds", 0x09: "Shotgun Shells",
    0x0A: "Magnum Rounds",  0x0B: "Fuel",
    0x0C: "Ink Ribbon",     0x0D: "Herb (Green)",
    0x0E: "Herb (Red)",     0x0F: "Herb (Blue)",
    0x10: "First Aid Spray", 0x11: "Mixed Herbs (G+R)",
    0x12: "Mixed Herbs (G+B)", 0x13: "Mixed Herbs (G+G)",
    0x14: "Mixed Herbs (G+G+G)", 0x15: "Mixed Herbs (G+R+B)",
    0x20: "Ink Ribbon",     0x28: "Wooden Emblem",
    0x29: "Gold Emblem",    0x2A: "Blue Jewel",
    0x2B: "Red Jewel",      0x2C: "Star Crest",
    0x2D: "Wolf Crest",     0x2E: "Eagle Crest",
    0x2F: "Armor Key",      0x30: "Shield Key",
    0x31: "Sword Key",      0x32: "Helmet Key",
    0x33: "Special Key",    0x34: "Doom Book 1",
    0x35: "Doom Book 2",    0x36: "Chemical",
    0x37: "Battery",        0x38: "MO Disk",
    0x39: "Valve Handle",   0x3A: "Square Crank",
    0x3B: "Hex Crank",      0x3C: "Map (Mansion 1F)",
    0x3D: "Map (Mansion 2F)", 0x3E: "Map (Guardhouse)",
    0x3F: "Map (Laboratory)",
}

# Item flags for RE2
RE2_ITEM_FLAGS = [
    (0x01, "On Floor"),
    (0x02, "Invisible"),
    (0x04, "Examined"),
    (0x08, "In Box"),
    (0x10, "Infinite Ammo"),
    (0x20, "No Drop"),
    (0x40, "Equipped"),
    (0x80, "Locked"),
]

# Use simpler RE1/RE2 agnostic flag names
ITEM_FLAGS = [
    (0x01, "On Floor (spawned)"),
    (0x02, "Invisible until trigger"),
    (0x04, "Already examined"),
    (0x08, "Inside container"),
    (0x10, "Infinite count"),
    (0x20, "Cannot be dropped"),
    (0x40, "Currently equipped"),
    (0x80, "Locked / conditional"),
]


class ItemEditDialog(QDialog): #vers 2
    """Edit all properties of an item placement entry."""

    item_changed = pyqtSignal(int)   # item index that changed

    def __init__(self, rdt: RDTFile, item_index: int,
                 game: str = 're1', parent=None): #vers 2
        super().__init__(parent)
        self.rdt        = rdt
        self.item_index = item_index
        self.game       = game
        self.setWindowTitle(f"Edit Item — {rdt.room_id}")
        self.setModal(True)
        self.resize(420, 480)
        self._build_ui()
        if 0 <= item_index < len(rdt.items):
            self.load_item(rdt.items[item_index])

    def _build_ui(self): #vers 2
        layout = QVBoxLayout(self)
        layout.setSpacing(6)

        # Icon + type row
        top_row = QHBoxLayout()
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(48, 48)
        self.icon_label.setStyleSheet(
            "border: 1px solid #444; background: #111;")
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top_row.addWidget(self.icon_label)

        type_col = QVBoxLayout()
        self.type_combo = QComboBox()
        self.type_combo.setFont(QFont("Courier New", 9))
        self._populate_type_combo()
        self.type_combo.currentIndexChanged.connect(self._on_type_changed)
        self.type_id_label = QLabel("0x00")
        self.type_id_label.setFont(QFont("Courier New", 8))
        self.type_id_label.setStyleSheet("color: #888;")
        type_col.addWidget(QLabel("Item Type:"))
        type_col.addWidget(self.type_combo)
        type_col.addWidget(self.type_id_label)
        top_row.addLayout(type_col, stretch=1)
        layout.addLayout(top_row)

        sep = QFrame(); sep.setFrameStyle(QFrame.Shape.HLine)
        layout.addWidget(sep)

        # Position
        pos_grp = QGroupBox("Position")
        pos_form = QFormLayout(pos_grp)

        self.x_spin = QSpinBox()
        self.x_spin.setRange(-32768, 32767)
        self.y_spin = QSpinBox()
        self.y_spin.setRange(-32768, 32767)
        self.z_spin = QSpinBox()
        self.z_spin.setRange(-32768, 32767)
        self.rot_spin = QSpinBox()
        self.rot_spin.setRange(0, 65535)
        self.rot_spin.setWrapping(True)

        for spin in [self.x_spin, self.y_spin, self.z_spin, self.rot_spin]:
            spin.setFont(QFont("Courier New", 9))

        pos_form.addRow("X:", self.x_spin)
        pos_form.addRow("Y:", self.y_spin)
        pos_form.addRow("Z:", self.z_spin)
        pos_form.addRow("Rotation (0-65535):", self.rot_spin)
        layout.addWidget(pos_grp)

        # Amount
        amt_grp = QGroupBox("Count / Amount")
        amt_form = QFormLayout(amt_grp)
        self.amount_spin = QSpinBox()
        self.amount_spin.setRange(0, 255)
        self.amount_spin.setFont(QFont("Courier New", 9))
        self.amount_spin.setToolTip(
            "For ammo: number of rounds. For items: usually 1 or 0.")
        amt_form.addRow("Amount:", self.amount_spin)
        layout.addWidget(amt_grp)

        # Flags
        flags_grp = QGroupBox("Flags")
        flags_layout = QVBoxLayout(flags_grp)
        self.flag_checks = []
        for bit, label in ITEM_FLAGS:
            cb = QCheckBox(f"0x{bit:02X}  {label}")
            cb.setFont(QFont("Courier New", 8))
            self.flag_checks.append((bit, cb))
            flags_layout.addWidget(cb)
        layout.addWidget(flags_grp)

        # Buttons
        btn_row = QHBoxLayout()
        ok_btn     = QPushButton("Apply Changes")
        ok_btn.clicked.connect(self._accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(ok_btn)
        btn_row.addWidget(cancel_btn)
        layout.addLayout(btn_row)

    def _populate_type_combo(self): #vers 1
        """Fill type dropdown with all known item names."""
        self.type_combo.clear()
        names = RE2_ITEM_NAMES if self.game == 're2' else RE1_ITEM_NAMES
        for type_id in sorted(names.keys()):
            self.type_combo.addItem(
                f"0x{type_id:02X}  {names[type_id]}", userData=type_id)

    def load_item(self, item: RDTItem): #vers 2
        """Populate controls from an RDTItem."""
        # Type
        names = RE2_ITEM_NAMES if self.game == 're2' else RE1_ITEM_NAMES
        for i in range(self.type_combo.count()):
            if self.type_combo.itemData(i) == item.item_type:
                self.type_combo.setCurrentIndex(i)
                break
        else:
            # Unknown type - add it
            label = f"0x{item.item_type:02X}  Unknown"
            self.type_combo.addItem(label, userData=item.item_type)
            self.type_combo.setCurrentIndex(self.type_combo.count() - 1)

        # Position
        self.x_spin.setValue(item.x)
        self.y_spin.setValue(item.y)
        self.z_spin.setValue(item.z)
        self.rot_spin.setValue(item.rotation)
        self.amount_spin.setValue(item.amount)

        # Flags
        for bit, cb in self.flag_checks:
            cb.setChecked(bool(item.flags & bit))

        self._update_icon(item.item_type)

    def _on_type_changed(self, idx: int): #vers 1
        """Update icon and type ID label when type changes."""
        type_id = self.type_combo.itemData(idx)
        if type_id is not None:
            self.type_id_label.setText(f"0x{type_id:02X}")
            self._update_icon(type_id)

    def _update_icon(self, item_type: int): #vers 1
        """Show item icon from cache."""
        try:
            from apps.core.re_item_icons import get_item_icon
            px = get_item_icon(item_type, 44)
            if px:
                self.icon_label.setPixmap(px)
                return
        except Exception:
            pass
        self.icon_label.setText(f"0x{item_type:02X}")
        self.icon_label.setStyleSheet(
            "border:1px solid #444; background:#111; color:#888;")

    def _accept(self): #vers 2
        """Write changes back to rdt.items[item_index] and trigger save."""
        if not (0 <= self.item_index < len(self.rdt.items)):
            self.accept()
            return

        item = self.rdt.items[self.item_index]

        # Apply all fields
        type_id     = self.type_combo.currentData()
        item.item_type = type_id if type_id is not None else item.item_type
        item.x         = self.x_spin.value()
        item.y         = self.y_spin.value()
        item.z         = self.z_spin.value()
        item.rotation  = self.rot_spin.value()
        item.amount    = self.amount_spin.value()

        flags = 0
        for bit, cb in self.flag_checks:
            if cb.isChecked():
                flags |= bit
        item.flags = flags

        self.item_changed.emit(self.item_index)
        self.accept()
