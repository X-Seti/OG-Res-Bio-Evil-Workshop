#!/usr/bin/env python3
#this belongs in apps/gui/item_edit_dialog.py - Version: 1
# X-Seti - May22 2026 - ResBio-Evil-Workshop - Item Edit Dialog
"""
Item Edit Dialog - Edit an RDT item's type, position, rotation and amount.
Double-click an item row in the Items tab to open.
Changes are applied directly to the RDTItem object on OK.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QPushButton, QComboBox, QSpinBox, QLabel, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from apps.core.re1_formats import RDTItem, RE1_ITEM_NAMES, get_item_name

##Methods list -
# _build_ui
# _populate_type_combo
# _on_type_changed
# _apply_changes
# exec

##class ItemEditDialog:


class ItemEditDialog(QDialog): #vers 1
    """Dialog for editing a single RDT item."""

    def __init__(self, item: RDTItem, parent=None): #vers 1
        super().__init__(parent)
        self.item = item
        self._orig = (item.item_type, item.x, item.y, item.z,
                      item.rotation, item.flags, item.amount)
        self.setWindowTitle(f"Edit Item - {get_item_name(item.item_type)}")
        self.setModal(True)
        self.setMinimumWidth(340)
        self._build_ui()

    def _build_ui(self): #vers 1
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        title = QLabel(f"Item 0x{self.item.item_type:02X}  —  {get_item_name(self.item.item_type)}")
        title.setFont(QFont("Courier New", 9))
        layout.addWidget(title)

        sep = QFrame(); sep.setFrameStyle(QFrame.Shape.HLine)
        layout.addWidget(sep)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        # Item type combo
        self.type_combo = QComboBox()
        self._populate_type_combo()
        self.type_combo.currentIndexChanged.connect(self._on_type_changed)
        form.addRow("Type:", self.type_combo)

        # Amount
        self.amount_spin = QSpinBox()
        self.amount_spin.setRange(0, 255)
        self.amount_spin.setValue(self.item.amount)
        form.addRow("Amount:", self.amount_spin)

        # Flags
        self.flags_spin = QSpinBox()
        self.flags_spin.setRange(0, 255)
        self.flags_spin.setValue(self.item.flags)
        form.addRow("Flags (hex):", self.flags_spin)

        # Position X
        self.x_spin = QSpinBox()
        self.x_spin.setRange(-32768, 32767)
        self.x_spin.setValue(self.item.x)
        form.addRow("X:", self.x_spin)

        # Position Y
        self.y_spin = QSpinBox()
        self.y_spin.setRange(-32768, 32767)
        self.y_spin.setValue(self.item.y)
        form.addRow("Y:", self.y_spin)

        # Position Z
        self.z_spin = QSpinBox()
        self.z_spin.setRange(-32768, 32767)
        self.z_spin.setValue(self.item.z)
        form.addRow("Z:", self.z_spin)

        # Rotation
        self.rot_spin = QSpinBox()
        self.rot_spin.setRange(0, 65535)
        self.rot_spin.setValue(self.item.rotation)
        form.addRow("Rotation:", self.rot_spin)

        layout.addLayout(form)

        sep2 = QFrame(); sep2.setFrameStyle(QFrame.Shape.HLine)
        layout.addWidget(sep2)

        # Buttons
        btn_row = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        ok_btn = QPushButton("Apply")
        ok_btn.setDefault(True)
        ok_btn.clicked.connect(self._apply_changes)
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(ok_btn)
        layout.addLayout(btn_row)

    def _populate_type_combo(self): #vers 1
        """Fill combo with all known RE1 item types, select current."""
        self.type_combo.blockSignals(True)
        current_idx = 0
        sorted_items = sorted(RE1_ITEM_NAMES.items())
        for i, (type_id, name) in enumerate(sorted_items):
            self.type_combo.addItem(f"0x{type_id:02X}  {name}", type_id)
            if type_id == self.item.item_type:
                current_idx = i
        self.type_combo.setCurrentIndex(current_idx)
        self.type_combo.blockSignals(False)

    def _on_type_changed(self, index: int): #vers 1
        """Update window title on type change."""
        type_id = self.type_combo.itemData(index)
        self.setWindowTitle(f"Edit Item - {get_item_name(type_id)}")

    def _apply_changes(self): #vers 1
        """Write values back to the RDTItem object and accept dialog."""
        self.item.item_type = self.type_combo.currentData()
        self.item.amount    = self.amount_spin.value()
        self.item.flags     = self.flags_spin.value()
        self.item.x         = self.x_spin.value()
        self.item.y         = self.y_spin.value()
        self.item.z         = self.z_spin.value()
        self.item.rotation  = self.rot_spin.value()
        self.accept()
