#this belongs in apps/methods/ribbon_system.py - Version: 1
# X-Seti - October 3 2026 - Multi-Emulator Launcher - Shared ribbon toolbar system

"""ribbon_system.py - Ribbon toolbars for MEL windows.

An inner QMainWindow hosts the window content as its central widget and the
tool buttons live in movable QToolBar ribbons. Buttons are QActions so the
Menu drop-down and the Ribbon Manager can enumerate and reorder them. Layout
saves to mel_settings.json (ribbon_state, ribbon_state_version); a save from
an older ribbon structure is rejected via _RIBBON_LAYOUT_VERSION.
"""

##Methods list -
# RibbonMixin.ribbon_action
# RibbonMixin.ribbon_apply_display_mode
# RibbonMixin.ribbon_button
# RibbonMixin.ribbon_context_menu
# RibbonMixin.ribbon_display_mode
# RibbonMixin.ribbon_label
# RibbonMixin.ribbon_restore_state
# RibbonMixin.ribbon_save_state
# RibbonMixin.ribbon_toolbar
# RibbonMixin.ribbon_toolbars
# RibbonMixin.ribbon_widget
# RibbonMixin.ribbon_wrap
# RibbonMixin._ribbon_config_get
# RibbonMixin._ribbon_config_set
# RibbonMixin._ribbon_icon
# RibbonMixin._ribbon_icon_color
# RibbonMixin._ribbon_icon_size
# RibbonMixin._ribbon_set_movable
# RibbonMixin._set_status

from PyQt6.QtCore import Qt, QSize, QByteArray
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMainWindow, QToolBar, QMenu, QLabel

from apps.methods.svg_icon_factory import SVGIconFactory


class RibbonMixin: #vers 1
    """Mix into a MEL window. Set _ribbon_name and bump
    _RIBBON_LAYOUT_VERSION whenever the set of ribbons changes."""

    _ribbon_name = "mel"
    _RIBBON_LAYOUT_VERSION = 1
    _RIBBON_ICON = 20
    _RIBBON_MODES = ('icons_and_text', 'icons_only', 'text_only')

    def ribbon_wrap(self, central) -> QMainWindow: #vers 1
        """Inner QMainWindow that hosts content plus the ribbons"""
        mw = QMainWindow()
        mw.setWindowFlags(Qt.WindowType.Widget)
        mw.setCentralWidget(central)
        self._ribbon_mw = mw
        self._ribbon_actions = []
        return mw

    def ribbon_toolbar(self, name, area=Qt.ToolBarArea.TopToolBarArea,
                       new_row=False) -> QToolBar: #vers 2
        """Add a ribbon to the inner window and return it

        new_row starts a fresh toolbar row so ribbons never overflow
        behind the hidden-buttons chevron.
        """
        mw = self._ribbon_mw
        px = self._ribbon_icon_size()
        tb = QToolBar(name, mw)
        tb.setObjectName(name)
        tb.setIconSize(QSize(px, px))
        tb.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        tb.setMovable(True)
        tb.setFloatable(True)
        tb.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        tb.customContextMenuRequested.connect(
            lambda pos, t=tb: self.ribbon_context_menu(t, pos))
        if new_row:
            mw.addToolBarBreak(area)
        mw.addToolBar(area, tb)
        return tb

    def ribbon_display_mode(self) -> str: #vers 1
        """Icon display mode for ribbons: the window setting, or
        the saved mel_settings value, defaulting to icons and text."""
        mode = getattr(self, 'icon_display_mode', None)
        if not mode:
            mode = self.mel_settings.settings.get('icon_display_mode', 'icons_and_text')
        if mode not in self._RIBBON_MODES:
            mode = 'icons_and_text'
        return mode

    def ribbon_apply_display_mode(self, mode=None): #vers 1
        """Apply icons_only, icons_and_text or text_only to every ribbon"""
        styles = {
            'icons_only': Qt.ToolButtonStyle.ToolButtonIconOnly,
            'icons_and_text': Qt.ToolButtonStyle.ToolButtonTextBesideIcon,
            'text_only': Qt.ToolButtonStyle.ToolButtonTextOnly,
        }
        style = styles[mode or self.ribbon_display_mode()]
        for tb in self.ribbon_toolbars():
            tb.setToolButtonStyle(style)

    def ribbon_button(self, tb, icon_fn, tip, slot, checkable=False,
                      checked=False, enabled=True, text=None) -> QAction: #vers 1
        """Icon button in a ribbon, returned as a QAction.

        icon_fn is an SVGIconFactory method name, or a callable taking
        (size, color). setEnabled/setChecked/setIcon work as on any button.
        """
        name = text or tip
        act = QAction(self._ribbon_icon(icon_fn), name, self._ribbon_mw)
        act.setToolTip(tip)
        act.setCheckable(checkable)
        if checkable:
            act.setChecked(checked)
        act.setEnabled(enabled)
        if checkable:
            act.toggled.connect(slot)
        else:
            act.triggered.connect(slot)
        tb.addAction(act)
        self._ribbon_actions.append({
            'action': act, 'toolbar': tb, 'name': name,
            'icon_fn': icon_fn, 'checkable': checkable,
        })
        return act

    def ribbon_action(self, tb, act) -> QAction: #vers 1
        """Add an existing QAction to a ribbon and register it"""
        tb.addAction(act)
        self._ribbon_actions.append({
            'action': act, 'toolbar': tb, 'name': act.text(),
            'icon_fn': None, 'checkable': act.isCheckable(),
        })
        return act

    def ribbon_label(self, tb, text) -> QLabel: #vers 1
        """Text label inside a ribbon"""
        lbl = QLabel(text)
        lbl.setStyleSheet("padding: 0 4px;")
        tb.addWidget(lbl)
        return lbl

    def ribbon_widget(self, tb, widget): #vers 1
        """Embed any widget at the end of a ribbon"""
        tb.addWidget(widget)
        return widget

    def ribbon_toolbars(self) -> list: #vers 1
        """Every ribbon toolbar, in creation order"""
        mw = getattr(self, '_ribbon_mw', None)
        if mw is None:
            return []
        return [tb for tb in mw.findChildren(QToolBar) if tb.parent() is mw]

    def ribbon_context_menu(self, toolbar, pos): #vers 1
        """Right-click menu for a ribbon"""
        menu = QMenu(self)
        menu.addAction("Save Ribbon Config", self.ribbon_save_state)
        menu.addSeparator()
        menu.addAction("Lock All Toolbars", lambda: self._ribbon_set_movable(False))
        menu.addAction("Unlock All Toolbars", lambda: self._ribbon_set_movable(True))
        menu.exec(toolbar.mapToGlobal(pos))

    def _ribbon_set_movable(self, movable): #vers 1
        """Lock or unlock every ribbon"""
        for tb in self.ribbon_toolbars():
            tb.setMovable(movable)

    def _ribbon_icon(self, icon_fn): #vers 2
        """Build a ribbon QIcon from a factory name or callable"""
        color = self._ribbon_icon_color()
        px = self._ribbon_icon_size()
        if callable(icon_fn):
            return icon_fn(px, color)
        return getattr(SVGIconFactory, icon_fn)(px, color)

    def _ribbon_icon_size(self) -> int: #vers 1
        """Ribbon icon size in pixels from the tool config"""
        return int(self._ribbon_config_get('icon_scale', self._RIBBON_ICON) or self._RIBBON_ICON)

    def _ribbon_config_get(self, key, default=None): #vers 1
        """Read one ribbon setting from the tool config json"""
        return self.mel_settings.settings.get(key, default)

    def _ribbon_config_set(self, key, value): #vers 1
        """Write one ribbon setting to the tool config json"""
        self.mel_settings.settings[key] = value
        self.mel_settings.save_mel_settings()

    def _set_status(self, message): #vers 1
        """Show a message in the window status bar"""
        if hasattr(self, 'status_label'):
            self.status_label.setText(message)
        else:
            print(message)

    def _ribbon_icon_color(self): #vers 1
        """Current theme icon colour"""
        if hasattr(self, '_get_icon_color'):
            return self._get_icon_color()
        return None

    def ribbon_save_state(self): #vers 1
        """Save ribbon layout into the tool config json"""
        mw = getattr(self, '_ribbon_mw', None)
        if mw is None:
            return
        try:
            state = mw.saveState(self._RIBBON_LAYOUT_VERSION).toHex().data().decode()
            self.mel_settings.settings['ribbon_state'] = state
            self.mel_settings.settings['ribbon_state_version'] = self._RIBBON_LAYOUT_VERSION
            self.mel_settings.save_mel_settings()
            if hasattr(self, 'log_message'):
                self.log_message("Ribbon config saved")
        except Exception as e:
            print(f"[{self._ribbon_name}] ribbon_save_state error: {e}")

    def ribbon_restore_state(self): #vers 1
        """Restore a saved ribbon layout, rejecting older structures

        Every ribbon is forced visible afterwards so a stale state can
        never leave one hidden with no way back.
        """
        mw = getattr(self, '_ribbon_mw', None)
        if mw is None:
            return
        try:
            settings = self.mel_settings.settings
            state = settings.get('ribbon_state')
            version = settings.get('ribbon_state_version')
            if state and version == self._RIBBON_LAYOUT_VERSION:
                mw.restoreState(QByteArray.fromHex(state.encode()),
                                self._RIBBON_LAYOUT_VERSION)
        except Exception as e:
            print(f"[{self._ribbon_name}] ribbon_restore_state error: {e}")
        finally:
            for tb in self.ribbon_toolbars():
                tb.setVisible(True)
