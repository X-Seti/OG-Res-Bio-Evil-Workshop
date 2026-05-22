#!/usr/bin/env python3
#this belongs in apps/gui/unpack_dialog.py - Version: 1
# X-Seti - May22 2026 - ResBio-Evil-Workshop - Unpack Dialog
"""
Unpack Dialog - Detect game version, list all known files,
extract archives (ROFS, BIN), decompress PAK/PRS/BSS on demand.
Works for RE1/RE2/RE3 PS1 and PC.
"""

import os
from typing import Optional, List

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFileDialog, QTreeWidget, QTreeWidgetItem,
    QProgressBar, QTextEdit, QFrame, QSplitter, QHeaderView,
    QMessageBox, QAbstractItemView
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QObject
from PyQt6.QtGui import QFont, QColor

from apps.core.re_unpacker import (
    detect_game_version, scan_game_folder, unpack_file,
    extract_rofs, extract_bin_re2, GameVersion, GameFolder
)

##Methods list -
# _browse_source
# _browse_output
# _detect_version
# _scan_folder
# _populate_tree
# _on_tree_selection_changed
# _extract_selected
# _extract_all
# _unpack_single
# _log

##class ScanWorker:
##class UnpackDialog:


class ScanWorker(QObject): #vers 1
    """Background worker for scanning game folder."""
    finished = pyqtSignal(object)   # GameFolder
    error    = pyqtSignal(str)

    def __init__(self, folder_path: str): #vers 1
        super().__init__()
        self.folder_path = folder_path

    def run(self): #vers 1
        try:
            gf = scan_game_folder(self.folder_path)
            self.finished.emit(gf)
        except Exception as e:
            self.error.emit(str(e))


class UnpackDialog(QDialog): #vers 1
    """Main unpack dialog."""

    files_extracted = pyqtSignal(str)   # output folder path

    def __init__(self, parent=None, initial_path: str = ''): #vers 1
        super().__init__(parent)
        self.setWindowTitle("RE File Unpacker")
        self.resize(820, 580)
        self.setModal(False)
        self._game_folder: Optional[GameFolder] = None
        self._scan_thread: Optional[QThread] = None
        self._build_ui(initial_path)

    def _build_ui(self, initial_path: str = ''): #vers 1
        layout = QVBoxLayout(self)
        layout.setSpacing(6)

        # --- Source row ---
        src_row = QHBoxLayout()
        src_row.addWidget(QLabel("Game folder:"))
        self.src_edit = QLineEdit(initial_path)
        self.src_edit.setPlaceholderText("Path to game folder (STAGE/, ROOM/, etc.)")
        src_row.addWidget(self.src_edit, stretch=1)
        browse_src_btn = QPushButton("Browse...")
        browse_src_btn.setMaximumWidth(80)
        browse_src_btn.clicked.connect(self._browse_source)
        src_row.addWidget(browse_src_btn)
        self.scan_btn = QPushButton("Scan")
        self.scan_btn.setMaximumWidth(60)
        self.scan_btn.clicked.connect(self._scan_folder)
        src_row.addWidget(self.scan_btn)
        layout.addLayout(src_row)

        # --- Output row ---
        out_row = QHBoxLayout()
        out_row.addWidget(QLabel("Output folder:"))
        self.out_edit = QLineEdit()
        self.out_edit.setPlaceholderText("Where to extract files (default: game folder/extracted)")
        out_row.addWidget(self.out_edit, stretch=1)
        browse_out_btn = QPushButton("Browse...")
        browse_out_btn.setMaximumWidth(80)
        browse_out_btn.clicked.connect(self._browse_output)
        out_row.addWidget(browse_out_btn)
        layout.addLayout(out_row)

        # --- Version label ---
        self.version_label = QLabel("Version: not detected")
        self.version_label.setFont(QFont("Courier New", 9))
        layout.addWidget(self.version_label)

        sep = QFrame(); sep.setFrameStyle(QFrame.Shape.HLine)
        layout.addWidget(sep)

        # --- Main splitter: tree + log ---
        splitter = QSplitter(Qt.Orientation.Vertical)

        # File tree
        self.tree = QTreeWidget()
        self.tree.setColumnCount(4)
        self.tree.setHeaderLabels(["File", "Type", "Size", "Status"])
        self.tree.setAlternatingRowColors(True)
        self.tree.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tree.header().resizeSection(1, 80)
        self.tree.header().resizeSection(2, 80)
        self.tree.header().resizeSection(3, 100)
        self.tree.setFont(QFont("Courier New", 8))
        splitter.addWidget(self.tree)

        # Log
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setMaximumHeight(120)
        self.log_box.setFont(QFont("Courier New", 8))
        splitter.addWidget(self.log_box)
        splitter.setSizes([400, 120])

        layout.addWidget(splitter, stretch=1)

        # --- Progress ---
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        # --- Buttons ---
        btn_row = QHBoxLayout()
        self.extract_sel_btn = QPushButton("Extract Selected")
        self.extract_sel_btn.setEnabled(False)
        self.extract_sel_btn.clicked.connect(self._extract_selected)
        self.extract_all_btn = QPushButton("Extract All")
        self.extract_all_btn.setEnabled(False)
        self.extract_all_btn.clicked.connect(self._extract_all)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        btn_row.addWidget(self.extract_sel_btn)
        btn_row.addWidget(self.extract_all_btn)
        btn_row.addStretch()
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

        self.tree.itemSelectionChanged.connect(self._on_tree_selection_changed)

    # --- Source / output browsing ---

    def _browse_source(self): #vers 1
        folder = QFileDialog.getExistingDirectory(self, "Select Game Folder")
        if folder:
            self.src_edit.setText(folder)
            self.out_edit.setText(os.path.join(folder, "extracted"))
            self._scan_folder()

    def _browse_output(self): #vers 1
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.out_edit.setText(folder)

    # --- Scan ---

    def _scan_folder(self): #vers 1
        folder = self.src_edit.text().strip()
        if not folder or not os.path.isdir(folder):
            QMessageBox.warning(self, "Scan", "Please select a valid game folder.")
            return

        if not self.out_edit.text():
            self.out_edit.setText(os.path.join(folder, "extracted"))

        self.scan_btn.setEnabled(False)
        self.tree.clear()
        self._log(f"Scanning: {folder}")

        # Run in thread
        self._scan_worker = ScanWorker(folder)
        self._scan_thread = QThread()
        self._scan_worker.moveToThread(self._scan_thread)
        self._scan_thread.started.connect(self._scan_worker.run)
        self._scan_worker.finished.connect(self._on_scan_done)
        self._scan_worker.error.connect(self._on_scan_error)
        self._scan_worker.finished.connect(self._scan_thread.quit)
        self._scan_thread.start()

    def _on_scan_done(self, gf: GameFolder): #vers 1
        self.scan_btn.setEnabled(True)
        self._game_folder = gf
        version_str = gf.version.value
        self.version_label.setText(f"Version: {version_str}")
        color = "#88cc88" if gf.version != GameVersion.UNKNOWN else "#cc8888"
        self.version_label.setStyleSheet(f"color: {color};")
        self._populate_tree(gf)
        self.extract_all_btn.setEnabled(gf.total_files > 0)
        self._log(f"Found: {len(gf.rdt_files)} RDT  {len(gf.texture_files)} textures  "
                  f"{len(gf.model_files)} models  {len(gf.archive_files)} archives")
        if gf.errors:
            for e in gf.errors:
                self._log(f"  ! {e}", error=True)

    def _on_scan_error(self, msg: str): #vers 1
        self.scan_btn.setEnabled(True)
        self._log(f"Scan error: {msg}", error=True)

    def _populate_tree(self, gf: GameFolder): #vers 1
        self.tree.clear()
        categories = [
            ("RDT Room Files",  gf.rdt_files),
            ("Textures",        gf.texture_files),
            ("Models",          gf.model_files),
            ("Archives",        gf.archive_files),
        ]
        for cat_name, files in categories:
            if not files:
                continue
            cat_item = QTreeWidgetItem([cat_name, "", f"{len(files)} files", ""])
            cat_item.setFont(0, QFont("Courier New", 8, QFont.Weight.Bold))
            cat_item.setForeground(0, QColor(150, 190, 230))
            self.tree.addTopLevelItem(cat_item)

            for gfile in files:
                size_str = f"{gfile.size:,}B"
                status = "compressed" if gfile.compressed else "raw"
                row = QTreeWidgetItem([
                    os.path.relpath(gfile.path, gf.root_path),
                    gfile.file_type,
                    size_str,
                    status,
                ])
                row.setData(0, Qt.ItemDataRole.UserRole, gfile)
                if gfile.compressed:
                    row.setForeground(3, QColor(200, 160, 80))
                cat_item.addChild(row)

            cat_item.setExpanded(True)

    # --- Selection ---

    def _on_tree_selection_changed(self): #vers 1
        items = [i for i in self.tree.selectedItems() if i.parent()]
        self.extract_sel_btn.setEnabled(len(items) > 0)

    # --- Extraction ---

    def _get_output_dir(self) -> str: #vers 1
        out = self.out_edit.text().strip()
        if not out and self._game_folder:
            out = os.path.join(self._game_folder.root_path, "extracted")
        return out

    def _extract_selected(self): #vers 1
        items = [i for i in self.tree.selectedItems() if i.parent()]
        if not items:
            return
        out_dir = self._get_output_dir()
        self.progress.setVisible(True)
        self.progress.setMaximum(len(items))
        for i, item in enumerate(items):
            gfile = item.data(0, Qt.ItemDataRole.UserRole)
            if gfile:
                ok, fmt, result = self._unpack_single(gfile, out_dir)
                status = "done" if ok else "error"
                item.setText(3, status)
                item.setForeground(3, QColor(100, 200, 100) if ok else QColor(220, 80, 80))
            self.progress.setValue(i + 1)
        self.progress.setVisible(False)
        self._log(f"Extracted {len(items)} files to: {out_dir}")
        self.files_extracted.emit(out_dir)

    def _extract_all(self): #vers 1
        if not self._game_folder:
            return
        all_files = (self._game_folder.rdt_files +
                     self._game_folder.texture_files +
                     self._game_folder.model_files +
                     self._game_folder.archive_files)
        out_dir = self._get_output_dir()
        self.progress.setVisible(True)
        self.progress.setMaximum(len(all_files))
        done = 0
        for i, gfile in enumerate(all_files):
            ok, fmt, _ = self._unpack_single(gfile, out_dir)
            if ok:
                done += 1
            self.progress.setValue(i + 1)
        self.progress.setVisible(False)
        self._log(f"Extracted {done}/{len(all_files)} files to: {out_dir}")
        self.files_extracted.emit(out_dir)

    def _unpack_single(self, gfile, out_dir: str): #vers 1
        """Decompress/copy one file to output_dir, preserving relative path."""
        try:
            rel = os.path.relpath(gfile.path, self._game_folder.root_path)
            dest = os.path.join(out_dir, rel)
            os.makedirs(os.path.dirname(dest), exist_ok=True)

            ok, fmt, data = unpack_file(gfile.path, out_dir)
            if ok and data:
                with open(dest, 'wb') as f:
                    f.write(data)
                self._log(f"  {rel}  [{fmt}]  -> {len(data):,}B")
            return ok, fmt, data
        except Exception as e:
            self._log(f"  ERROR {gfile.name}: {e}", error=True)
            return False, '', b''

    def _log(self, msg: str, error: bool = False): #vers 1
        color = "#cc6666" if error else "#aaaaaa"
        self.log_box.append(f'<span style="color:{color};">{msg}</span>')
        self.log_box.verticalScrollBar().setValue(
            self.log_box.verticalScrollBar().maximum())
