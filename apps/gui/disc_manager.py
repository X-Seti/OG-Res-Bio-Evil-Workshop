#!/usr/bin/env python3
#this belongs in apps/gui/disc_manager.py - Version: 1
# X-Seti - May22 2026 - ResBio-Evil-Workshop - Disc Manager
"""
Disc Manager - Open and extract PS1 disc images (ISO, BIN/CUE, CCD/IMG/SUB)
and compressed archives (7z, RAR, ZIP). Also builds new ISO images.
Integrates with the RE file unpacker after extraction.
"""

import os
from typing import Optional

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFileDialog, QTreeWidget, QTreeWidgetItem,
    QProgressBar, QTextEdit, QFrame, QSplitter, QHeaderView,
    QTabWidget, QWidget, QMessageBox, QAbstractItemView,
    QGroupBox, QFormLayout, QComboBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QObject
from PyQt6.QtGui import QFont, QColor

from apps.core.disc_image import (
    open_disc, detect_format, build_iso,
    DiscImage, DiscFile, DiscFormat, ArchiveImage
)

##Methods list -
# _browse_disc
# _browse_archive
# _browse_output
# _open_disc
# _open_archive
# _populate_tree
# _extract_selected
# _extract_all_re_files
# _extract_all
# _build_iso_tab
# _do_build_iso
# _log

##class DiscOpenWorker:
##class DiscManagerDialog:


# File type colors
COLORS = {
    '.RDT': QColor(100, 180, 255),
    '.TIM': QColor(200, 160, 80),
    '.EMD': QColor(150, 220, 150),
    '.PAK': QColor(200, 130, 200),
    '.BSS': QColor(180, 180, 100),
    '.ADT': QColor(200, 120, 100),
}

# RE-relevant extensions
RE_EXTENSIONS = {'.RDT', '.TIM', '.EMD', '.PAK', '.BSS', '.ADT',
                 '.PLD', '.EDD', '.BIN', '.DAT', '.SLD', '.PRS'}


class DiscOpenWorker(QObject): #vers 1
    """Background worker: open disc image and scan filesystem."""
    finished = pyqtSignal(object)   # DiscImage
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


class DiscManagerDialog(QDialog): #vers 1
    """Disc image browser, extractor and ISO builder."""

    stage_folder_ready = pyqtSignal(str)   # extracted folder ready to scan

    def __init__(self, parent=None): #vers 1
        super().__init__(parent)
        self.setWindowTitle("Disc Manager")
        self.resize(900, 640)
        self.setModal(False)
        self._disc: Optional[DiscImage] = None
        self._worker_thread: Optional[QThread] = None
        self._build_ui()

    def _build_ui(self): #vers 1
        layout = QVBoxLayout(self)
        layout.setSpacing(4)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_open_tab(),  "Open / Extract")
        self.tabs.addTab(self._build_build_tab(), "Build ISO")
        layout.addWidget(self.tabs)

        # Log
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setMaximumHeight(100)
        self.log_box.setFont(QFont("Courier New", 8))
        layout.addWidget(self.log_box)

    # --- Open/Extract tab ---

    def _build_open_tab(self) -> QWidget: #vers 1
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(4)

        # Folder picker row
        folder_row = QHBoxLayout()
        folder_row.addWidget(QLabel("Folder:"))
        self.folder_edit = QLineEdit()
        self.folder_edit.setPlaceholderText("Folder containing disc images (.img .iso .bin .cue .ccd .7z .rar .zip)")
        folder_row.addWidget(self.folder_edit, stretch=1)
        browse_folder_btn = QPushButton("Browse...")
        browse_folder_btn.setMaximumWidth(80)
        browse_folder_btn.clicked.connect(self._browse_folder)
        folder_row.addWidget(browse_folder_btn)
        layout.addLayout(folder_row)

        # Disc image list
        disc_list_label = QLabel("Disc images found:")
        disc_list_label.setFont(QFont("Courier New", 8))
        layout.addWidget(disc_list_label)

        self.disc_list = QTreeWidget()
        self.disc_list.setColumnCount(3)
        self.disc_list.setHeaderLabels(["File", "Format", "Size"])
        self.disc_list.setMaximumHeight(120)
        self.disc_list.setAlternatingRowColors(True)
        self.disc_list.setFont(QFont("Courier New", 8))
        self.disc_list.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.disc_list.header().resizeSection(1, 120)
        self.disc_list.header().resizeSection(2, 80)
        self.disc_list.itemDoubleClicked.connect(self._on_disc_double_clicked)
        layout.addWidget(self.disc_list)

        # Open selected row
        open_row = QHBoxLayout()
        self.disc_edit = QLineEdit()
        self.disc_edit.setPlaceholderText("Selected disc image path")
        open_row.addWidget(self.disc_edit, stretch=1)
        self.open_btn = QPushButton("Open")
        self.open_btn.setMaximumWidth(60)
        self.open_btn.clicked.connect(self._open_disc)
        open_row.addWidget(self.open_btn)
        layout.addLayout(open_row)

        # Format label
        self.fmt_label = QLabel("Format: —")
        self.fmt_label.setFont(QFont("Courier New", 8))
        layout.addWidget(self.fmt_label)

        sep = QFrame(); sep.setFrameStyle(QFrame.Shape.HLine)
        layout.addWidget(sep)

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

        # Progress
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        # Action buttons
        btn_row = QHBoxLayout()
        self.ext_sel_btn = QPushButton("Extract Selected")
        self.ext_sel_btn.setEnabled(False)
        self.ext_sel_btn.clicked.connect(self._extract_selected)
        self.ext_re_btn = QPushButton("Extract RE Files")
        self.ext_re_btn.setEnabled(False)
        self.ext_re_btn.setToolTip("Extract only RDT, TIM, EMD, PAK, BSS, etc.")
        self.ext_re_btn.clicked.connect(self._extract_all_re_files)
        self.ext_all_btn = QPushButton("Extract All")
        self.ext_all_btn.setEnabled(False)
        self.ext_all_btn.clicked.connect(self._extract_all)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        btn_row.addWidget(self.ext_sel_btn)
        btn_row.addWidget(self.ext_re_btn)
        btn_row.addWidget(self.ext_all_btn)
        btn_row.addStretch()
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

        self.tree.itemSelectionChanged.connect(self._on_selection_changed)
        return w

    # --- Build ISO tab ---

    def _build_build_tab(self) -> QWidget: #vers 1
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(8)

        grp = QGroupBox("Build ISO from folder")
        form = QFormLayout(grp)

        self.build_src_edit = QLineEdit()
        self.build_src_edit.setPlaceholderText("Source folder (extracted game files)")
        src_btn = QPushButton("Browse...")
        src_btn.setMaximumWidth(80)
        src_btn.clicked.connect(self._browse_build_source)
        src_row = QHBoxLayout()
        src_row.addWidget(self.build_src_edit, stretch=1)
        src_row.addWidget(src_btn)
        form.addRow("Source folder:", src_row)

        self.build_out_edit = QLineEdit()
        self.build_out_edit.setPlaceholderText("Output .iso path")
        out_btn = QPushButton("Browse...")
        out_btn.setMaximumWidth(80)
        out_btn.clicked.connect(self._browse_build_output)
        out_row = QHBoxLayout()
        out_row.addWidget(self.build_out_edit, stretch=1)
        out_row.addWidget(out_btn)
        form.addRow("Output ISO:", out_row)

        self.vol_label_edit = QLineEdit("BIOHAZARD")
        form.addRow("Volume label:", self.vol_label_edit)

        layout.addWidget(grp)

        info = QLabel(
            "Note: This builds a standard ISO9660 data disc.\n"
            "It does NOT include PS1 anti-piracy data or audio tracks.\n"
            "Use for PC versions or as an extracted game file archive."
        )
        info.setFont(QFont("Courier New", 8))
        info.setStyleSheet("color: #888;")
        layout.addWidget(info)

        self.build_progress = QProgressBar()
        self.build_progress.setVisible(False)
        layout.addWidget(self.build_progress)

        build_btn = QPushButton("Build ISO")
        build_btn.clicked.connect(self._do_build_iso)
        layout.addWidget(build_btn)
        layout.addStretch()
        return w

    # --- Disc opening ---

    def _browse_disc(self): #vers 1
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Disc Image", "",
            "Disc Images (*.iso *.bin *.cue *.ccd *.img *.7z *.rar *.zip);;All Files (*)"
        )
        if path:
            self.disc_edit.setText(path)
            folder = os.path.dirname(path)
            if not self.out_edit.text():
                self.out_edit.setText(os.path.join(folder, "extracted"))
            self._open_disc()

    def _browse_output(self): #vers 1
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.out_edit.setText(folder)

    def _open_disc(self): #vers 1
        path = self.disc_edit.text().strip()
        if not path or not os.path.exists(path):
            QMessageBox.warning(self, "Open", "Please select a valid disc image file.")
            return

        fmt = detect_format(path)
        self.fmt_label.setText(f"Format: {fmt.value}")

        # Handle archives specially - just list contents
        if fmt in (DiscFormat.ARCHIVE_7Z, DiscFormat.ARCHIVE_RAR, DiscFormat.ARCHIVE_ZIP):
            self._open_archive(path, fmt)
            return

        self.open_btn.setEnabled(False)
        self.tree.clear()

        self._worker = DiscOpenWorker(path)
        self._worker_thread = QThread()
        self._worker.moveToThread(self._worker_thread)
        self._worker_thread.started.connect(self._worker.run)
        self._worker.finished.connect(self._on_disc_opened)
        self._worker.error.connect(self._on_disc_error)
        self._worker.progress.connect(lambda m: self._log(m))
        self._worker.finished.connect(self._worker_thread.quit)
        self._worker_thread.start()

    def _open_archive(self, path: str, fmt: DiscFormat): #vers 1
        """List archive contents without full extraction."""
        try:
            arch = ArchiveImage(path)
            contents = arch.list_archive_contents()
            self.tree.clear()
            root = QTreeWidgetItem([os.path.basename(path), f"{len(contents)} files", fmt.value])
            root.setFont(0, QFont("Courier New", 8, QFont.Weight.Bold))
            self.tree.addTopLevelItem(root)
            for name in contents:
                child = QTreeWidgetItem([name, "", ""])
                ext = os.path.splitext(name)[1].upper()
                if ext in COLORS:
                    child.setForeground(0, COLORS[ext])
                root.addChild(child)
            root.setExpanded(True)
            self.ext_all_btn.setEnabled(True)
            self._disc = arch
            self._log(f"Archive: {len(contents)} files inside {os.path.basename(path)}")
        except Exception as e:
            self._log(f"Archive error: {e}", error=True)

    def _on_disc_opened(self, disc: DiscImage): #vers 1
        self.open_btn.setEnabled(True)
        self._disc = disc
        self._populate_tree(disc)
        count = len(disc.list_files())
        re_count = sum(1 for f in disc.list_files()
                       if os.path.splitext(f.name)[1].upper() in RE_EXTENSIONS)
        self._log(f"Disc: {count} total files, {re_count} RE game files")
        self.ext_all_btn.setEnabled(count > 0)
        self.ext_re_btn.setEnabled(re_count > 0)

    def _on_disc_error(self, msg: str): #vers 1
        self.open_btn.setEnabled(True)
        self._log(f"Error: {msg}", error=True)

    def _populate_tree(self, disc: DiscImage): #vers 1
        self.tree.clear()
        files = disc.list_files()

        # Group by top-level directory
        dirs: dict = {}
        for f in files:
            parts = f.path.lstrip('/').split('/')
            top = parts[0] if len(parts) > 1 else ''
            dirs.setdefault(top, []).append(f)

        for top_dir, dir_files in sorted(dirs.items()):
            if top_dir:
                parent = QTreeWidgetItem([top_dir, "", "DIR"])
                parent.setFont(0, QFont("Courier New", 8, QFont.Weight.Bold))
                parent.setForeground(0, QColor(150, 190, 230))
                self.tree.addTopLevelItem(parent)
            else:
                parent = self.tree.invisibleRootItem()

            for f in dir_files:
                ext = os.path.splitext(f.name)[1].upper()
                size_str = f"{f.size:,}B" if f.size else ""
                row = QTreeWidgetItem([f.path, size_str, ext.lstrip('.')])
                row.setData(0, Qt.ItemDataRole.UserRole, f)
                if ext in COLORS:
                    row.setForeground(0, COLORS[ext])
                parent.addChild(row)

            if top_dir:
                parent.setExpanded(True)

    # --- Extraction ---

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
        done = 0
        for i, item in enumerate(items):
            f: DiscFile = item.data(0, Qt.ItemDataRole.UserRole)
            dest = os.path.join(out_dir, f.path.lstrip('/').replace('/', os.sep))
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            try:
                self._disc.extract_file(f.path, dest)
                done += 1
                self._log(f"  {f.path}")
            except Exception as e:
                self._log(f"  ERROR {f.path}: {e}", error=True)
            self.progress.setValue(i + 1)
        self.progress.setVisible(False)
        self._log(f"Extracted {done}/{len(items)} to {out_dir}")
        self._offer_open_stage(out_dir)

    def _extract_all_re_files(self): #vers 1
        if not self._disc:
            return
        out_dir = self._get_output_dir()
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
                self._log(f"  ERROR {f.path}: {e}", error=True)
            self.progress.setValue(i + 1)
        self.progress.setVisible(False)
        self._log(f"Extracted {done} RE files to {out_dir}")
        self._offer_open_stage(out_dir)

    def _extract_all(self): #vers 1
        if not self._disc:
            return
        out_dir = self._get_output_dir()

        # Archives extract differently
        if isinstance(self._disc, ArchiveImage):
            self._log(f"Extracting archive to {out_dir}...")
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
                self._log(f"  ERROR {f.path}: {e}", error=True)
            self.progress.setValue(i + 1)
        self.progress.setVisible(False)
        self._log(f"Extracted {done}/{len(files)} to {out_dir}")
        self._offer_open_stage(out_dir)

    def _offer_open_stage(self, out_dir: str): #vers 1
        reply = QMessageBox.question(self, "Open Stage Folder",
            f"Open extracted files as stage folder?\n{out_dir}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.stage_folder_ready.emit(out_dir)

    # --- Build ISO tab ---

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
        src = self.build_src_edit.text().strip()
        out = self.build_out_edit.text().strip()
        label = self.vol_label_edit.text().strip() or 'BIOHAZARD'

        if not src or not os.path.isdir(src):
            QMessageBox.warning(self, "Build ISO", "Please select a valid source folder.")
            return
        if not out:
            QMessageBox.warning(self, "Build ISO", "Please specify output ISO path.")
            return

        self.build_progress.setVisible(True)
        self.build_progress.setRange(0, 0)  # indeterminate
        self._log(f"Building ISO: {out}")

        try:
            ok = build_iso(src, out, volume_label=label)
            self.build_progress.setVisible(False)
            if ok:
                size = os.path.getsize(out)
                self._log(f"ISO built: {out}  ({size:,} bytes)")
                QMessageBox.information(self, "ISO Built",
                    f"ISO created successfully:\n{out}\n{size:,} bytes")
            else:
                self._log("ISO build failed", error=True)
                QMessageBox.critical(self, "Build Failed", "ISO build failed. Check log.")
        except Exception as e:
            self.build_progress.setVisible(False)
            self._log(f"ISO build error: {e}", error=True)
            QMessageBox.critical(self, "Error", str(e))

    # --- Log ---

    def _log(self, msg: str, error: bool = False): #vers 1
        color = "#cc6666" if error else "#aaaaaa"
        self.log_box.append(f'<span style="color:{color};">{msg}</span>')
        self.log_box.verticalScrollBar().setValue(
            self.log_box.verticalScrollBar().maximum())
