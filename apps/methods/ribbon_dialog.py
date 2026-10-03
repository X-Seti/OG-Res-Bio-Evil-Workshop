#this belongs in apps/methods/ribbon_dialog.py - Version: 1
# X-Seti - October 3 2026 - Multi-Emulator Launcher - Ribbon Manager dialog

"""ribbon_dialog.py - Ribbon Manager for MEL windows.

RibbonManagerDialog - two panes: toolbars on the left, the buttons of the
selected toolbar on the right. Drag to reorder, move buttons between
toolbars, create/delete toolbars, add or remove dividers, tick a button to
show it or untick to hide it, give a button a custom image icon, restore
its built-in icon, change the icon size, save and load named presets.
Changes apply live; Cancel restores the layout from when the dialog opened.

RibbonIconsMixin - the window-side half: icon files, saved button order,
dividers and hidden buttons, plus the hooks the dialog calls.

Ribbon settings live in mel_settings.json: ribbon_state,
ribbon_state_version, ribbon_layout, custom_icons, icon_scale,
toolbar_presets.
"""

##Methods list -
# RibbonManagerDialog.__init__
# RibbonManagerDialog._add_divider
# RibbonManagerDialog._build_ui
# RibbonManagerDialog._create_toolbar
# RibbonManagerDialog._delete_divider
# RibbonManagerDialog._delete_toolbar
# RibbonManagerDialog._load_preset
# RibbonManagerDialog._move_action
# RibbonManagerDialog._on_accept
# RibbonManagerDialog._on_action_reordered
# RibbonManagerDialog._on_cancel
# RibbonManagerDialog._on_icon_size_changed
# RibbonManagerDialog._on_item_checked
# RibbonManagerDialog._on_toolbar_selected
# RibbonManagerDialog._refresh_action_list
# RibbonManagerDialog._refresh_toolbar_list
# RibbonManagerDialog._reset_icon
# RibbonManagerDialog._save_preset
# RibbonManagerDialog._selected_entry_name
# RibbonManagerDialog._set_icon

##class RibbonIconsMixin: -
# _apply_custom_icon_images
# _apply_custom_icons
# _apply_icon_scale
# _apply_ribbon_layout
# _custom_icons
# _icons_dir
# _render_ribbon_icons
# _ribbon_layout_snapshot
# _save_custom_icons
# _save_ribbon_layout
# open_ribbon_manager

import json
import shutil
import sys
from pathlib import Path

from PyQt6.QtCore import QByteArray, QSize, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (QComboBox, QDialog, QDialogButtonBox, QFileDialog,
                             QHBoxLayout, QInputDialog, QLabel, QListWidget,
                             QListWidgetItem, QMessageBox, QPushButton,
                             QSlider, QSplitter, QToolBar, QVBoxLayout, QWidget)

__all__ = ['RibbonManagerDialog', 'RibbonIconsMixin']


class RibbonManagerDialog(QDialog): #vers 1
    """Two-pane ribbon manager: toolbars, and the buttons on each"""

    def __init__(self, window, parent=None): #vers 1
        super().__init__(parent)
        self._ws = window
        self._mw = getattr(window, '_ribbon_mw', None)
        self._selected_tb = None
        self._cancel_state = None
        self.setWindowTitle("Ribbon Manager")
        self.setMinimumSize(660, 440)
        self._build_ui()
        self._refresh_toolbar_list()
        if self._mw:
            self._cancel_state = self._mw.saveState()

    def _build_ui(self): #vers 1
        outer = QVBoxLayout(self)

        # Toolbar row
        tb_row = QHBoxLayout()
        self._new_btn = QPushButton("+ New Toolbar")
        self._del_btn = QPushButton("Delete")
        self._save_preset_btn = QPushButton("Save Preset...")
        self._load_preset_btn = QPushButton("Load Preset...")
        for b in (self._new_btn, self._del_btn,
                  self._save_preset_btn, self._load_preset_btn):
            tb_row.addWidget(b)
        tb_row.addStretch()
        self._new_btn.clicked.connect(self._create_toolbar)
        self._del_btn.clicked.connect(self._delete_toolbar)
        self._save_preset_btn.clicked.connect(self._save_preset)
        self._load_preset_btn.clicked.connect(self._load_preset)
        outer.addLayout(tb_row)

        # Icon size row
        size_row = QHBoxLayout()
        size_row.addWidget(QLabel("Ribbon Icon Size:"))
        self._size_slider = QSlider(Qt.Orientation.Horizontal)
        self._size_slider.setRange(14, 40)
        self._size_slider.setSingleStep(2)
        saved_px = int(self._ws._ribbon_config_get('icon_scale', self._ws._RIBBON_ICON)
                       or self._ws._RIBBON_ICON)
        self._size_slider.setValue(saved_px)
        self._size_value_label = QLabel(f"{saved_px}px")
        self._size_value_label.setMinimumWidth(36)
        self._size_slider.valueChanged.connect(self._on_icon_size_changed)
        size_row.addWidget(self._size_slider, stretch=1)
        size_row.addWidget(self._size_value_label)
        outer.addLayout(size_row)

        # Splitter: left = toolbar list, right = action list
        splitter = QSplitter(Qt.Orientation.Horizontal)
        outer.addWidget(splitter, stretch=1)

        # Left pane
        left = QWidget()
        ll = QVBoxLayout(left)
        ll.setSpacing(4)
        ll.addWidget(QLabel("Toolbars"))
        self._tb_list = QListWidget()
        self._tb_list.currentRowChanged.connect(self._on_toolbar_selected)
        ll.addWidget(self._tb_list)
        splitter.addWidget(left)

        # Right pane
        right = QWidget()
        rl = QVBoxLayout(right)
        rl.setSpacing(4)
        self._action_label = QLabel("Select a toolbar")
        rl.addWidget(self._action_label)
        self._act_list = QListWidget()
        self._act_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self._act_list.setDefaultDropAction(Qt.DropAction.MoveAction)
        self._act_list.setIconSize(QSize(24, 24))
        self._act_list.model().rowsMoved.connect(self._on_action_reordered)
        self._act_list.itemChanged.connect(self._on_item_checked)
        self._act_list.setToolTip("Untick a button to hide it on the ribbon")
        rl.addWidget(self._act_list)

        # Move-to-toolbar row
        move_row = QHBoxLayout()
        move_row.addWidget(QLabel("Move selected to:"))
        self._move_combo = QComboBox()
        move_row.addWidget(self._move_combo, stretch=1)
        self._move_btn = QPushButton("Move")
        self._move_btn.setToolTip("Move selected buttons to the chosen ribbon")
        self._move_btn.clicked.connect(self._move_action)
        move_row.addWidget(self._move_btn)
        rl.addLayout(move_row)

        # Icon and divider row
        icon_row = QHBoxLayout()
        self._set_icon_btn = QPushButton("Set Icon...")
        self._set_icon_btn.setToolTip("Use an image from the icons folder")
        self._set_icon_btn.clicked.connect(self._set_icon)
        self._reset_icon_btn = QPushButton("Reset Icon")
        self._reset_icon_btn.setToolTip("Restore the built-in SVG icon")
        self._reset_icon_btn.clicked.connect(self._reset_icon)
        icon_row.addWidget(self._set_icon_btn)
        icon_row.addWidget(self._reset_icon_btn)
        self._add_div_btn = QPushButton("Add Divider")
        self._add_div_btn.setToolTip("Insert a divider after the selected button")
        self._add_div_btn.clicked.connect(self._add_divider)
        self._del_div_btn = QPushButton("Delete Divider")
        self._del_div_btn.setToolTip("Remove the selected divider")
        self._del_div_btn.clicked.connect(self._delete_divider)
        icon_row.addWidget(self._add_div_btn)
        icon_row.addWidget(self._del_div_btn)
        icon_row.addStretch()
        rl.addLayout(icon_row)
        splitter.addWidget(right)
        splitter.setSizes([200, 440])

        # OK / Cancel
        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self._on_accept)
        btns.rejected.connect(self._on_cancel)
        outer.addWidget(btns)

    def _on_icon_size_changed(self, px): #vers 1
        """Apply and save the new icon size live"""
        self._size_value_label.setText(f"{px}px")
        self._ws._apply_icon_scale(px)

    def _refresh_toolbar_list(self): #vers 1
        """Fill the left pane with every toolbar"""
        self._tb_list.clear()
        self._move_combo.clear()
        for tb in self._ws.ribbon_toolbars():
            name = tb.windowTitle() or tb.objectName()
            item = QListWidgetItem(name)
            item.setData(Qt.ItemDataRole.UserRole, tb)
            acts = [a for a in tb.actions() if not a.isSeparator() and not a.icon().isNull()]
            if acts:
                item.setIcon(acts[0].icon())
            self._tb_list.addItem(item)
            self._move_combo.addItem(name, tb)

    def _on_toolbar_selected(self, row): #vers 1
        """Show the buttons of the selected toolbar"""
        item = self._tb_list.item(row)
        if not item:
            return
        self._selected_tb = item.data(Qt.ItemDataRole.UserRole)
        self._refresh_action_list()

    def _refresh_action_list(self): #vers 1
        """Fill the right pane with the selected toolbar's buttons"""
        self._act_list.clear()
        tb = self._selected_tb
        if not tb:
            return
        name = tb.windowTitle() or tb.objectName()
        self._action_label.setText(f"{name} - buttons")
        for act in tb.actions():
            if act.isSeparator():
                item = QListWidgetItem("- divider -")
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsDragEnabled)
            else:
                item = QListWidgetItem(act.text() or act.toolTip() or "Button")
                icon = act.icon()
                if not icon.isNull():
                    item.setIcon(icon)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(Qt.CheckState.Checked if act.isVisible()
                                   else Qt.CheckState.Unchecked)
            item.setData(Qt.ItemDataRole.UserRole, act)
            self._act_list.blockSignals(True)
            self._act_list.addItem(item)
            self._act_list.blockSignals(False)

    def _on_action_reordered(self): #vers 1
        """Apply the dragged order to the toolbar"""
        tb = self._selected_tb
        if not tb:
            return
        new_order = []
        for i in range(self._act_list.count()):
            act = self._act_list.item(i).data(Qt.ItemDataRole.UserRole)
            if act:
                new_order.append(act)
        for act in list(tb.actions()):
            tb.removeAction(act)
        for act in new_order:
            tb.addAction(act)

    def _on_item_checked(self, item): #vers 1
        """Tick shows the button on the ribbon, untick hides it"""
        act = item.data(Qt.ItemDataRole.UserRole)
        if act is not None and not act.isSeparator():
            act.setVisible(item.checkState() == Qt.CheckState.Checked)

    def _add_divider(self): #vers 1
        """Insert a divider after the selected button"""
        tb = self._selected_tb
        if not tb:
            return
        acts = tb.actions()
        row = self._act_list.currentRow()
        before = acts[row + 1] if 0 <= row < len(acts) - 1 else None
        if before is not None:
            tb.insertSeparator(before)
        else:
            tb.addSeparator()
        self._refresh_action_list()

    def _delete_divider(self): #vers 1
        """Remove the selected divider"""
        item = self._act_list.currentItem()
        act = item.data(Qt.ItemDataRole.UserRole) if item else None
        if act is None or not act.isSeparator() or not self._selected_tb:
            self._ws._set_status("Select a divider to delete")
            return
        self._selected_tb.removeAction(act)
        self._refresh_action_list()

    def _move_action(self): #vers 1
        """Move the selected button to the chosen toolbar"""
        item = self._act_list.currentItem()
        act = item.data(Qt.ItemDataRole.UserRole) if item else None
        if not act or not self._selected_tb or act.isSeparator():
            return
        target_tb = self._move_combo.currentData()
        if not target_tb or target_tb is self._selected_tb:
            return
        self._selected_tb.removeAction(act)
        target_tb.addAction(act)
        self._refresh_action_list()

    def _create_toolbar(self): #vers 1
        """Create a new empty toolbar"""
        if not self._mw:
            return
        name, ok = QInputDialog.getText(self, "New Toolbar", "Toolbar name:")
        if not ok or not name.strip():
            return
        self._ws.ribbon_toolbar(name.strip())
        self._refresh_toolbar_list()

    def _delete_toolbar(self): #vers 1
        """Delete the selected toolbar after confirming"""
        tb = self._selected_tb
        if not tb or not self._mw:
            return
        n_acts = len([a for a in tb.actions() if not a.isSeparator()])
        if n_acts > 0:
            ans = QMessageBox.question(
                self, "Delete Toolbar",
                f"'{tb.windowTitle()}' has {n_acts} button(s).\n"
                "They will be removed from the ribbon.\nContinue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel)
            if ans != QMessageBox.StandardButton.Yes:
                return
        self._mw.removeToolBar(tb)
        tb.deleteLater()
        self._selected_tb = None
        self._refresh_toolbar_list()
        self._act_list.clear()

    def _selected_entry_name(self): #vers 1
        """Registered name of the selected button, None if not iconable"""
        item = self._act_list.currentItem()
        act = item.data(Qt.ItemDataRole.UserRole) if item else None
        for entry in getattr(self._ws, '_ribbon_actions', []):
            if entry['action'] is act:
                return entry['name']
        if act and not act.isSeparator():
            self._ws._set_status("This button's icon can't be changed")
        return None

    def _set_icon(self): #vers 1
        """Pick an image for the selected button, copied into icons/"""
        name = self._selected_entry_name()
        if not name:
            return
        folder = self._ws._icons_dir()
        src, _ = QFileDialog.getOpenFileName(
            self, f"Icon for {name}", str(folder),
            "Images (*.png *.jpg *.jpeg *.svg)")
        if not src:
            return
        src = Path(src)
        folder.mkdir(parents=True, exist_ok=True)
        if src.parent.resolve() != folder.resolve():
            shutil.copy2(src, folder / src.name)
        icons = self._ws._custom_icons()
        icons[name] = src.name
        self._ws._save_custom_icons(icons)
        row = self._act_list.currentRow()
        self._refresh_action_list()
        self._act_list.setCurrentRow(row)

    def _reset_icon(self): #vers 1
        """Restore the built-in icon on the selected button"""
        name = self._selected_entry_name()
        if not name:
            return
        icons = self._ws._custom_icons()
        icons.pop(name, None)
        self._ws._save_custom_icons(icons)
        row = self._act_list.currentRow()
        self._refresh_action_list()
        self._act_list.setCurrentRow(row)

    def _save_preset(self): #vers 1
        """Save the current layout under a preset name"""
        if not self._mw:
            return
        name, ok = QInputDialog.getText(self, "Save Preset", "Preset name:")
        if not ok or not name.strip():
            return
        presets = dict(self._ws._ribbon_config_get('toolbar_presets', {}) or {})
        presets[name.strip()] = {
            'state': self._mw.saveState().toHex().data().decode(),
            'icons': self._ws._custom_icons(),
        }
        self._ws._ribbon_config_set('toolbar_presets', presets)
        self._ws._set_status(f"Preset '{name.strip()}' saved")

    def _load_preset(self): #vers 1
        """Load a saved preset"""
        if not self._mw:
            return
        presets = self._ws._ribbon_config_get('toolbar_presets', {}) or {}
        if not presets:
            QMessageBox.information(self, "Load Preset", "No saved presets found.")
            return
        name, ok = QInputDialog.getItem(self, "Load Preset", "Select preset:",
                                        list(presets.keys()), editable=False)
        if not ok:
            return
        preset = presets[name]
        if isinstance(preset, str):
            preset = {'state': preset}
        self._mw.restoreState(QByteArray.fromHex(preset['state'].encode()))
        if 'icons' in preset:
            self._ws._save_custom_icons(preset['icons'])
        self._refresh_toolbar_list()
        self._ws._set_status(f"Preset '{name}' loaded")

    def _on_accept(self): #vers 1
        """Save state, button order, dividers and hidden buttons"""
        self._ws.ribbon_save_state()
        self._ws._save_ribbon_layout()
        self.accept()

    def _on_cancel(self): #vers 1
        """Restore the layout from when the dialog opened"""
        if self._cancel_state and self._mw:
            self._mw.restoreState(self._cancel_state)
        self.reject()


class RibbonIconsMixin: #vers 1
    """Ribbon Manager hooks, custom icons and saved ribbon layout"""

    def open_ribbon_manager(self): #vers 1
        """Open the Ribbon Manager dialog"""
        RibbonManagerDialog(self, parent=self).exec()

    def _icons_dir(self) -> Path: #vers 1
        """Shared icons folder: apps/icons, or beside a frozen exe"""
        if getattr(sys, 'frozen', False):
            return Path(sys.executable).parent / 'icons'
        return Path(__file__).resolve().parents[1] / 'icons'

    def _custom_icons(self) -> dict: #vers 1
        """Button name to image file name in the icons folder"""
        return dict(self._ribbon_config_get('custom_icons', {}) or {})

    def _save_custom_icons(self, icons): #vers 1
        """Store the icon choices and redraw every ribbon icon"""
        self._ribbon_config_set('custom_icons', dict(icons))
        self._render_ribbon_icons()
        self._apply_custom_icon_images()

    def _apply_icon_scale(self, px): #vers 1
        """Apply the ribbon icon size and redraw the icons"""
        self._ribbon_config_set('icon_scale', int(px))
        for tb in self.ribbon_toolbars():
            tb.setIconSize(QSize(int(px), int(px)))
        self._render_ribbon_icons()
        self._apply_custom_icon_images()

    def _render_ribbon_icons(self): #vers 1
        """Redraw every built-in ribbon icon in the theme colour"""
        for entry in getattr(self, '_ribbon_actions', []):
            if entry['icon_fn'] is not None:
                entry['action'].setIcon(self._ribbon_icon(entry['icon_fn']))

    def _apply_custom_icon_images(self): #vers 1
        """Draw chosen icons/ images over the built-in icons"""
        icons = self._custom_icons()
        folder = self._icons_dir()
        missing = []
        for entry in getattr(self, '_ribbon_actions', []):
            fname = icons.get(entry['name'])
            if not fname:
                continue
            if (folder / fname).is_file():
                entry['action'].setIcon(QIcon(str(folder / fname)))
            else:
                missing.append(fname)
        if missing:
            self._set_status(f"Missing icons: {', '.join(missing)}")

    def _apply_custom_icons(self): #vers 1
        """First call applies the saved layout, then icons are redrawn"""
        if not getattr(self, '_ribbon_layout_done', False):
            self._ribbon_layout_done = True
            self._apply_ribbon_layout()
        self._render_ribbon_icons()
        self._apply_custom_icon_images()

    def _ribbon_layout_snapshot(self) -> dict: #vers 1
        """Saved button order, dividers and hidden buttons per toolbar"""
        names = {id(e['action']): e['name']
                 for e in getattr(self, '_ribbon_actions', [])}
        bars, hidden = {}, []
        for tb in self.ribbon_toolbars():
            row = []
            for act in tb.actions():
                if act.isSeparator():
                    row.append('|')
                elif id(act) in names:
                    row.append(names[id(act)])
                    if not act.isVisible():
                        hidden.append(names[id(act)])
                else:
                    row = None
                    break
            if row is not None and tb.objectName():
                bars[tb.objectName()] = row
        return {'toolbars': bars, 'hidden': hidden}

    def _save_ribbon_layout(self): #vers 1
        """Store button order, dividers and hidden buttons"""
        self._ribbon_config_set('ribbon_layout', self._ribbon_layout_snapshot())

    def _apply_ribbon_layout(self): #vers 1
        """Rebuild toolbars from the saved layout; new buttons append at the end"""
        layout = self._ribbon_config_get('ribbon_layout')
        if not layout:
            return
        entries = {e['name']: e for e in getattr(self, '_ribbon_actions', [])}
        current = self._ribbon_layout_snapshot()['toolbars']
        bars = {tb.objectName(): tb for tb in self.ribbon_toolbars()}

        for name in layout.get('toolbars', {}):
            if name not in bars:
                bars[name] = self.ribbon_toolbar(name)
                current[name] = []

        managed = [bars[n] for n in current]
        for tb in managed:
            for act in list(tb.actions()):
                tb.removeAction(act)

        placed = set()
        for name, row in layout.get('toolbars', {}).items():
            tb = bars.get(name)
            if tb is None or tb not in managed:
                continue
            for item in row:
                if item == '|':
                    tb.addSeparator()
                elif item in entries and item not in placed:
                    tb.addAction(entries[item]['action'])
                    placed.add(item)

        for name, entry in entries.items():
            if name not in placed and entry.get('toolbar') in managed:
                entry['toolbar'].addAction(entry['action'])

        hidden = set(layout.get('hidden', []))
        for name, entry in entries.items():
            entry['action'].setVisible(name not in hidden)
