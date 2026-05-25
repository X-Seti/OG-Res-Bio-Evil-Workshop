#!/usr/bin/env python3
#this belongs in apps/gui/settings_dialog.py - Version: 1
# X-Seti - May25 2026 - ResBio-Evil-Workshop - Settings Dialog
"""
ResBio Settings Dialog
Tabs:
  Game Paths   - register RE game folders per version/platform
  Emulators    - configure emulator paths and launch options
  Viewer       - display options for room map, floor plan, stage map
  Audio        - volume, VAG sample rate, audio device
  Display      - theme, fonts, UI scaling
  About        - version info, credits, links
"""

import os
from typing import Optional

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTabWidget, QWidget, QGroupBox, QFormLayout,
    QCheckBox, QSlider, QSpinBox, QComboBox, QTreeWidget,
    QTreeWidgetItem, QFileDialog, QHeaderView, QFrame,
    QTextEdit, QSplitter, QFontComboBox, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QDesktopServices
from PyQt6.QtCore import QUrl

##Methods list -
# _build_paths_tab
# _build_emulators_tab
# _build_viewer_tab
# _build_audio_tab
# _build_display_tab
# _build_about_tab
# _add_game_path
# _remove_game_path
# _browse_emulator
# _save_settings
# _load_settings
# _apply

##class ResBioSettingsDialog:


class ResBioSettingsDialog(QDialog): #vers 1

    settings_changed = pyqtSignal()

    def __init__(self, main_window, parent=None): #vers 1
        super().__init__(parent)
        self.main_window = main_window
        self.setWindowTitle("Settings \u2014 ResBio-Evil Workshop")
        self.resize(720, 580)
        self.setModal(True)
        self._build_ui()
        self._load_settings()

    def _build_ui(self): #vers 1
        layout = QVBoxLayout(self)
        layout.setSpacing(4)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_paths_tab(),     "Game Paths")
        self.tabs.addTab(self._build_emulators_tab(), "Emulators")
        self.tabs.addTab(self._build_viewer_tab(),    "Viewer")
        self.tabs.addTab(self._build_audio_tab(),     "Audio")
        self.tabs.addTab(self._build_display_tab(),   "Display")
        self.tabs.addTab(self._build_about_tab(),     "About")
        layout.addWidget(self.tabs)

        # Bottom buttons
        btn_row = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self._save_settings)
        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(self._apply)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        btn_row.addWidget(save_btn)
        btn_row.addWidget(apply_btn)
        btn_row.addStretch()
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

    # --- Game Paths tab ---

    def _build_paths_tab(self) -> QWidget: #vers 1
        w = QScrollArea()
        inner = QWidget()
        layout = QVBoxLayout(inner)
        layout.setSpacing(8)

        info = QLabel(
            "Register your game installation folders here.\n"
            "These appear in the Menu → Game Paths for quick access.")
        info.setFont(QFont("Courier New", 8))
        info.setStyleSheet("color: #888;")
        layout.addWidget(info)

        # Path list
        self.paths_tree = QTreeWidget()
        self.paths_tree.setColumnCount(3)
        self.paths_tree.setHeaderLabels(["Label", "Platform", "Path"])
        self.paths_tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.paths_tree.header().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.paths_tree.header().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.paths_tree.setFont(QFont("Courier New", 8))
        self.paths_tree.setMinimumHeight(180)
        layout.addWidget(self.paths_tree)

        # Add path controls
        add_grp = QGroupBox("Add Game Path")
        add_form = QFormLayout(add_grp)

        self.path_label_edit = QLineEdit()
        self.path_label_edit.setPlaceholderText('e.g. "Biohazard PS1 Japan"')
        add_form.addRow("Label:", self.path_label_edit)

        platform_row = QHBoxLayout()
        self.path_platform_combo = QComboBox()
        self.path_platform_combo.addItems([
            "PlayStation 1", "Sega Saturn", "Nintendo GameCube",
            "PC (Win98 era)", "PC (Modern/GOG)", "Unknown"])
        platform_row.addWidget(self.path_platform_combo)
        add_form.addRow("Platform:", platform_row)

        path_row = QHBoxLayout()
        self.path_folder_edit = QLineEdit()
        self.path_folder_edit.setPlaceholderText("Folder path")
        path_row.addWidget(self.path_folder_edit, stretch=1)
        browse_btn = QPushButton("Browse...")
        browse_btn.setMaximumWidth(80)
        browse_btn.clicked.connect(self._browse_game_path)
        path_row.addWidget(browse_btn)
        add_form.addRow("Folder:", path_row)

        add_btn_row = QHBoxLayout()
        add_btn = QPushButton("Add Path")
        add_btn.clicked.connect(self._add_game_path)
        remove_btn = QPushButton("Remove Selected")
        remove_btn.clicked.connect(self._remove_game_path)
        add_btn_row.addWidget(add_btn)
        add_btn_row.addWidget(remove_btn)
        add_btn_row.addStretch()
        add_form.addRow("", add_btn_row)
        layout.addWidget(add_grp)

        # Auto-detect button
        detect_btn = QPushButton("Auto-detect game paths from common locations")
        detect_btn.clicked.connect(self._auto_detect_paths)
        layout.addWidget(detect_btn)
        layout.addStretch()

        w.setWidget(inner)
        w.setWidgetResizable(True)
        return w

    # --- Emulators tab ---

    def _build_emulators_tab(self) -> QWidget: #vers 1
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(6)

        info = QLabel("Configure emulator paths. Leave blank to auto-detect from PATH.")
        info.setFont(QFont("Courier New", 8))
        info.setStyleSheet("color: #888;")
        layout.addWidget(info)

        # Detected emulators
        detected_grp = QGroupBox("Detected Emulators")
        det_layout = QVBoxLayout(detected_grp)
        self.detected_tree = QTreeWidget()
        self.detected_tree.setColumnCount(3)
        self.detected_tree.setHeaderLabels(["Name", "Platform", "Path"])
        self.detected_tree.setFont(QFont("Courier New", 8))
        self.detected_tree.setMaximumHeight(120)
        self.detected_tree.header().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        det_layout.addWidget(self.detected_tree)
        detect_btn = QPushButton("Scan for Emulators")
        detect_btn.clicked.connect(self._scan_emulators)
        det_layout.addWidget(detect_btn)
        layout.addWidget(detected_grp)

        # Manual paths
        manual_grp = QGroupBox("Manual Emulator Paths")
        manual_form = QFormLayout(manual_grp)

        self.emu_paths = {}
        for name, placeholder in [
            ("DuckStation",  "duckstation-qt or duckstation"),
            ("Dolphin",      "dolphin-emu"),
            ("Mednafen",     "mednafen"),
            ("RetroArch",    "retroarch"),
            ("Wine",         "wine or wine64"),
        ]:
            row = QHBoxLayout()
            edit = QLineEdit()
            edit.setPlaceholderText(placeholder)
            row.addWidget(edit, stretch=1)
            btn = QPushButton("...")
            btn.setMaximumWidth(30)
            btn.clicked.connect(lambda checked, e=edit: self._browse_emulator(e))
            row.addWidget(btn)
            manual_form.addRow(f"{name}:", row)
            self.emu_paths[name] = edit

        layout.addWidget(manual_grp)

        # Wine options
        wine_grp = QGroupBox("Wine Options (for Win98 PC versions)")
        wine_form = QFormLayout(wine_grp)
        self.wine_prefix_edit = QLineEdit(
            os.path.expanduser("~/.wine_resbio"))
        wine_form.addRow("Wine prefix:", self.wine_prefix_edit)
        self.dgvoodoo_check = QCheckBox(
            "Use dgVoodoo2 ddraw.dll (recommended for RE1/RE2/RE3 PC)")
        wine_form.addRow("", self.dgvoodoo_check)
        dgvoodoo_row = QHBoxLayout()
        self.dgvoodoo_path_edit = QLineEdit()
        self.dgvoodoo_path_edit.setPlaceholderText("Path to dgVoodoo2 folder")
        dgvoodoo_row.addWidget(self.dgvoodoo_path_edit, stretch=1)
        dg_btn = QPushButton("...")
        dg_btn.setMaximumWidth(30)
        dg_btn.clicked.connect(lambda: self._browse_folder(self.dgvoodoo_path_edit))
        dgvoodoo_row.addWidget(dg_btn)
        wine_form.addRow("dgVoodoo2:", dgvoodoo_row)
        layout.addWidget(wine_grp)
        layout.addStretch()
        return w

    # --- Viewer tab ---

    def _build_viewer_tab(self) -> QWidget: #vers 1
        w = QScrollArea()
        inner = QWidget()
        layout = QVBoxLayout(inner)
        layout.setSpacing(6)

        # Room Map
        rm_grp = QGroupBox("Room Map Editor")
        rm_form = QFormLayout(rm_grp)
        self.show_grid_check      = QCheckBox("Show grid")
        self.show_cameras_check   = QCheckBox("Show camera positions")
        self.show_items_check     = QCheckBox("Show item markers")
        self.show_collision_check = QCheckBox("Show collision boundaries")
        self.show_doors_check     = QCheckBox("Show door markers")
        for cb in [self.show_grid_check, self.show_cameras_check,
                   self.show_items_check, self.show_collision_check,
                   self.show_doors_check]:
            cb.setChecked(True)
            rm_form.addRow("", cb)
        layout.addWidget(rm_grp)

        # Stage Map
        sm_grp = QGroupBox("Stage Map")
        sm_form = QFormLayout(sm_grp)
        self.show_thumbnails_check = QCheckBox("Show room thumbnails (loads BSS/PAK backgrounds)")
        self.show_thumbnails_check.setChecked(True)
        self.show_room_names_check = QCheckBox("Show room names")
        self.show_room_names_check.setChecked(True)
        self.show_arrows_check     = QCheckBox("Show connection arrows")
        self.show_arrows_check.setChecked(True)
        for cb in [self.show_thumbnails_check, self.show_room_names_check,
                   self.show_arrows_check]:
            sm_form.addRow("", cb)
        layout.addWidget(sm_grp)

        # Floor Plan
        fp_grp = QGroupBox("Floor Plan")
        fp_form = QFormLayout(fp_grp)
        self.fp_show_items_check   = QCheckBox("Show items")
        self.fp_show_cameras_check = QCheckBox("Show cameras")
        self.fp_show_labels_check  = QCheckBox("Show labels")
        self.fp_show_items_check.setChecked(True)
        self.fp_show_cameras_check.setChecked(True)
        self.fp_show_labels_check.setChecked(True)
        for cb in [self.fp_show_items_check, self.fp_show_cameras_check,
                   self.fp_show_labels_check]:
            fp_form.addRow("", cb)
        layout.addWidget(fp_grp)

        # Background loading
        bg_grp = QGroupBox("Backgrounds")
        bg_form = QFormLayout(bg_grp)
        self.load_bss_check = QCheckBox("Decode BSS backgrounds (MDEC decoder - may be slow)")
        self.load_bss_check.setChecked(True)
        self.load_pak_check = QCheckBox("Load PAK backgrounds (RE1 PC)")
        self.load_pak_check.setChecked(True)
        bg_form.addRow("", self.load_bss_check)
        bg_form.addRow("", self.load_pak_check)
        layout.addWidget(bg_grp)

        layout.addStretch()
        w.setWidget(inner)
        w.setWidgetResizable(True)
        return w

    # --- Audio tab ---

    def _build_audio_tab(self) -> QWidget: #vers 1
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(6)

        vol_grp = QGroupBox("Volume")
        vol_form = QFormLayout(vol_grp)

        self.master_vol_slider = QSlider(Qt.Orientation.Horizontal)
        self.master_vol_slider.setRange(0, 100)
        self.master_vol_slider.setValue(70)
        vol_label = QLabel("70%")
        vol_label.setMinimumWidth(35)
        self.master_vol_slider.valueChanged.connect(
            lambda v: vol_label.setText(f"{v}%"))
        vol_row = QHBoxLayout()
        vol_row.addWidget(self.master_vol_slider)
        vol_row.addWidget(vol_label)
        vol_form.addRow("Master volume:", vol_row)
        layout.addWidget(vol_grp)

        vag_grp = QGroupBox("VAG Decoder")
        vag_form = QFormLayout(vag_grp)

        self.vag_rate_combo = QComboBox()
        self.vag_rate_combo.addItems(["11025", "22050", "44100"])
        self.vag_rate_combo.setCurrentText("22050")
        vag_form.addRow("Default sample rate:", self.vag_rate_combo)

        self.auto_play_check = QCheckBox(
            "Auto-play audio when loading a stage folder")
        self.auto_play_check.setChecked(False)
        vag_form.addRow("", self.auto_play_check)
        layout.addWidget(vag_grp)

        layout.addStretch()
        return w

    # --- Display tab ---

    def _build_display_tab(self) -> QWidget: #vers 1
        w = QScrollArea()
        inner = QWidget()
        layout = QVBoxLayout(inner)
        layout.setSpacing(6)

        # Theme
        theme_grp = QGroupBox("Theme")
        theme_form = QFormLayout(theme_grp)
        self.theme_combo = QComboBox()
        # Populate from app_settings if available
        mw = self.main_window
        if mw and hasattr(mw, 'app_settings') and mw.app_settings:
            themes = list(mw.app_settings.themes.keys())
            self.theme_combo.addItems(sorted(themes))
            current = mw.app_settings.current_settings.get('theme', '')
            if current in themes:
                self.theme_combo.setCurrentText(current)
        theme_form.addRow("Theme:", self.theme_combo)
        open_settings_btn = QPushButton("Open full Theme Editor...")
        open_settings_btn.clicked.connect(self._open_theme_editor)
        theme_form.addRow("", open_settings_btn)
        layout.addWidget(theme_grp)

        # Fonts
        font_grp = QGroupBox("Fonts")
        font_form = QFormLayout(font_grp)
        self.ui_font_combo = QFontComboBox()
        self.ui_font_size  = QSpinBox()
        self.ui_font_size.setRange(8, 16)
        self.ui_font_size.setValue(9)
        font_row = QHBoxLayout()
        font_row.addWidget(self.ui_font_combo, stretch=1)
        font_row.addWidget(self.ui_font_size)
        font_row.addWidget(QLabel("pt"))
        font_form.addRow("UI Font:", font_row)
        layout.addWidget(font_grp)

        # UI options
        ui_grp = QGroupBox("Interface")
        ui_form = QFormLayout(ui_grp)
        self.show_icons_check = QCheckBox("Show icons on buttons")
        self.show_icons_check.setChecked(True)
        self.show_statusbar_check = QCheckBox("Show status bar")
        self.show_statusbar_check.setChecked(True)
        self.single_click_check = QCheckBox("Single click loads room (vs double click)")
        self.single_click_check.setChecked(True)
        for cb in [self.show_icons_check, self.show_statusbar_check,
                   self.single_click_check]:
            ui_form.addRow("", cb)
        layout.addWidget(ui_grp)

        layout.addStretch()
        w.setWidget(inner)
        w.setWidgetResizable(True)
        return w

    # --- About tab ---

    def _build_about_tab(self) -> QWidget: #vers 1
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(8)

        from apps.version import APP_NAME, APP_VERSION, APP_BUILD, APP_AUTHOR
        title = QLabel(f"{APP_NAME}")
        title.setFont(QFont("Courier New", 14, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        version = QLabel(f"Version {APP_VERSION}  (build {APP_BUILD})")
        version.setFont(QFont("Courier New", 9))
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version.setStyleSheet("color: #888;")
        layout.addWidget(version)

        sep = QFrame(); sep.setFrameStyle(QFrame.Shape.HLine)
        layout.addWidget(sep)

        info = QTextEdit()
        info.setReadOnly(True)
        info.setFont(QFont("Courier New", 8))
        info.setHtml("""
<p><b>ResBio-Evil Workshop</b> is an open-source editor and room viewer
for Resident Evil 1, 2 and 3 on PS1, Saturn, GameCube and PC.</p>

<p><b>Supported platforms:</b><br>
PlayStation 1 (JP/US/EU) &bull; Sega Saturn (JP/US) &bull;
Nintendo GameCube &bull; PC (Win98) &bull; PC (GOG/Modern)</p>

<p><b>Features:</b><br>
&bull; Disc image browser (ISO/BIN/CUE/CCD/IMG/7z/RAR/ZIP)<br>
&bull; RDT room file parser (RE1/RE2/RE3)<br>
&bull; Item editor with write-back<br>
&bull; Floor plan viewer (in-game style)<br>
&bull; Stage map with room connections<br>
&bull; TIM texture viewer<br>
&bull; EMD/PLD wireframe model viewer<br>
&bull; SCD script hex browser + disassembly<br>
&bull; VAG/VB/HSB/WAV audio player<br>
&bull; BSS background MDEC decoder<br>
&bull; Game launcher (DuckStation/Dolphin/Mednafen/Wine)<br>
&bull; JSON room export</p>

<p><b>Reference implementation:</b><br>
reevengi-tools by Patrice Mandin (GPL v2+)<br>
MDEC decoder ported from depack_mdec.c</p>

<p><b>Author:</b> X-Seti &bull; <b>GitHub:</b>
<a href="https://github.com/X-Seti/OG-Res-Bio-Evil-Workshop">
OG-Res-Bio-Evil-Workshop</a></p>
        """)
        layout.addWidget(info, stretch=1)

        link_row = QHBoxLayout()
        github_btn = QPushButton("GitHub Repository")
        github_btn.clicked.connect(lambda: QDesktopServices.openUrl(
            QUrl("https://github.com/X-Seti/OG-Res-Bio-Evil-Workshop")))
        link_row.addWidget(github_btn)
        link_row.addStretch()
        layout.addLayout(link_row)
        return w

    # --- Actions ---

    def _browse_game_path(self): #vers 1
        folder = QFileDialog.getExistingDirectory(self, "Select Game Folder")
        if folder:
            self.path_folder_edit.setText(folder)
            mw = self.main_window
            rf = getattr(mw, '_recent_files', None) if mw else None
            if rf and not self.path_label_edit.text():
                self.path_label_edit.setText(rf.suggest_game_label(folder))

    def _add_game_path(self): #vers 1
        label  = self.path_label_edit.text().strip()
        folder = self.path_folder_edit.text().strip()
        plat   = self.path_platform_combo.currentText()
        if not label or not folder or not os.path.isdir(folder):
            return
        row = QTreeWidgetItem([label, plat, folder])
        self.paths_tree.addTopLevelItem(row)
        mw = self.main_window
        rf = getattr(mw, '_recent_files', None) if mw else None
        if rf:
            rf.add_game_path(label, folder)
        self.path_label_edit.clear()
        self.path_folder_edit.clear()

    def _remove_game_path(self): #vers 1
        item = self.paths_tree.currentItem()
        if not item:
            return
        label = item.text(0)
        mw = self.main_window
        rf = getattr(mw, '_recent_files', None) if mw else None
        if rf:
            rf.remove_game_path(label)
        root = self.paths_tree.invisibleRootItem()
        root.removeChild(item)

    def _browse_emulator(self, edit: QLineEdit): #vers 1
        path, _ = QFileDialog.getOpenFileName(self, "Select Emulator Executable")
        if path:
            edit.setText(path)

    def _browse_folder(self, edit: QLineEdit): #vers 1
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            edit.setText(folder)

    def _auto_detect_paths(self): #vers 1
        """Scan common locations for RE game folders."""
        common = [
            os.path.expanduser("~/games"),
            os.path.expanduser("~/Games"),
            "/games", "/mnt/games", "/media",
            os.path.expanduser("~/.local/share/lutris/runners/wine/prefix"),
        ]
        found = 0
        for base in common:
            if not os.path.isdir(base):
                continue
            for entry in os.listdir(base):
                full = os.path.join(base, entry)
                if not os.path.isdir(full):
                    continue
                lower = entry.lower()
                if any(k in lower for k in ['resident', 'evil', 'biohazard', 're1', 're2', 're3']):
                    mw = self.main_window
                    rf = getattr(mw, '_recent_files', None) if mw else None
                    if rf:
                        label = rf.suggest_game_label(full) or entry
                        rf.add_game_path(label, full)
                    row = QTreeWidgetItem([entry, "Auto-detected", full])
                    self.paths_tree.addTopLevelItem(row)
                    found += 1
        if not found:
            row = QTreeWidgetItem(["(none found)", "", ""])
            row.setForeground(0, QColor(140, 80, 80))
            self.paths_tree.addTopLevelItem(row)

    def _scan_emulators(self): #vers 1
        """Scan and populate detected emulators tree."""
        from apps.core.re_launchers import detect_emulators, Platform
        self.detected_tree.clear()
        emus = detect_emulators()
        for plat, emu_list in emus.items():
            for emu in emu_list:
                row = QTreeWidgetItem([emu.name, plat.value, emu.path])
                self.detected_tree.addTopLevelItem(row)
        if not self.detected_tree.topLevelItemCount():
            row = QTreeWidgetItem(["No emulators found", "", ""])
            row.setForeground(0, QColor(140, 80, 80))
            self.detected_tree.addTopLevelItem(row)

    def _open_theme_editor(self): #vers 1
        mw = self.main_window
        if mw and hasattr(mw, '_show_settings_dialog'):
            mw._show_settings_dialog()

    def _load_settings(self): #vers 1
        """Populate controls from saved settings."""
        mw = self.main_window
        rf = getattr(mw, '_recent_files', None) if mw else None

        # Game paths
        if rf:
            for label, path in rf.get_game_paths().items():
                row = QTreeWidgetItem([label, "", path])
                self.paths_tree.addTopLevelItem(row)

        # Emulator scan
        self._scan_emulators()

        # App settings
        if mw and hasattr(mw, 'app_settings') and mw.app_settings:
            s = mw.app_settings.current_settings
            vol = s.get('audio_volume', 70)
            self.master_vol_slider.setValue(vol)

    def _save_settings(self): #vers 1
        """Save all settings."""
        mw = self.main_window
        if mw and hasattr(mw, 'app_settings') and mw.app_settings:
            s = mw.app_settings.current_settings
            s['audio_volume']   = self.master_vol_slider.value()
            s['vag_sample_rate'] = int(self.vag_rate_combo.currentText())
            s['auto_play_audio'] = self.auto_play_check.isChecked()
            s['show_thumbnails'] = self.show_thumbnails_check.isChecked()
            s['load_bss']        = self.load_bss_check.isChecked()
            s['load_pak']        = self.load_pak_check.isChecked()
            s['single_click']    = self.single_click_check.isChecked()
            # Theme
            theme = self.theme_combo.currentText()
            if theme:
                s['theme'] = theme
            try:
                mw.app_settings.save_settings()
            except Exception as e:
                print(f"Settings save error: {e}")

        # Apply volume to audio player
        if mw and hasattr(mw, 'audio_player') and mw.audio_player:
            mw.audio_player.set_volume(
                self.master_vol_slider.value() / 100.0)

        self.settings_changed.emit()
        self._apply()

    def _apply(self): #vers 1
        """Apply settings without closing."""
        mw = self.main_window
        if not mw:
            return
        # Apply theme
        theme = self.theme_combo.currentText()
        if theme and hasattr(mw, 'app_settings') and mw.app_settings:
            mw.app_settings.current_settings['theme'] = theme
            if hasattr(mw, '_on_theme_changed'):
                mw._on_theme_changed()
        # Apply floor plan toggles
        if hasattr(mw, 'floor_plan') and mw.floor_plan:
            c = mw.floor_plan.canvas
            c.show_items   = self.fp_show_items_check.isChecked()
            c.show_cameras = self.fp_show_cameras_check.isChecked()
            c.show_labels  = self.fp_show_labels_check.isChecked()
            c.update()
