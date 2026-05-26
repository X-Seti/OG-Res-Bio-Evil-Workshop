#!/usr/bin/env python3
#this belongs in apps/gui/disc_manager.py - Version: 2
# X-Seti - May22 2026 - ResBio-Evil-Workshop - Disc Manager
"""
Disc Manager - Open and extract PS1 disc images (ISO, BIN/CUE, CCD/IMG/SUB)
and compressed archives (7z, RAR, ZIP).
Features:
  - Folder scan to find all disc images
  - Proper nested directory tree matching ISO filesystem
  - Right-click context menu: view TIM/RDT/EMD/VAG files directly in viewers
  - Snapshot: save disc contents to JSON
  - Extract selected / RE files / all
  - Build ISO from folder
"""

import os
import json
import tempfile
from typing import Optional, Dict, List

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFileDialog, QTreeWidget, QTreeWidgetItem,
    QProgressBar, QTextEdit, QFrame, QSplitter, QHeaderView,
    QTabWidget, QWidget, QMessageBox, QAbstractItemView,
    QGroupBox, QMenu
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QObject, QPoint
from PyQt6.QtGui import QFont, QColor

from apps.core.disc_image import (
    open_disc, detect_format, build_iso,
    DiscImage, DiscFile, DiscFormat, ArchiveImage
)

##Methods list -
# _browse_folder
# _browse_output
# _scan_folder_for_discs
# _on_disc_double_clicked
# _open_disc
# _open_archive
# _populate_tree
# _build_tree_node
# _on_tree_context_menu
# _view_file_in_app
# _extract_temp_and_view
# _on_selection_changed
# _get_output_dir
# _extract_selected
# _extract_all_re_files
# _extract_all
# _save_snapshot
# _browse_build_source
# _browse_build_output
# _do_build_iso
# _log

##class DiscOpenWorker:
##class DiscManagerDialog:


# File type colours (based on real Biohazard disc snapshot)
COLORS = {
    # Room data
    '.RDT': QColor(100, 180, 255),   # room file - blue
    '.ARD': QColor(120, 160, 255),   # RE1.5 room data - blue
    '.BSS': QColor(160, 200, 120),   # background - green
    # Textures
    '.TIM': QColor(200, 160, 80),    # PSX texture - orange
    '.PIX': QColor(180, 140, 80),    # raw VRAM pixel - orange dim
    '.RGB': QColor(160, 120, 80),    # raw RGB - brown
    '.PAK': QColor(200, 130, 200),   # PC background - purple
    '.ADT': QColor(180, 110, 180),   # RE2 PC bg - purple dim
    # Models
    '.EMD': QColor(150, 220, 150),   # enemy model - green
    '.PLD': QColor(130, 200, 130),   # player model - green dim
    '.IVM': QColor(120, 200, 120),   # item model - green dim
    '.DOR': QColor(110, 180, 110),   # door model - green dim
    '.EMW': QColor(100, 170, 100),   # weapon attachment
    '.TMD': QColor(90,  160, 90),    # PS1 TMD model
    # Audio
    '.VAG': QColor(100, 200, 200),   # PS1 ADPCM
    '.WAV': QColor(100, 200, 200),   # PC audio
    '.SND': QColor(80,  180, 180),   # sound container
    '.HSB': QColor(80,  190, 190),   # biohazard sound bank
    '.VB':  QColor(70,  170, 170),   # voice bank (raw ADPCM)
    '.HED': QColor(60,  150, 150),   # sound index header
    '.XAS': QColor(60,  160, 160),   # XA audio stream
    # Video
    '.STR': QColor(200, 100, 100),   # FMV MDEC stream - red
    # Data
    '.BIN': QColor(160, 160, 160),
    '.DAT': QColor(160, 160, 160),
    '.ETM': QColor(150, 150, 170),   # effect texture
    '.ESP': QColor(150, 150, 170),   # effect sprite
}

# RE-relevant extensions (all game assets)
RE_EXTENSIONS = {
    '.RDT', '.TIM', '.EMD', '.PAK', '.BSS', '.ADT',
    '.PLD', '.EDD', '.BIN', '.DAT', '.SLD', '.PRS',
    '.VAG', '.WAV', '.SND', '.HSB', '.VB', '.HED',
    '.IVM', '.DOR', '.EMW', '.TMD', '.PIX', '.RGB',
    '.XAS', '.STR', '.ETM', '.ESP', '.PTC',
}

# What each extension can be opened in directly
VIEWERS = {
    '.RDT': 'room',
    '.TIM': 'texture',
    '.PIX': 'texture',   # raw VRAM - try as TIM
    '.PAK': 'texture',
    '.BSS': 'texture',
    '.EMD': 'model',
    '.PLD': 'model',
    '.IVM': 'model',
    '.TMD': 'model',
    '.DOR': 'model',
    '.EMW': 'model',
    '.VAG': 'audio',
    '.WAV': 'audio',
    '.SND': 'audio',
    '.VB':  'audio',
    '.HSB': 'audio',
}

# Human-readable descriptions for status bar
FILE_DESCRIPTIONS = {
    '.RDT': 'Room Data Table',
    '.BSS': 'Background (PS1 MDEC)',
    '.TIM': 'PS1 Texture',
    '.PIX': 'Raw VRAM Pixels',
    '.RGB': 'Raw RGB Image',
    '.EMD': 'Enemy Model',
    '.PLD': 'Player Model',
    '.IVM': 'Item Model',
    '.DOR': 'Door/Obstacle Model',
    '.EMW': 'Enemy Weapon Model',
    '.TMD': 'PS1 TMD Model',
    '.PAK': 'Packed Background (PC)',
    '.BSS': 'Background Screen (PS1)',
    '.ADT': 'Background (RE2 PC)',
    '.VAG': 'PS1 ADPCM Audio',
    '.VB':  'Voice Bank (ADPCM)',
    '.HED': 'Sound Bank Index',
    '.HSB': 'Biohazard Sound Bank',
    '.XAS': 'XA Audio Stream (BGM)',
    '.STR': 'FMV Video Stream',
    '.ETM': 'Effect Texture Map',
    '.ESP': 'Effect Sprite',
    '.PTC': 'Patch/Config Data',
}


class DiscOpenWorker(QObject): #vers 1
    finished = pyqtSignal(object)
    error    = pyqtSignal(str)
    progress = pyqtSignal(str)

    def __init__(self, path: str): #vers 1
        super().__init__()
        self.path = path

    def run(self): #vers 1
        try:
            self.progress.emit(f"Opening: {os.path.basename(self.path)}")
            disc = open_disc(self.path)
            if disc is None:
                self.error.emit(f"Unsupported format: {self.path}")
            else:
                self.progress.emit(f"Found {len(disc.list_files())} files")
                self.finished.emit(disc)
        except Exception as e:
            self.error.emit(str(e))


class DiscManagerDialog(QDialog): #vers 2

    stage_folder_ready = pyqtSignal(str)

    def __init__(self, parent=None): #vers 1
        super().__init__(parent)
        self.setWindowTitle("Disc Manager \u2014 ResBio-Evil Workshop")
        self.resize(1100, 720)
        self.setModal(False)
        self._disc: Optional[DiscImage] = None
        self._worker_thread: Optional[QThread] = None
        self._last_extracted_dir: str = ''
        self._build_ui()

    def _build_ui(self): #vers 1
        layout = QVBoxLayout(self)
        layout.setSpacing(4)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_open_tab(),  "Open / Extract")
        self.tabs.addTab(self._build_build_tab(), "Build ISO")
        layout.addWidget(self.tabs)

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setMaximumHeight(90)
        self.log_box.setFont(QFont("Courier New", 8))
        layout.addWidget(self.log_box)

    def _build_open_tab(self) -> QWidget: #vers 1
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(4)

        # Folder picker
        folder_row = QHBoxLayout()
        folder_row.addWidget(QLabel("Folder:"))
        self.folder_edit = QLineEdit()
        self.folder_edit.setPlaceholderText(
            "Folder containing disc images (.img .iso .bin .cue .ccd .7z .rar .zip)")
        folder_row.addWidget(self.folder_edit, stretch=1)
        browse_btn = QPushButton("Browse...")
        browse_btn.setMaximumWidth(80)
        browse_btn.clicked.connect(self._browse_folder)
        folder_row.addWidget(browse_btn)
        recent_btn = QPushButton("Recent")
        recent_btn.setMaximumWidth(60)
        recent_btn.setToolTip("Show recently opened disc images")
        recent_btn.clicked.connect(self._show_recent_discs_menu)
        folder_row.addWidget(recent_btn)
        layout.addLayout(folder_row)

        # Disc list
        layout.addWidget(QLabel("Disc images found:"))
        self.disc_list = QTreeWidget()
        self.disc_list.setColumnCount(3)
        self.disc_list.setHeaderLabels(["File", "Format", "Size"])
        self.disc_list.setMaximumHeight(110)
        self.disc_list.setAlternatingRowColors(True)
        self.disc_list.setFont(QFont("Courier New", 8))
        self.disc_list.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.disc_list.header().resizeSection(1, 140)
        self.disc_list.header().resizeSection(2, 80)
        self.disc_list.itemDoubleClicked.connect(self._on_disc_double_clicked)
        self.disc_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.disc_list.customContextMenuRequested.connect(self._on_disc_list_context_menu)
        layout.addWidget(self.disc_list)

        # Selected disc path
        open_row = QHBoxLayout()
        self.disc_edit = QLineEdit()
        self.disc_edit.setPlaceholderText("Disc image path")
        open_row.addWidget(self.disc_edit, stretch=1)
        self.open_btn = QPushButton("Open")
        self.open_btn.setMaximumWidth(60)
        self.open_btn.clicked.connect(self._open_disc)
        open_row.addWidget(self.open_btn)

        launch_btn = QPushButton("Launch")
        launch_btn.setMaximumWidth(65)
        launch_btn.setToolTip("Launch disc in emulator")
        launch_btn.clicked.connect(lambda: self._launch_disc())
        open_row.addWidget(launch_btn)

        snapshot_btn = QPushButton("Snapshot")
        snapshot_btn.setMaximumWidth(80)
        snapshot_btn.setToolTip("Save disc contents to JSON snapshot")
        snapshot_btn.clicked.connect(self._save_snapshot)
        open_row.addWidget(snapshot_btn)
        layout.addLayout(open_row)

        # Format label
        self.fmt_label = QLabel("Format: \u2014")
        self.fmt_label.setFont(QFont("Courier New", 8))
        layout.addWidget(self.fmt_label)

        # File tree
        self.tree = QTreeWidget()
        self.tree.setColumnCount(3)
        self.tree.setHeaderLabels(["Path", "Size", "Type"])
        self.tree.setAlternatingRowColors(True)
        self.tree.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tree.header().resizeSection(1, 80)
        self.tree.header().resizeSection(2, 60)
        self.tree.setFont(QFont("Courier New", 8))
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._on_tree_context_menu)
        layout.addWidget(self.tree, stretch=1)

        # Output row
        out_row = QHBoxLayout()
        out_row.addWidget(QLabel("Output:"))
        self.out_edit = QLineEdit()
        self.out_edit.setPlaceholderText("Extraction output folder")
        out_row.addWidget(self.out_edit, stretch=1)
        browse_out = QPushButton("Browse...")
        browse_out.setMaximumWidth(80)
        browse_out.clicked.connect(self._browse_output)
        out_row.addWidget(browse_out)
        layout.addLayout(out_row)

        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        btn_row = QHBoxLayout()
        self.ext_sel_btn = QPushButton("Extract Selected")
        self.ext_sel_btn.setEnabled(False)
        self.ext_sel_btn.clicked.connect(self._extract_selected)
        self.ext_re_btn  = QPushButton("Extract RE Files")
        self.ext_re_btn.setEnabled(False)
        self.ext_re_btn.setToolTip("Extract only RDT, TIM, EMD, PAK, BSS, VAG etc.")
        self.ext_re_btn.clicked.connect(self._extract_all_re_files)
        self.ext_all_btn = QPushButton("Extract All")
        self.ext_all_btn.setEnabled(False)
        self.ext_all_btn.clicked.connect(self._extract_all)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self._on_close)
        btn_row.addWidget(self.ext_sel_btn)
        btn_row.addWidget(self.ext_re_btn)
        btn_row.addWidget(self.ext_all_btn)
        btn_row.addStretch()
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

        self.tree.itemSelectionChanged.connect(self._on_selection_changed)
        return w

    def _build_build_tab(self) -> QWidget: #vers 1
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(8)

        grp = QGroupBox("Build ISO from folder")
        form = QVBoxLayout(grp)

        src_row = QHBoxLayout()
        src_row.addWidget(QLabel("Source folder:"))
        self.build_src_edit = QLineEdit()
        self.build_src_edit.setPlaceholderText("Extracted game files folder")
        src_row.addWidget(self.build_src_edit, stretch=1)
        src_btn = QPushButton("Browse...")
        src_btn.setMaximumWidth(80)
        src_btn.clicked.connect(self._browse_build_source)
        src_row.addWidget(src_btn)
        form.addLayout(src_row)

        out_row = QHBoxLayout()
        out_row.addWidget(QLabel("Output ISO: "))
        self.build_out_edit = QLineEdit()
        self.build_out_edit.setPlaceholderText("Output .iso path")
        out_row.addWidget(self.build_out_edit, stretch=1)
        out_btn = QPushButton("Browse...")
        out_btn.setMaximumWidth(80)
        out_btn.clicked.connect(self._browse_build_output)
        out_row.addWidget(out_btn)
        form.addLayout(out_row)

        lbl_row = QHBoxLayout()
        lbl_row.addWidget(QLabel("Volume label:"))
        self.vol_label_edit = QLineEdit("BIOHAZARD")
        lbl_row.addWidget(self.vol_label_edit)
        lbl_row.addStretch()
        form.addLayout(lbl_row)
        layout.addWidget(grp)

        note = QLabel(
            "Note: Builds a standard ISO9660 data disc.\n"
            "Does not include PS1 anti-piracy data or audio tracks.")
        note.setFont(QFont("Courier New", 8))
        note.setStyleSheet("color: #888;")
        layout.addWidget(note)

        self.build_progress = QProgressBar()
        self.build_progress.setVisible(False)
        layout.addWidget(self.build_progress)

        build_btn = QPushButton("Build ISO")
        build_btn.clicked.connect(self._do_build_iso)
        layout.addWidget(build_btn)
        layout.addStretch()
        return w

    # --- Folder / disc browsing ---

    def _browse_folder(self): #vers 1
        folder = QFileDialog.getExistingDirectory(self, "Select Folder with Disc Images")
        if folder:
            self.folder_edit.setText(folder)
            if not self.out_edit.text():
                self.out_edit.setText(os.path.join(folder, "extracted"))
            self._last_extracted_dir = os.path.join(folder, "extracted")
            self._scan_folder_for_discs(folder)

    def _browse_output(self): #vers 1
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.out_edit.setText(folder)

    def _scan_folder_for_discs(self, folder: str): #vers 1
        self.disc_list.clear()
        exts = {'.ISO', '.BIN', '.CUE', '.CCD', '.IMG', '.7Z', '.RAR', '.ZIP'}
        found = []
        for root, dirs, files in os.walk(folder):
            depth = root[len(folder):].count(os.sep)
            if depth > 2:
                dirs.clear()
                continue
            for fname in sorted(files):
                if os.path.splitext(fname)[1].upper() in exts:
                    found.append(os.path.join(root, fname))

        filtered = []
        for path in found:
            ext = os.path.splitext(path)[1].upper()
            if ext in ('.SUB', '.SBI'):
                continue
            if ext == '.IMG':
                ccd = os.path.splitext(path)[0] + '.ccd'
                if os.path.exists(ccd) or os.path.exists(ccd.upper()):
                    continue
            if ext == '.BIN':
                fname_up = os.path.basename(path).upper()
                if any(f'TRACK {i}' in fname_up or f'TRACK{i}' in fname_up
                       for i in range(2, 20)):
                    continue
            filtered.append(path)

        for path in filtered:
            fmt   = detect_format(path)
            size  = os.path.getsize(path)
            sz_s  = f"{size/1024/1024:.0f} MB" if size > 1048576 else f"{size//1024} KB"
            rel   = os.path.relpath(path, folder)
            row   = QTreeWidgetItem([rel, fmt.value, sz_s])
            row.setData(0, Qt.ItemDataRole.UserRole, path)
            self.disc_list.addTopLevelItem(row)

        count = self.disc_list.topLevelItemCount()
        self._log(f"Found {count} disc image{'s' if count != 1 else ''} in {folder}")
        if count == 1:
            item = self.disc_list.topLevelItem(0)
            self.disc_list.setCurrentItem(item)
            self.disc_edit.setText(item.data(0, Qt.ItemDataRole.UserRole))

    def _on_disc_double_clicked(self, item): #vers 1
        path = item.data(0, Qt.ItemDataRole.UserRole)
        if path:
            self.disc_edit.setText(path)
            self._open_disc()

    # --- Disc opening ---

    def _open_disc(self): #vers 1
        path = self.disc_edit.text().strip()
        if not path or not os.path.exists(path):
            QMessageBox.warning(self, "Open", "Please select a valid disc image.")
            return

        fmt = detect_format(path)
        self.fmt_label.setText(f"Format: {fmt.value}")

        if fmt in (DiscFormat.ARCHIVE_7Z, DiscFormat.ARCHIVE_RAR, DiscFormat.ARCHIVE_ZIP):
            self._open_archive(path, fmt)
            return

        self.open_btn.setEnabled(False)
        self.tree.clear()

        # Keep strong refs - Python GC will kill threads otherwise
        self._worker = DiscOpenWorker(path)
        self._worker_thread = QThread(self)   # parent=self keeps alive
        self._worker.moveToThread(self._worker_thread)
        self._worker_thread.started.connect(self._worker.run)
        self._worker.finished.connect(self._on_disc_opened)
        self._worker.error.connect(self._on_disc_error)
        self._worker.progress.connect(lambda m: self._log(m))
        self._worker.finished.connect(self._worker_thread.quit)
        self._worker_thread.finished.connect(self._worker_thread.deleteLater)
        self._worker_thread.start()

    def _open_archive(self, path: str, fmt: DiscFormat): #vers 1
        try:
            arch     = ArchiveImage(path)
            contents = arch.list_archive_contents()
            self.tree.clear()
            root = QTreeWidgetItem([os.path.basename(path),
                                    f"{len(contents)} files", fmt.value])
            root.setFont(0, QFont("Courier New", 8, QFont.Weight.Bold))
            self.tree.addTopLevelItem(root)
            for name in contents:
                ext = os.path.splitext(name)[1].upper()
                child = QTreeWidgetItem([name, "", ""])
                if ext in COLORS:
                    child.setForeground(0, COLORS[ext])
                root.addChild(child)
            root.setExpanded(True)
            self.ext_all_btn.setEnabled(True)
            self._disc = arch
            self._log(f"Archive: {len(contents)} files")
        except Exception as e:
            self._log(f"Archive error: {e}", error=True)

    def _on_disc_opened(self, disc: DiscImage): #vers 3
        self.open_btn.setEnabled(True)
        self._disc = disc
        self._populate_tree(disc)
        count   = len(disc.list_files())
        re_cnt  = sum(1 for f in disc.list_files()
                      if os.path.splitext(f.name)[1].upper() in RE_EXTENSIONS)
        self._log(f"Disc: {count} total files, {re_cnt} RE game files")
        self.ext_all_btn.setEnabled(count > 0)
        self.ext_re_btn.setEnabled(re_cnt > 0)
        # Save to recent discs
        disc_path = self.disc_edit.text().strip()
        if disc_path:
            self._save_recent_disc(disc_path)
        # Check if already extracted
        out_dir = self._get_output_dir()
        if self._already_extracted():
            self._log(f"Already extracted — loading: {out_dir}")
            self._last_extracted_dir = out_dir
            self.stage_folder_ready.emit(out_dir)
        elif os.path.isdir(out_dir):
            self._log(f"Output folder exists but no RDTs found: {out_dir}")

    def _on_disc_error(self, msg: str): #vers 1
        self.open_btn.setEnabled(True)
        self._log(f"Error: {msg}", error=True)

    # --- Nested tree ---

    def _populate_tree(self, disc: DiscImage): #vers 2
        """Build a fully nested directory tree matching the ISO filesystem."""
        self.tree.clear()
        dir_nodes: Dict[str, QTreeWidgetItem] = {}

        def get_dir_node(dir_path: str) -> QTreeWidgetItem:
            """Return (creating if needed) the tree node for a directory."""
            if dir_path in dir_nodes:
                return dir_nodes[dir_path]
            parts = dir_path.strip('/').split('/')
            # Ensure parent exists
            if len(parts) > 1:
                parent_path = '/' + '/'.join(parts[:-1])
                parent_node = get_dir_node(parent_path)
            else:
                parent_node = self.tree.invisibleRootItem()

            node = QTreeWidgetItem([parts[-1], "", "DIR"])
            node.setFont(0, QFont("Courier New", 8, QFont.Weight.Bold))
            node.setForeground(0, QColor(150, 190, 230))
            node.setExpanded(True)
            parent_node.addChild(node)
            dir_nodes[dir_path] = node
            return node

        for f in disc.list_files():
            if f.is_dir:
                get_dir_node(f.path)
                continue

            parts    = f.path.strip('/').split('/')
            dir_path = ('/' + '/'.join(parts[:-1])) if len(parts) > 1 else '/'
            parent   = get_dir_node(dir_path)

            ext      = os.path.splitext(f.name)[1].upper()
            size_str = f"{f.size:,}B" if f.size else ""
            row      = QTreeWidgetItem([f.name, size_str, ext.lstrip('.')])
            row.setData(0, Qt.ItemDataRole.UserRole, f)
            if ext in COLORS:
                row.setForeground(0, COLORS[ext])
            parent.addChild(row)

        # Expand top level only
        root = self.tree.invisibleRootItem()
        for i in range(root.childCount()):
            root.child(i).setExpanded(True)

    # --- Right-click context menu ---

    def _on_tree_context_menu(self, pos: QPoint): #vers 1
        item = self.tree.itemAt(pos)
        menu = QMenu(self)

        if item:
            f: Optional[DiscFile] = item.data(0, Qt.ItemDataRole.UserRole)
            if f and not f.is_dir:
                ext = os.path.splitext(f.name)[1].upper()
                viewer = VIEWERS.get(ext)

                if viewer == 'room':
                    menu.addAction(f"\U0001f3e0  Load Room in Editor",
                        lambda: self._extract_temp_and_view(f, 'room'))
                elif viewer == 'texture':
                    menu.addAction(f"\U0001f5bc  View Texture (TIM)",
                        lambda: self._extract_temp_and_view(f, 'texture'))
                elif viewer == 'model':
                    menu.addAction(f"\U0001f4e6  View Model (EMD)",
                        lambda: self._extract_temp_and_view(f, 'model'))
                elif viewer == 'audio':
                    menu.addAction(f"\U0001f3b5  Play Audio",
                        lambda: self._extract_temp_and_view(f, 'audio'))

                menu.addAction(f"Extract  {f.name}",
                    lambda: self._extract_single(f))
                menu.addAction("Extract to...",
                    lambda: self._extract_single_to(f))
                menu.addSeparator()

            # Folder operations
            if item.childCount() > 0 or (f is None):
                menu.addAction("Extract Folder Contents",
                    lambda: self._extract_folder_item(item))
                menu.addSeparator()

        menu.addAction("Extract RE Files", self._extract_all_re_files)
        menu.addAction("Extract All",      self._extract_all)
        menu.addSeparator()
        menu.addAction("Launch in Emulator", lambda: self._launch_disc())
        menu.addAction("Open Extracted Folder", lambda: self._open_folder())
        menu.addSeparator()
        menu.addAction("Save Snapshot (JSON)", self._save_snapshot)

        menu.exec(self.tree.viewport().mapToGlobal(pos))

    def _extract_temp_and_view(self, f: DiscFile, viewer_type: str): #vers 1
        """Extract file to temp, open in appropriate viewer."""
        if not self._disc:
            return
        try:
            suffix = os.path.splitext(f.name)[1]
            fd, tmp = tempfile.mkstemp(suffix=suffix)
            os.close(fd)
            self._disc.extract_file(f.path, tmp)
            self._log(f"Extracted to temp: {tmp}")
            self._open_in_viewer(tmp, viewer_type)
        except Exception as e:
            self._log(f"View error: {e}", error=True)
            QMessageBox.warning(self, "View Error", str(e))

    def _open_in_viewer(self, path: str, viewer_type: str): #vers 1
        """Route file to the correct viewer in the main window."""
        parent = self.parent()
        if not parent:
            return
        try:
            if viewer_type == 'room':
                parent._load_rdt(path)
                parent.display_mode_combo.setCurrentText("Room Map")
                self.stage_folder_ready.emit(os.path.dirname(path))
            elif viewer_type == 'texture':
                parent.show_tim_file(path)
            elif viewer_type == 'model':
                if hasattr(parent, 'emd_viewer') and parent.emd_viewer:
                    parent.emd_viewer.load_emd_file(path)
                    parent.display_mode_combo.setCurrentText("Model")
            elif viewer_type == 'audio':
                if hasattr(parent, 'audio_player') and parent.audio_player:
                    parent.audio_player.load_file(path)
        except Exception as e:
            self._log(f"Open in viewer error: {e}", error=True)

    # --- Single file extraction ---

    def _extract_single(self, f: DiscFile): #vers 1
        """Extract one file to the current output directory."""
        out_dir = self._get_output_dir()
        dest = os.path.join(out_dir, f.path.lstrip('/').replace('/', os.sep))
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        try:
            self._disc.extract_file(f.path, dest)
            self._log(f"Extracted: {f.path} -> {dest}")
        except Exception as e:
            self._log(f"Error: {e}", error=True)

    def _extract_single_to(self, f: DiscFile): #vers 1
        """Extract one file with a Save As dialog."""
        dest, _ = QFileDialog.getSaveFileName(
            self, f"Extract {f.name}", f.name)
        if dest:
            try:
                self._disc.extract_file(f.path, dest)
                self._log(f"Extracted: {f.name} -> {dest}")
            except Exception as e:
                self._log(f"Error: {e}", error=True)

    def _extract_folder_item(self, item: QTreeWidgetItem): #vers 1
        """Extract all files under a directory tree node."""
        if not self._disc:
            return
        out_dir = self._get_output_dir()
        count = 0

        def extract_children(node: QTreeWidgetItem):
            nonlocal count
            for i in range(node.childCount()):
                child = node.child(i)
                f: Optional[DiscFile] = child.data(0, Qt.ItemDataRole.UserRole)
                if f and not f.is_dir:
                    dest = os.path.join(out_dir,
                                        f.path.lstrip('/').replace('/', os.sep))
                    os.makedirs(os.path.dirname(dest), exist_ok=True)
                    try:
                        self._disc.extract_file(f.path, dest)
                        count += 1
                    except Exception as e:
                        self._log(f"  Error {f.path}: {e}", error=True)
                if child.childCount():
                    extract_children(child)

        extract_children(item)
        self._log(f"Extracted {count} files to {out_dir}")

    # --- Snapshot ---

    def _save_snapshot(self): #vers 1
        """Save disc contents as a JSON snapshot file."""
        if not self._disc:
            QMessageBox.warning(self, "Snapshot", "No disc mounted.")
            return

        disc_name = os.path.splitext(
            os.path.basename(self.disc_edit.text()))[0]
        default = os.path.join(self._get_output_dir(), f"{disc_name}_snapshot.json")
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Snapshot", default, "JSON (*.json)")
        if not path:
            return

        files = self.disc_disc_files() if hasattr(self, 'disc_disc_files') \
                else self._disc.list_files()
        doc = {
            "disc":    self.disc_edit.text(),
            "format":  self.fmt_label.text().replace("Format: ", ""),
            "files":   [
                {
                    "path": f.path,
                    "size": f.size,
                    "type": os.path.splitext(f.name)[1].upper().lstrip('.'),
                }
                for f in self._disc.list_files() if not f.is_dir
            ]
        }
        with open(path, 'w', encoding='utf-8') as fp:
            json.dump(doc, fp, indent=2)
        self._log(f"Snapshot saved: {path} ({len(doc['files'])} files)")
        QMessageBox.information(self, "Snapshot Saved",
            f"Saved {len(doc['files'])} entries to:\n{path}")

    # --- Bulk extraction ---

    def _on_selection_changed(self): #vers 1
        items = [i for i in self.tree.selectedItems()
                 if i.data(0, Qt.ItemDataRole.UserRole)]
        self.ext_sel_btn.setEnabled(len(items) > 0)

    def _get_output_dir(self) -> str: #vers 1
        out = self.out_edit.text().strip()
        if not out:
            out = os.path.join(os.path.dirname(self.disc_edit.text()), "extracted")
        return out

    def _extract_selected(self): #vers 1
        items = [i for i in self.tree.selectedItems()
                 if i.data(0, Qt.ItemDataRole.UserRole)]
        if not items or not self._disc:
            return
        out_dir = self._get_output_dir()
        self.progress.setVisible(True)
        self.progress.setMaximum(len(items))
        for i, item in enumerate(items):
            f: DiscFile = item.data(0, Qt.ItemDataRole.UserRole)
            dest = os.path.join(out_dir, f.path.lstrip('/').replace('/', os.sep))
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            try:
                self._disc.extract_file(f.path, dest)
            except Exception as e:
                self._log(f"  Error {f.path}: {e}", error=True)
            self.progress.setValue(i + 1)
        self.progress.setVisible(False)
        self._log(f"Extracted {len(items)} files to {out_dir}")
        self._offer_open_stage(out_dir)

    def _extract_all_re_files(self): #vers 2
        if not self._disc:
            return
        out_dir = self._get_output_dir()

        # Check already extracted
        if self._already_extracted():
            self._log(f"Already extracted: {out_dir}")
            self._log("Skipping extraction - loading existing files into viewer.")
            self._last_extracted_dir = out_dir
            self._offer_open_stage(out_dir)
            return

        re_files = [f for f in self._disc.list_files()
                    if os.path.splitext(f.name)[1].upper() in RE_EXTENSIONS]
        self.progress.setVisible(True)
        self.progress.setMaximum(len(re_files))
        done = 0
        for i, f in enumerate(re_files):
            dest = os.path.join(out_dir, f.path.lstrip('/').replace('/', os.sep))
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            try:
                self._disc.extract_file(f.path, dest)
                done += 1
            except Exception as e:
                self._log(f"  Error {f.path}: {e}", error=True)
            self.progress.setValue(i + 1)
        self.progress.setVisible(False)
        self._log(f"Extracted {done} RE files to {out_dir}")
        self._offer_open_stage(out_dir)

    def _already_extracted(self) -> bool: #vers 2
        """Check if output folder already contains extracted game files.
        Checks for RDT (PS1), ARD (RE1.5), ROFS*.DAT (RE3 PC), or TIM files.
        """
        out_dir = self._get_output_dir()
        if not os.path.isdir(out_dir):
            return False
        game_exts = {'.RDT', '.ARD', '.TIM', '.EMD', '.BSS'}
        for root, dirs, files in os.walk(out_dir):
            for fname in files:
                upper = fname.upper()
                if any(upper.endswith(ext) for ext in game_exts):
                    return True
                # RE3 PC: ROFS*.DAT archives
                if upper.startswith('ROFS') and upper.endswith('.DAT'):
                    return True
        return False

    def _extract_all(self): #vers 2
        if not self._disc:
            return
        out_dir = self._get_output_dir()

        # Check already extracted
        if self._already_extracted():
            self._log(f"Already extracted: {out_dir}")
            self._log("Skipping extraction - loading existing files into viewer.")
            self._last_extracted_dir = out_dir
            self._offer_open_stage(out_dir)
            return

        if isinstance(self._disc, ArchiveImage):
            extracted = self._disc.extract_archive_to(out_dir)
            self._log(f"Extracted {len(extracted)} files")
            self._offer_open_stage(out_dir)
            return
        files = [f for f in self._disc.list_files() if not f.is_dir]
        self.progress.setVisible(True)
        self.progress.setMaximum(len(files))
        done = 0
        for i, f in enumerate(files):
            dest = os.path.join(out_dir, f.path.lstrip('/').replace('/', os.sep))
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            try:
                self._disc.extract_file(f.path, dest)
                done += 1
            except Exception as e:
                self._log(f"  Error {f.path}: {e}", error=True)
            self.progress.setValue(i + 1)
        self.progress.setVisible(False)
        self._log(f"Extracted {done}/{len(files)} to {out_dir}")
        self._offer_open_stage(out_dir)

    def _offer_open_stage(self, out_dir: str): #vers 3
        """Store and emit extracted folder path."""
        self._last_extracted_dir = out_dir
        self._log(f"Extracted to: {out_dir}")
        # Don't emit here - wait for close so user can verify contents first
        # (emitting on close ensures panel loads after dialog is gone)

    # --- Build ISO ---

    def _browse_build_source(self): #vers 1
        folder = QFileDialog.getExistingDirectory(self, "Select Source Folder")
        if folder:
            self.build_src_edit.setText(folder)
            if not self.build_out_edit.text():
                self.build_out_edit.setText(folder + "_rebuilt.iso")

    def _browse_build_output(self): #vers 1
        path, _ = QFileDialog.getSaveFileName(
            self, "Save ISO As", "", "ISO Images (*.iso)")
        if path:
            self.build_out_edit.setText(path)

    def _do_build_iso(self): #vers 1
        src   = self.build_src_edit.text().strip()
        out   = self.build_out_edit.text().strip()
        label = self.vol_label_edit.text().strip() or 'BIOHAZARD'
        if not src or not os.path.isdir(src):
            QMessageBox.warning(self, "Build ISO", "Select a valid source folder.")
            return
        if not out:
            QMessageBox.warning(self, "Build ISO", "Specify output ISO path.")
            return
        self.build_progress.setVisible(True)
        self.build_progress.setRange(0, 0)
        self._log(f"Building ISO: {out}")
        try:
            ok = build_iso(src, out, volume_label=label)
            self.build_progress.setVisible(False)
            if ok:
                size = os.path.getsize(out)
                self._log(f"ISO built: {out}  ({size:,} bytes)")
                QMessageBox.information(self, "ISO Built",
                    f"ISO created:\n{out}\n{size:,} bytes")
            else:
                self._log("ISO build failed", error=True)
        except Exception as e:
            self.build_progress.setVisible(False)
            self._log(f"ISO build error: {e}", error=True)
            QMessageBox.critical(self, "Error", str(e))

    # --- Log ---

    def _on_close(self): #vers 2
        """Emit extracted folder to left panel then hide."""
        self._emit_stage_folder()
        self.hide()

    def closeEvent(self, event): #vers 2
        """On X button close, emit stage folder then accept."""
        self._emit_stage_folder()
        event.accept()

    def _emit_stage_folder(self): #vers 1
        """Emit stage_folder_ready with the best available folder path."""
        # Try output dir first
        out_dir = self._get_output_dir()
        if out_dir and os.path.isdir(out_dir):
            print(f"DiscManager: emitting stage folder: {out_dir}")
            self.stage_folder_ready.emit(out_dir)
            return
        # Try last known extracted folder
        if hasattr(self, '_last_extracted_dir') and self._last_extracted_dir:
            if os.path.isdir(self._last_extracted_dir):
                print(f"DiscManager: emitting last extracted: {self._last_extracted_dir}")
                self.stage_folder_ready.emit(self._last_extracted_dir)
                return
        print(f"DiscManager: no valid folder to emit (out_dir={out_dir!r})")

    def _show_recent_discs_menu(self): #vers 1
        """Show popup menu of recently opened disc images."""
        parent_win = self.parent()
        rf = getattr(parent_win, '_recent_files', None) if parent_win else None

        from PyQt6.QtWidgets import QMenu
        menu = QMenu(self)

        recent_discs = rf.get_recent_discs() if rf else []
        if recent_discs:
            for path in recent_discs:
                name = os.path.basename(path)
                folder = os.path.dirname(path)
                act = menu.addAction(f"{name}  —  {folder}")
                act.triggered.connect(
                    lambda checked, p=path, f=folder: self._open_recent_disc(p, f))
            menu.addSeparator()
            menu.addAction("Clear Recent", lambda: rf.clear_recent_discs() if rf and hasattr(rf, 'clear_recent_discs') else None)
        else:
            menu.addAction("(no recent disc images)").setEnabled(False)

        btn = self.sender()
        if btn:
            menu.exec(btn.mapToGlobal(btn.rect().bottomLeft()))

    def _open_recent_disc(self, disc_path: str, folder: str): #vers 1
        """Open a recent disc directly."""
        self.folder_edit.setText(folder)
        self.disc_edit.setText(disc_path)
        if not self.out_edit.text():
            self.out_edit.setText(os.path.join(folder, "extracted"))
        self._last_extracted_dir = os.path.join(folder, "extracted")
        self._scan_folder_for_discs(folder)
        self._open_disc()

    def _save_recent_disc(self, disc_path: str): #vers 1
        """Save disc path to recent files manager."""
        parent_win = self.parent()
        rf = getattr(parent_win, '_recent_files', None) if parent_win else None
        if rf:
            rf.add_recent_disc(disc_path)

    def _on_disc_list_context_menu(self, pos): #vers 1
        """Right-click context menu on disc image list."""
        item = self.disc_list.itemAt(pos)
        if not item:
            return
        path = item.data(0, Qt.ItemDataRole.UserRole)
        if not path:
            return
        menu = QMenu(self)
        menu.addAction("Open", lambda: (
            self.disc_edit.setText(path), self._open_disc()))
        menu.addAction("Launch in Emulator", lambda: self._launch_disc(path))
        menu.addAction("Open Folder", lambda: self._open_folder(os.path.dirname(path)))
        menu.exec(self.disc_list.viewport().mapToGlobal(pos))

    def _launch_disc(self, disc_path: str = ''): #vers 1
        """Open launcher dialog for a disc image."""
        try:
            from apps.gui.launcher_dialog import LauncherDialog
            disc = disc_path or self.disc_edit.text().strip()
            out  = self._get_output_dir()
            dlg  = LauncherDialog(self, disc_path=disc, folder_path=out)
            dlg.show()
        except Exception as e:
            self._log(f"Launcher error: {e}", error=True)

    def _open_folder(self, path: str = ''): #vers 1
        """Open folder in system file manager."""
        from apps.core.re_launchers import open_in_filemanager
        target = path or self._get_output_dir()
        ok, msg = open_in_filemanager(target)
        self._log(msg, error=not ok)

    def _log(self, msg: str, error: bool = False): #vers 1
        color = "#cc6666" if error else "#aaaaaa"
        self.log_box.append(f'<span style="color:{color};">{msg}</span>')
        self.log_box.verticalScrollBar().setValue(
            self.log_box.verticalScrollBar().maximum())
