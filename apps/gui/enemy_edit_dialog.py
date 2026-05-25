#!/usr/bin/env python3
#this belongs in apps/gui/enemy_edit_dialog.py - Version: 1
# X-Seti - May25 2026 - ResBio-Evil-Workshop - Enemy Edit Dialog
"""
Enemy Edit Dialog - Edit all properties of an enemy placement entry.
Type dropdown, position, rotation, AI flags, spawn conditions.
"""

from typing import Optional

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,
    QPushButton, QSpinBox, QComboBox, QGroupBox, QCheckBox,
    QFrame
)
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont

from apps.core.re1_formats import (
    RDTFile, RDTEnemy, get_enemy_name,
    RE1_ENEMY_NAMES, RE2_ENEMY_NAMES, RE3_ENEMY_NAMES
)

##Methods list -
# load_enemy
# _populate_type_combo
# _on_type_changed
# _accept

##class EnemyEditDialog:


class EnemyEditDialog(QDialog): #vers 1

    enemy_changed = pyqtSignal(int)   # enemy index

    def __init__(self, rdt: RDTFile, enemy_index: int,
                 game: str = 're1', parent=None): #vers 1
        super().__init__(parent)
        self.rdt         = rdt
        self.enemy_index = enemy_index
        self.game        = game
        self.setWindowTitle(f"Edit Enemy — {rdt.room_id}")
        self.setModal(True)
        self.resize(400, 380)
        self._build_ui()
        if 0 <= enemy_index < len(rdt.enemies):
            self.load_enemy(rdt.enemies[enemy_index])

    def _build_ui(self): #vers 1
        layout = QVBoxLayout(self)
        layout.setSpacing(6)

        # Type
        type_grp = QGroupBox("Enemy Type")
        type_form = QFormLayout(type_grp)
        self.type_combo = QComboBox()
        self.type_combo.setFont(QFont("Courier New", 9))
        self._populate_type_combo()
        self.type_combo.currentIndexChanged.connect(self._on_type_changed)
        self.type_id_label = QLabel("0x00")
        self.type_id_label.setFont(QFont("Courier New", 8))
        self.type_id_label.setStyleSheet("color: #888;")
        type_form.addRow("Type:", self.type_combo)
        type_form.addRow("Type ID:", self.type_id_label)
        layout.addWidget(type_grp)

        # Position
        pos_grp = QGroupBox("Position")
        pos_form = QFormLayout(pos_grp)
        self.x_spin = QSpinBox(); self.x_spin.setRange(-32768, 32767)
        self.y_spin = QSpinBox(); self.y_spin.setRange(-32768, 32767)
        self.z_spin = QSpinBox(); self.z_spin.setRange(-32768, 32767)
        self.rot_spin = QSpinBox(); self.rot_spin.setRange(0, 65535)
        self.floor_spin = QSpinBox(); self.floor_spin.setRange(0, 15)
        for s in [self.x_spin, self.y_spin, self.z_spin,
                  self.rot_spin, self.floor_spin]:
            s.setFont(QFont("Courier New", 9))
        pos_form.addRow("X:", self.x_spin)
        pos_form.addRow("Y:", self.y_spin)
        pos_form.addRow("Z:", self.z_spin)
        pos_form.addRow("Rotation:", self.rot_spin)
        pos_form.addRow("Floor:", self.floor_spin)
        layout.addWidget(pos_grp)

        # Spawn
        spawn_grp = QGroupBox("Spawn Settings")
        spawn_form = QFormLayout(spawn_grp)
        self.id_spin  = QSpinBox(); self.id_spin.setRange(0, 255)
        self.num_spin = QSpinBox(); self.num_spin.setRange(0, 255)
        self.id_spin.setToolTip("Unique enemy ID within room")
        self.num_spin.setToolTip("Spawn group / scenario condition")
        spawn_form.addRow("Enemy ID:", self.id_spin)
        spawn_form.addRow("Spawn Group:", self.num_spin)
        layout.addWidget(spawn_grp)

        sep = QFrame(); sep.setFrameStyle(QFrame.Shape.HLine)
        layout.addWidget(sep)

        btn_row = QHBoxLayout()
        ok_btn = QPushButton("Apply Changes")
        ok_btn.clicked.connect(self._accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(ok_btn)
        btn_row.addWidget(cancel_btn)
        layout.addLayout(btn_row)

    def _populate_type_combo(self): #vers 2
        if self.game == 're3':
            names = RE3_ENEMY_NAMES
        elif self.game == 're2':
            names = RE2_ENEMY_NAMES
        else:
            names = RE1_ENEMY_NAMES
        for type_id in sorted(names.keys()):
            self.type_combo.addItem(
                f"0x{type_id:02X}  {names[type_id]}", userData=type_id)

    def load_enemy(self, enemy: RDTEnemy): #vers 1
        for i in range(self.type_combo.count()):
            if self.type_combo.itemData(i) == enemy.enemy_type:
                self.type_combo.setCurrentIndex(i)
                break
        else:
            self.type_combo.addItem(
                f"0x{enemy.enemy_type:02X}  Unknown", userData=enemy.enemy_type)
            self.type_combo.setCurrentIndex(self.type_combo.count()-1)

        self.x_spin.setValue(enemy.x)
        self.y_spin.setValue(enemy.y)
        self.z_spin.setValue(enemy.z)
        self.rot_spin.setValue(enemy.rotation)
        self.floor_spin.setValue(enemy.floor)
        self.id_spin.setValue(enemy.id)
        self.num_spin.setValue(enemy.num)

    def _on_type_changed(self, idx: int): #vers 1
        type_id = self.type_combo.itemData(idx)
        if type_id is not None:
            self.type_id_label.setText(f"0x{type_id:02X}")

    def _accept(self): #vers 1
        if not (0 <= self.enemy_index < len(self.rdt.enemies)):
            self.accept(); return
        enemy = self.rdt.enemies[self.enemy_index]
        type_id = self.type_combo.currentData()
        enemy.enemy_type = type_id if type_id is not None else enemy.enemy_type
        enemy.x         = self.x_spin.value()
        enemy.y         = self.y_spin.value()
        enemy.z         = self.z_spin.value()
        enemy.rotation  = self.rot_spin.value()
        enemy.floor     = self.floor_spin.value()
        enemy.id        = self.id_spin.value()
        enemy.num       = self.num_spin.value()
        self.enemy_changed.emit(self.enemy_index)
        self.accept()
