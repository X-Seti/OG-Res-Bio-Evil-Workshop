#!/usr/bin/env python3
#this belongs in apps/gui/launcher_dialog.py - Version: 1
# X-Seti - May22 2026 - ResBio-Evil-Workshop - Game Launcher Dialog
"""
Game Launcher Dialog - Configure and launch RE games in emulators.
Shows detected emulators, game version info, and launch options.
"""

import os
from typing import Optional

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFileDialog, QTreeWidget, QTreeWidgetItem,
    QGroupBox, QTextEdit, QFrame, QHeaderView, QComboBox,
    QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

from apps.core.re_launchers import (
    detect_emulators, get_launch_options, launch_disc,
    launch_pc_folder, open_in_filemanager, identify_disc,
    identify_folder, Platform, GameVersion, EmulatorInfo
)

##Methods list -
# _browse_disc
# _browse_folder
# _detect_all
# _populate_emulators
# _on_emulator_selected
# _launch
# _open_folder
# _log

##class LauncherDialog:


PLATFORM_COLORS = {
    Platform.PS1:       QColor(100, 140, 220),
    Platform.SATURN:    QColor(100, 200, 100),
    Platform.GAMECUBE:  QColor(200, 140, 80),
    Platform.PC_WIN98:  QColor(180, 180, 100),
    Platform.PC_MODERN: QColor(140, 200, 140),
    Platform.UNKNOWN:   QColor(140, 140, 140),
}


class LauncherDialog(QDialog): #vers 1

    def __init__(self, parent=None,
                 disc_path: str = '',
                 folder_path: str = ''): #vers 1
        super().__init__(parent)
        self.setWindowTitle("Game Launcher \u2014 ResBio-Evil Workshop")
        self.resize(700, 520)
        self.setModal(False)
        self._disc_path = disc_path
        self._folder_path = folder_path
        self._emulators = {}
        self._build_ui()
        self._detect_all()

    def _build_ui(self): #vers 1
        layout = QVBoxLayout(self)
        layout.setSpacing(6)

        # Disc image row
        disc_grp = QGroupBox("Disc Image / Folder")
        disc_layout = QVBoxLayout(disc_grp)

        disc_row = QHBoxLayout()
        disc_row.addWidget(QLabel("Disc:"))
        self.disc_edit = QLineEdit(self._disc_path)
        self.disc_edit.setPlaceholderText(".iso / .bin / .ccd / .img / .gcz / .rvz")
        disc_row.addWidget(self.disc_edit, stretch=1)
        browse_disc = QPushButton("Browse...")
        browse_disc.setMaximumWidth(80)
        browse_disc.clicked.connect(self._browse_disc)
        disc_row.addWidget(browse_disc)
        disc_layout.addLayout(disc_row)

        folder_row = QHBoxLayout()
        folder_row.addWidget(QLabel("Folder:"))
        self.folder_edit = QLineEdit(self._folder_path)
        self.folder_edit.setPlaceholderText("Extracted game folder (for PC versions)")
        folder_row.addWidget(self.folder_edit, stretch=1)
        browse_folder = QPushButton("Browse...")
        browse_folder.setMaximumWidth(80)
        browse_folder.clicked.connect(self._browse_folder)
        folder_row.addWidget(browse_folder)
        detect_btn = QPushButton("Detect")
        detect_btn.setMaximumWidth(60)
        detect_btn.clicked.connect(self._detect_all)
        folder_row.addWidget(detect_btn)
        disc_layout.addLayout(folder_row)

        # Game info labels
        self.game_label    = QLabel("Game: —")
        self.platform_label = QLabel("Platform: —")
        self.game_label.setFont(QFont("Courier New", 9))
        self.platform_label.setFont(QFont("Courier New", 9))
        disc_layout.addWidget(self.game_label)
        disc_layout.addWidget(self.platform_label)

        layout.addWidget(disc_grp)

        # Emulator list
        emu_grp = QGroupBox("Available Emulators")
        emu_layout = QVBoxLayout(emu_grp)

        self.emu_tree = QTreeWidget()
        self.emu_tree.setColumnCount(3)
        self.emu_tree.setHeaderLabels(["Emulator", "Platform", "Path"])
        self.emu_tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.emu_tree.header().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.emu_tree.header().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.emu_tree.setFont(QFont("Courier New", 8))
        self.emu_tree.setMaximumHeight(160)
        self.emu_tree.itemClicked.connect(self._on_emulator_selected)
        emu_layout.addWidget(self.emu_tree)

        # Wine/dgVoodoo note
        self.wine_label = QLabel("")
        self.wine_label.setFont(QFont("Courier New", 8))
        self.wine_label.setStyleSheet("color: #aaa;")
        self.wine_label.setWordWrap(True)
        emu_layout.addWidget(self.wine_label)

        layout.addWidget(emu_grp)

        # Log
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setMaximumHeight(80)
        self.log_box.setFont(QFont("Courier New", 8))
        layout.addWidget(self.log_box)

        # Buttons
        btn_row = QHBoxLayout()
        self.launch_btn = QPushButton("Launch in Emulator")
        self.launch_btn.setEnabled(False)
        self.launch_btn.clicked.connect(self._launch)

        self.launch_pc_btn = QPushButton("Launch PC Version")
        self.launch_pc_btn.setEnabled(False)
        self.launch_pc_btn.clicked.connect(self._launch_pc)

        self.folder_btn = QPushButton("Open Folder")
        self.folder_btn.clicked.connect(self._open_folder)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)

        btn_row.addWidget(self.launch_btn)
        btn_row.addWidget(self.launch_pc_btn)
        btn_row.addWidget(self.folder_btn)
        btn_row.addStretch()
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

        self._selected_emulator: Optional[EmulatorInfo] = None

    def _browse_disc(self): #vers 1
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Disc Image", "",
            "Disc Images (*.iso *.bin *.cue *.ccd *.img *.gcz *.rvz *.wia);;All Files (*)")
        if path:
            self.disc_edit.setText(path)
            self._detect_all()

    def _browse_folder(self): #vers 1
        folder = QFileDialog.getExistingDirectory(self, "Select Game Folder")
        if folder:
            self.folder_edit.setText(folder)
            self._detect_all()

    def _detect_all(self): #vers 1
        """Detect game version and available emulators."""
        disc   = self.disc_edit.text().strip()
        folder = self.folder_edit.text().strip()

        # Identify game
        ver  = GameVersion.UNKNOWN
        plat = Platform.UNKNOWN

        if disc and os.path.exists(disc):
            from apps.core.re_launchers import identify_disc
            ver, plat = identify_disc(disc)

        if ver == GameVersion.UNKNOWN and folder and os.path.isdir(folder):
            from apps.core.re_launchers import identify_folder
            ver, plat = identify_folder(folder)

        self.game_label.setText(f"Game: {ver.value}")
        self.platform_label.setText(f"Platform: {plat.value}")
        color = PLATFORM_COLORS.get(plat, QColor(140, 140, 140))
        self.platform_label.setStyleSheet(f"color: rgb({color.red()},{color.green()},{color.blue()});")

        # Detect emulators
        self._emulators = detect_emulators()
        self._populate_emulators(plat)

        # Enable PC launch if folder has executable
        if folder and os.path.isdir(folder):
            from apps.core.re_launchers import find_pc_executable
            exe = find_pc_executable(folder)
            self.launch_pc_btn.setEnabled(bool(exe))
            if exe:
                self._log(f"Found PC executable: {os.path.basename(exe)}")

        # Wine note
        from apps.core.re_launchers import detect_wine
        wine = detect_wine()
        if plat == Platform.PC_WIN98:
            if wine:
                self.wine_label.setText(
                    f"Wine: {wine}\n"
                    "Tip: RE1/RE2/RE3 PC may need dgVoodoo2 ddraw.dll override for DirectX.")
            else:
                self.wine_label.setText(
                    "Wine not found. Install with: sudo apt install wine\n"
                    "Needed to run Win98-era PC versions of RE1/RE2/RE3.")
        else:
            self.wine_label.setText("")

    def _populate_emulators(self, preferred_platform: Platform): #vers 1
        self.emu_tree.clear()
        self._selected_emulator = None
        self.launch_btn.setEnabled(False)

        # Show preferred platform first, then others
        platforms_order = [preferred_platform] + [
            p for p in Platform if p != preferred_platform and p != Platform.UNKNOWN]

        first = True
        for plat in platforms_order:
            emus = self._emulators.get(plat, [])
            if not emus:
                continue
            for emu in emus:
                color = PLATFORM_COLORS.get(plat, QColor(140, 140, 140))
                row = QTreeWidgetItem([emu.name, plat.value, emu.path])
                row.setData(0, Qt.ItemDataRole.UserRole, emu)
                row.setForeground(1, color)
                if emu.notes:
                    row.setToolTip(0, emu.notes)
                self.emu_tree.addTopLevelItem(row)
                if first:
                    self.emu_tree.setCurrentItem(row)
                    self._selected_emulator = emu
                    self.launch_btn.setEnabled(True)
                    first = False

        if not self.emu_tree.topLevelItemCount():
            none_row = QTreeWidgetItem(["No emulators found", "", ""])
            none_row.setForeground(0, QColor(140, 80, 80))
            self.emu_tree.addTopLevelItem(none_row)
            self._log("No emulators found. Install DuckStation, Dolphin, or Mednafen.")

    def _on_emulator_selected(self, item): #vers 1
        emu = item.data(0, Qt.ItemDataRole.UserRole)
        if emu:
            self._selected_emulator = emu
            self.launch_btn.setEnabled(True)

    def _launch(self): #vers 1
        """Launch disc in selected emulator."""
        disc = self.disc_edit.text().strip()
        if not disc or not os.path.exists(disc):
            QMessageBox.warning(self, "Launch", "Please select a valid disc image.")
            return
        emu = self._selected_emulator
        ok, msg = launch_disc(disc, emu)
        self._log(msg, error=not ok)
        if not ok:
            QMessageBox.warning(self, "Launch Failed", msg)

    def _launch_pc(self): #vers 1
        """Launch PC version from folder."""
        folder = self.folder_edit.text().strip()
        if not folder or not os.path.isdir(folder):
            QMessageBox.warning(self, "Launch", "Please select the game folder.")
            return
        ok, msg = launch_pc_folder(folder)
        self._log(msg, error=not ok)
        if not ok:
            QMessageBox.warning(self, "Launch Failed", msg)

    def _open_folder(self): #vers 1
        path = self.folder_edit.text().strip() or self.disc_edit.text().strip()
        if path:
            ok, msg = open_in_filemanager(path)
            self._log(msg, error=not ok)

    def _log(self, msg: str, error: bool = False): #vers 1
        color = "#cc6666" if error else "#aaaaaa"
        self.log_box.append(f'<span style="color:{color};">{msg}</span>')
        self.log_box.verticalScrollBar().setValue(
            self.log_box.verticalScrollBar().maximum())
