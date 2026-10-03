#!/usr/bin/env python3
#this belongs in apps/gui/emu_launcher_gui.py - Version: 23
# X-Seti - November30 2025 - Multi-Emulator Launcher - Main GUI

"""
Multi-Emulator Launcher GUI
Main window with 3-panel layout for emulator management
"""

#TODO - Artwork comes with RetroArch - if retroarch is installed, borrow the artwork from that, to replace the thumbnails and display window cover art.
#TODO - Move window functionality is broken.
#TODO - Controller layout models, Playstation 4, 5, X-Box, Generic Layouts.

#Changelog

#November27 v18 - Button Visibility and Font Support
#- Move window functionality is fixed
#- Controller layout models, Playstation 4, 5, X-Box, Generic Layouts added
#-

#November26 v17 - Button Visibility and Font Support
#- Fixed the icons in the svg section, now in their own file..
#- #ccd2cc hex and other hardcoded version removed
#- All SVG icons should be theme aware, Dark on light themes, Light on dark themes.


#November24 v16 - Button Visibility and Font Support
#- Fixed button colors for light themes - calculate from bg_primary with 0.85 brightness
#- Buttons now visible on light backgrounds (no more white on white)
#- Added _style_control_buttons (vers 1) to style Launch/Load/Manager buttons
#- All buttons get proper contrast, borders, and hover states
#- Added _apply_fonts_to_widgets (vers 1) to apply AppSettings fonts
#- Fonts from AppSettings now properly applied to title, panels, buttons
#- Debug output shows which fonts are being applied
#- This fixes both button visibility and font customization support!

#November24 v15.7 - Fix Titlebar Button Colors and Drag Debug
#- Fixed _apply_titlebar_colors (vers 5 -> 6) with !important flags
#- Titlebar buttons now use theme colors (text_primary, button_normal) properly
#- Added size constraints to buttons (30x30) for consistency
#- Added debug output showing button colors being applied
#- Added extensive debug to _is_on_draggable_area (vers 3 -> 4)
#- Debug shows titlebar detection, button positions, click locations
#- This will help identify why drag isn't working

#November24 v15.6 - Fix Theme Color Loading from AppSettings
#- Fixed _get_theme_colors (vers 6 -> 7) to load CURRENT active theme
#- Now reads current_settings.theme to get active theme name
#- Looks for colors in theme.colors or theme root
#- Added extensive debug output showing what's being loaded
#- setdefault() only fills MISSING keys, preserves AppSettings values
#- Titlebar buttons use colors from _get_theme_colors via _apply_titlebar_colors
#- This should now use your actual AppSettings theme colors!

#November24 v15.5 - CRITICAL FIX: Removed Duplicate Method, Fixed Dark Defaults
#- Found and removed duplicate _get_theme_colors at line 1834 (vers 5)
#- Fixed actual _get_theme_colors (vers 6) to use light/dark defaults properly
#- Root cause: Method had DARK defaults for ALL themes (bg_primary=#1a1a1a)
#- Now checks is_dark FIRST, then sets appropriate defaults
#- Light themes get light defaults (#ffffff, #f0f0f0, #000000)
#- Dark themes get dark defaults (#1a1a1a, #2d2d2d, #ffffff)
#- Added debug output to show theme detection and final colors
#- This WILL fix the dark panels on light theme!

#November24 v15.4 - Extreme Debug Mode (Fallback Disabled)
#- Disabled fallback in _get_theme_colors (vers 4 -> 5)
#- Returns BRIGHT PINK/YELLOW colors if AppSettings fails
#- Extensive debug output showing exactly what's happening
#- If you see pink/yellow, AppSettings is NOT providing colors
#- This will help identify the exact failure point

#November24 v15.3 - Fix Theme Color Fetching from AppSettings
#- Fixed _get_theme_colors (vers 3 -> 4) to use self.app_settings instead of self.main_window.app_settings
#- Root cause: Method was looking for app_settings in wrong place (main_window doesn't exist in this context)
#- Now correctly accesses self.app_settings which is set in __init__
#- Added better debug output with checkmarks and sample colors
#- Added traceback on errors for easier debugging
#- This should fix the dark panels on light theme issue

#November24 v15.2 - Debug Version to Identify Theme Color Issues
#- Added debug output in _apply_theme (vers 8 -> 9) to print actual colors being used
#- Prints bg_primary, panel_bg, text_primary, border, accent_primary to terminal
#- This will help identify if AppSettings is providing dark colors on light theme
#- Run app and check terminal output to see what colors are being applied

#November24 v15.1 - Critical Hotfix for Theme Application
#- Fixed _apply_theme (vers 7 -> 8) to apply styles DIRECTLY to widgets
#- AppSettings base stylesheet was overriding MEL-specific styles
#- Now uses widget.setStyleSheet() with !important flags for precedence
#- Lists now correctly show light background on light themes
#- Alternating rows now visible
#- Display frame now properly styled
#- All visual improvements from v15 now working correctly

#November24 v15 - UI Polish and Visual Consistency
#- Added alternating row colors to platform and game lists (like file dialog)
#- Comprehensive theme stylesheet for all widgets (buttons, frames, scrollbars, sliders)
#- All gadgets now use uniform themed colors - no hardcoded styles
#- Added frame around game display panel for professional appearance
#- Welcome message in display panel before ROM scan
#- Theme-based scrollbars and sliders with proper theming
#- Added adjust_brightness helper for calculating alternate row colors
#- Updated _apply_theme (vers 3) with comprehensive widget styling
#- Updated EmulatorDisplayWidget (vers 4) with framed display and welcome message
#- All visual elements now consistent between light and dark themes

#November24 v14 - Fixed misplaced methods and titlebar theming
#- Moved _show_load_core and _on_core_loaded from EmulatorDisplayWidget to EmuLauncherGUI (correct class)
#- Fixed AttributeError: EmulatorDisplayWidget no longer tries to access self.core_launcher  
#- Updated _apply_titlebar_colors (vers 5) to properly theme min/max/close buttons based on theme
#- Light themes now show dark buttons, dark themes show light buttons for proper contrast
#- Fixed window drag functionality - _is_on_draggable_area now properly detects titlebar
#- Updated methods list to include _on_core_loaded and _show_load_core in correct alphabetical order
#- All three manager buttons (Art Manager, Game Manager, Game Ports) fully functional

#November23 v13 - Fixed main launcher parameter passing
#- Updated __init__ (vers 13) to accept core_downloader, core_launcher, gamepad_config
#- Parameters now passed from emu_launcher_main.py properly
#- Maintains backward compatibility with existing initialization

#November22 v12 - Fixed themed titlebar setting to actually work
#- Updated _apply_titlebar_colors (vers 4) to check use_themed_titlebar setting
#- Updated _open_mel_settings (vers 2) to reapply titlebar colors after saving settings
#- Unchecked: White text on dark blue background (always visible)
#- Checked: Uses theme colors from AppSettings
#- Setting now properly toggles between hardcoded and themed titlebar

#November22 v11 - Fixed titlebar button visibility and updated icons to 64x64
#- Fixed _apply_titlebar_colors (vers 3) - buttons now use accent color backgrounds for visibility
#- Updated EmulatorListWidget icon size from 32x32 to 64x64
#- Created mel_settings_dialog.py v4 with themed titlebar checkbox
#- Titlebar buttons now visible in both light and dark themes
#- Better contrast with colored button backgrounds and borders

#November22 v10 - CRITICAL FIX: Theme system now works properly
#- Fixed _apply_titlebar_colors (vers 2) - removed duplicate stylesheet code that was overriding AppSettings
#- Fixed _show_settings_dialog (vers 2) - connects to _on_theme_changed not _apply_theme
#- Theme switching now applies correctly on startup and when changed
#- Removed conflicting stylesheet code that prevented AppSettings themes from loading

#November22 v9 - Added artwork system
#- Created artwork_loader.py (vers 1) for game thumbnails and title images
#- Updated GameListWidget (vers 2) to display 64x64 thumbnails in game list
#- Updated EmulatorDisplayWidget (vers 3) to show title artwork
#- Added show_title_artwork method to display panel
#- Updated _on_platform_selected (vers 4) to pass artwork_loader to game list
#- Updated _on_game_selected (vers 3) to load title artwork on selection
#- Fixed AppSettings signal: uses themeChanged not theme_changed
#- Artwork structure: /artwork/[platform]/thumbnails/ and /artwork/[platform]/titles/

#November22 v8 - Fixed theme switching
#- Connected app_settings.theme_changed signal in __init__
#- Added _on_theme_changed method (vers 1) to handle theme changes
#- Theme switching now works properly instead of staying in fallback

#November22 v7 - Fixed theme integration issues
#- Removed obsolete _apply_table_theme_styling method (no self.table widget)
#- Updated _apply_theme (vers 2) to call _apply_titlebar_colors
#- Added _apply_titlebar_colors (vers 1) for titlebar text/button visibility in dark themes
#- Fixed AttributeError on startup

#November20 - Added - PlatformScanner for dynamic platform discovery
#- 1. Add PlatformScanner import at top
#- 2. Initialize platform_scanner in __init__ (vers 5)
#- 3. Update _create_left_panel to use scanner (vers 2)
#- 4. Add _refresh_platforms method (vers 1)
#- 5. Update _on_platform_selected to use platform info (vers 3)

import os
import tempfile
import subprocess
import shutil
import struct
import sys
import io
import numpy as np
from pathlib import Path
from typing import Optional, List, Dict, Tuple
from PyQt6.QtSvg import QSvgRenderer



base_dir = "config/"

# PyQt6 imports
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QListWidget, QListWidgetItem, QLabel, QPushButton, QFrame, QTabWidget, QGroupBox, QFormLayout, QDialog, QMessageBox, QTextBrowser)
from PyQt6.QtWidgets import (QApplication, QSlider, QCheckBox, QTreeWidget,
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QListWidget, QDialog, QFormLayout, QSpinBox,  QListWidgetItem, QLabel, QPushButton, QFrame, QFileDialog, QLineEdit, QTextEdit, QMessageBox, QScrollArea, QGroupBox, QTableWidget, QTableWidgetItem, QColorDialog, QHeaderView, QAbstractItemView, QMenu, QComboBox, QInputDialog, QTabWidget, QDoubleSpinBox, QRadioButton, QToolButton
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QPoint, QRect, QByteArray
from PyQt6.QtGui import QFont, QIcon, QPixmap, QImage, QPainter, QPen, QBrush,  QColor, QCursor, QPalette
from PyQt6.QtSvg import QSvgRenderer

# Import SVG icon factory
from apps.methods.svg_icon_factory import SVGIconFactory
from apps.methods.ribbon_system import RibbonMixin
from apps.methods.ribbon_dialog import RibbonIconsMixin
from apps.components.emulator_embed_widget import EmulatorEmbedWidget
from apps.methods.platform_scanner import PlatformScanner
from apps.methods.platform_icons import PlatformIcons
from apps.methods.artwork_loader import ArtworkLoader
from apps.methods.system_core_scanner import SystemCoreScanner
from apps.gui.mel_settings_dialog import MELSettingsDialog
from apps.gui.mel_settings_manager import MELSettingsManager
from apps.utils.debug_logger import debug, info, warning, error, verbose, init_logger
from apps.gui.game_manager_dialog import GameManagerDialog, GameConfig
from apps.gui.ports_manager_dialog import PortsManagerDialog
from apps.gui.load_core_dialog import LoadCoreDialog
from apps.gui.database_manager_dialog import DatabaseManagerDialog
from apps.methods.database_manager import DatabaseManager
from apps.methods.mel_app_icon import generate_icon, save_icon_to_file, get_mel_svg
from apps.methods.system_core_scanner import SystemCoreScanner

# Subsystems created by __init__ when not injected by the caller
from apps.methods.core_downloader import CoreDownloader
from apps.core.core_launcher import CoreLauncher
from apps.methods.rom_loader import RomLoader
from apps.methods.game_scanner import GameScanner
from apps.methods.bios_manager import BiosManager


# Import AppSettings
try:
    from apps.utils.app_settings_system import AppSettings, SettingsDialog
    APPSETTINGS_AVAILABLE = True
except ImportError:
    APPSETTINGS_AVAILABLE = False
    print("Warning: AppSettings not available")

##METHODS LIST ORDER (ALPHABETICAL):
# __init__
# closeEvent
# mouseDoubleClickEvent
# mouseMoveEvent
# mousePressEvent
# mouseReleaseEvent
# paintEvent
# resizeEvent
# setup_ui
# _adjust_brightness
# _apply_fallback_theme
# _apply_fonts_to_widgets
# _apply_theme
# _apply_titlebar_colors
# _browse_and_scan
# _create_close_icon
# _create_left_panel
# _create_maximize_icon
# _create_middle_panel
# _create_minimize_icon
# _create_right_panel
# _create_status_bar
# _create_titlebar
# _download_game_artwork
# _enable_move_mode
# _get_resize_corner
# _get_theme_colors
# _handle_corner_resize
# _is_on_draggable_area
# _load_fonts_from_settings
# _normalize_port_name
# _on_artwork_downloaded
# _on_core_loaded
# _on_game_config_saved
# _on_game_selected
# _on_launch_game
# _on_platform_selected
# _on_port_selected
# _on_stop_emulation
# _on_theme_changed
# _open_mel_settings
# _open_rom_folder
# _refresh_platforms
# _save_config
# _scan_roms
# _setup_controller
# _show_about_dialog
# _show_database_manager
# _show_game_manager
# _show_load_core
# _show_ports_manager
# _show_scan_roms_context_menu
# _show_settings_context_menu
# _show_settings_dialog
# _show_shaders_dialog
# _show_window_context_menu
# _style_control_buttons
# _toggle_maximize
# _toggle_upscale_native
# _update_cursor


# App configuration
App_name = "Multi-Emulator Launcher"
DEBUG_STANDALONE = True

class EmulatorListWidget(QListWidget): #vers 2
    """Panel 1: List of emulator platforms with icon support"""

    platform_selected = pyqtSignal(str)

    def __init__(self, parent=None, display_mode="icons_and_text"): #vers 5
        super().__init__(parent)
        self.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.currentRowChanged.connect(self.on_selection_changed)
        self.display_mode = display_mode
        self.setIconSize(QSize(64, 64))  # Increased from 32x32 to 64x64
        
        # Enable alternating row colors for visual distinction
        self.setAlternatingRowColors(True)

        # Enable context menu
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

        # Hidden platforms storage
        self.hidden_platforms = set()

    def _show_context_menu(self, position): #vers 4
        """Show right-click context menu"""
        item = self.itemAt(position)

        from PyQt6.QtWidgets import QMenu, QFileDialog
        menu = QMenu(self)

        # If clicked on an item, show platform options
        if item:
            platform = item.data(Qt.ItemDataRole.UserRole)
            if not platform:
                platform = item.text()

            # Configure controller for this platform
            config_action = menu.addAction(f"Configure Controller for {platform}")
            config_action.triggered.connect(lambda: self._configure_platform_controller(platform))

            menu.addSeparator()

            # Add "Open As" option to select emulator binary
            open_as_action = menu.addAction(f"Open As (Select Emulator Binary)")
            open_as_action.triggered.connect(lambda: self._open_as_emulator(platform))

            menu.addSeparator()

            hide_action = menu.addAction(f"Hide {platform}")
            hide_action.triggered.connect(lambda: self._hide_platform(platform))

            menu.addSeparator()

        # Show hidden platforms submenu (always available)
        if self.hidden_platforms:
            hidden_menu = menu.addMenu("Show Hidden Platform")
            for hidden_platform in sorted(self.hidden_platforms):
                show_action = hidden_menu.addAction(hidden_platform)
                show_action.triggered.connect(lambda checked, p=hidden_platform: self._show_platform(p))

            menu.addSeparator()
            show_all_action = menu.addAction(f"Show All Hidden ({len(self.hidden_platforms)})")
            show_all_action.triggered.connect(self._show_all_platforms)

        menu.exec(self.mapToGlobal(position))


    def _configure_platform_controller(self, platform): #vers 1
        """Open controller config for specific platform"""
        # Find parent EmuLauncherGUI
        parent_widget = self.parent()
        while parent_widget and not hasattr(parent_widget, '_setup_controller'):
            parent_widget = parent_widget.parent()

        if parent_widget and hasattr(parent_widget, '_setup_controller'):
            # Open controller dialog with platform pre-selected
            from apps.gui.controller_config_dialog import ControllerConfigDialog
            dialog = ControllerConfigDialog(parent_widget.gamepad_config, parent_widget)
            # TODO: Select platform tab and highlight platform
            dialog.exec()


    def _open_as_emulator(self, platform): #vers 1
        """Open emulator binary selection dialog to use for this platform"""
        # Find parent EmuLauncherGUI
        parent_widget = self.parent()
        while parent_widget and not hasattr(parent_widget, '_on_launch_game'):
            parent_widget = parent_widget.parent()

        if parent_widget and hasattr(parent_widget, '_on_launch_game'):
            # Get the selected game from the game list
            game_list = getattr(parent_widget, 'game_list', None)
            if game_list and game_list.currentItem():
                selected_game = game_list.currentItem().text()
                
                # Get the ROM path for the selected game
                rom_path = None
                if hasattr(parent_widget, 'available_roms') and platform in parent_widget.available_roms:
                    for rom_file in parent_widget.available_roms[platform]:
                        if rom_file.stem == selected_game:
                            rom_path = rom_file
                            break
                
                if rom_path:
                    # Open file dialog to select emulator binary
                    from PyQt6.QtWidgets import QFileDialog
                    emulator_path, _ = QFileDialog.getOpenFileName(
                        self, 
                        f"Select Emulator for {platform}", 
                        "", 
                        "Executable Files (*)"
                    )
                    
                    if emulator_path:
                        # Launch the game with the selected emulator
                        parent_widget._launch_with_custom_emulator(platform, rom_path, emulator_path)
                else:
                    from PyQt6.QtWidgets import QMessageBox
                    QMessageBox.warning(self, "No Game Selected", "Please select a game first before using 'Open As'.")
            else:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "No Game Selected", "Please select a game first before using 'Open As'.")


    def _show_all_platforms(self): #vers 1
        """Show all hidden platforms at once"""
        self.hidden_platforms.clear()

        # Trigger parent refresh to reload all platforms
        if self.parent():
            parent_widget = self.parent()
            while parent_widget and not hasattr(parent_widget, '_refresh_platforms'):
                parent_widget = parent_widget.parent()
            if parent_widget and hasattr(parent_widget, '_refresh_platforms'):
                parent_widget._refresh_platforms()


    def _hide_platform(self, platform): #vers 1
        """Hide a platform from the list"""
        self.hidden_platforms.add(platform)

        # Remove from list
        for i in range(self.count()):
            item = self.item(i)
            item_platform = item.data(Qt.ItemDataRole.UserRole)
            if not item_platform:
                item_platform = item.text()
            if item_platform == platform:
                self.takeItem(i)
                break


    def _show_platform(self, platform): #vers 1
        """Show a hidden platform"""
        self.hidden_platforms.discard(platform)

        # Would need to re-scan to add it back
        # Trigger parent refresh
        if self.parent():
            parent_widget = self.parent()
            while parent_widget and not hasattr(parent_widget, '_refresh_platforms'):
                parent_widget = parent_widget.parent()
            if parent_widget and hasattr(parent_widget, '_refresh_platforms'):
                parent_widget._refresh_platforms()


    def on_selection_changed(self, row): #vers 2
        """Handle platform selection"""
        if row >= 0:
            item = self.item(row)
            platform = item.data(Qt.ItemDataRole.UserRole)
            if not platform:
                platform = item.text()
            self.platform_selected.emit(platform)


    def populate_platforms(self, platforms, icon_factory=None): #vers 3
        """Populate with platform names and optional icons"""
        self.clear()
        for platform in platforms:
            # Skip hidden platforms
            if platform in self.hidden_platforms:
                continue

            item = QListWidgetItem()

            # Set icon if available and mode allows
            if icon_factory and self.display_mode != "text_only":
                icon = icon_factory.get_platform_icon(platform, size=32)
                item.setIcon(icon)

            # Set text based on display mode
            if self.display_mode == "icons_only":
                item.setText("")
                item.setToolTip(platform)
            else:
                item.setText(platform)

            # Store platform name in data
            item.setData(Qt.ItemDataRole.UserRole, platform)
            self.addItem(item)


    def set_display_mode(self, mode): #vers 1
        """Change display mode and refresh"""
        self.display_mode = mode

        # Update existing items
        for i in range(self.count()):
            item = self.item(i)
            platform = item.data(Qt.ItemDataRole.UserRole)

            if mode == "icons_only":
                item.setText("")
                item.setToolTip(platform)
            elif mode == "text_only":
                item.setText(platform)
                item.setIcon(QIcon())
            else:  # icons_and_text
                item.setText(platform)


class GameListWidget(QListWidget): #vers 2
    """Panel 2: List of games for selected platform with artwork support"""
    
    game_selected = pyqtSignal(str)
    
    def __init__(self, parent=None): #vers 3
        super().__init__(parent)
        self.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.currentRowChanged.connect(self.on_selection_changed)
        self.setIconSize(QSize(64, 64))  # Set icon size for artwork
        
        # Enable alternating row colors for visual distinction
        self.setAlternatingRowColors(True)
        
        self.artwork_loader = None
        self.current_platform = None
        

    def populate_games(self, games, artwork_loader=None, platform=None): #vers 2
        """Populate with game names and artwork thumbnails
        
        Args:
            games: List of game names
            artwork_loader: ArtworkLoader instance for thumbnails
            platform: Platform name for artwork lookup
        """
        self.clear()
        self.artwork_loader = artwork_loader
        self.current_platform = platform
        
        for game in games:
            item = QListWidgetItem()
            item.setText(game)
            
            # Add artwork thumbnail if available
            if artwork_loader and platform:
                icon = artwork_loader.get_game_icon(game, platform, size=64)
                item.setIcon(icon)
            
            self.addItem(item)
            

    def on_selection_changed(self, row): #vers 1
        """Handle game selection"""
        if row >= 0:
            game = self.item(row).text()
            self.game_selected.emit(game)


class EmulatorDisplayWidget(QWidget): #vers 4
    """Panel 3: Emulator display with framed controls and title artwork"""
    
    def __init__(self, parent=None, main_window=None): #vers 5
        super().__init__(parent)
        self.main_window = main_window
        self.title_artwork_label = None
        self.display_frame = None
        self.fullscreen_window = None  # For fullscreen display
        self.current_pixmap = None  # Store current pixmap for fullscreen
        self.setup_ui()
        

    def setup_ui(self): #vers 7
        """Setup display panel with framed display and welcome message"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        # Create framed container for display
        self.display_frame = QFrame()
        self.display_frame.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.display_frame.setLineWidth(2)
        # REMOVED: self.display.setFixedHeight(45)  <-- This was wrong, display doesn't exist yet

        frame_layout = QVBoxLayout(self.display_frame)
        frame_layout.setContentsMargins(10, 10, 10, 10)

        # Title artwork display
        self.title_artwork_label = QLabel()
        self.title_artwork_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_artwork_label.setScaledContents(False)
        self.title_artwork_label.setMinimumHeight(300)

        # Show welcome message initially
        self._show_welcome_message()

        frame_layout.addWidget(self.title_artwork_label)
        frame_layout.addStretch()

        main_layout.addWidget(self.display_frame)

        # Create bottom buttons
        bottom_bar = self._create_bottom_right()
        main_layout.addWidget(bottom_bar)

    def show_title_artwork(self, pixmap): #vers 3
        """Display title artwork
        
        Args:
            pixmap: QPixmap with title artwork or None to clear
        """
        if pixmap and not pixmap.isNull():
            # Store pixmap for fullscreen
            self.current_pixmap = pixmap
            
            # Clear welcome message if showing
            self.title_artwork_label.setTextFormat(Qt.TextFormat.PlainText)
            
            # Scale pixmap to fit while maintaining aspect ratio
            scaled_pixmap = pixmap.scaled(
                self.title_artwork_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.title_artwork_label.setPixmap(scaled_pixmap)
            self.title_artwork_label.setText("")
            self.title_artwork_label.setStyleSheet("")
            
            # Enable double-click for fullscreen
            self.title_artwork_label.mouseDoubleClickEvent = self._on_artwork_double_clicked
            self.title_artwork_label.setMouseTracking(True)
            self.title_artwork_label.setStyleSheet("QLabel { background-color: white; }")  # Make it clickable
        else:
            # Clear artwork and show text
            self.current_pixmap = None
            self.title_artwork_label.clear()
            self.title_artwork_label.setText("No title artwork")
            self.title_artwork_label.setStyleSheet("font-size: 14pt; padding: 50px;")
    

    def _show_welcome_message(self): #vers 1
        """Show welcome message in display panel"""
        welcome_html = """
        <div style='text-align: center; padding: 20px;'>
            <h1 style='color: #3498db; font-size: 32pt; margin-bottom: 10px;'>
                Multi-Emulator Launcher
            </h1>
            <p style='font-size: 16pt; color: #7f8c8d; margin-bottom: 20px;'>
                Welcome to MEL 1.0
            </p>
            <hr style='border: 1px solid #bdc3c7; margin: 20px 50px;'>
            <p style='font-size: 14pt; color: #95a5a6; line-height: 1.8;'>
                <b>Getting Started:</b><br><br>
                1. Click <b>Scan ROMs</b> to detect your games<br>
                2. Select a platform from the left panel<br>
                3. Choose a game from the middle panel<br>
                4. Click <b>Launch Game</b> to play!
            </p>
            <p style='font-size: 12pt; color: #95a5a6; margin-top: 30px;'>
                Use the managers to configure cores,<br>
                download artwork, and view game ports.
            </p>
        </div>
        """
        
        self.title_artwork_label.setText(welcome_html)
        self.title_artwork_label.setTextFormat(Qt.TextFormat.RichText)
        self.title_artwork_label.setWordWrap(True)
        self.title_artwork_label.setStyleSheet("background-color: transparent; padding: 30px;")
    

    def clear_welcome_message(self): #vers 1
        """Clear welcome message when games are loaded"""
        # Only clear if showing welcome (check for HTML content)
        if self.title_artwork_label.textFormat() == Qt.TextFormat.RichText:
            self.title_artwork_label.clear()
            self.title_artwork_label.setTextFormat(Qt.TextFormat.PlainText)
            self.title_artwork_label.setStyleSheet("")

    def _create_bottom_right(self): #vers 6
        """Create the right buttons with all controls in one line"""
        # Create button bar frame
        rightbar = QFrame()
        rightbar.setFrameStyle(QFrame.Shape.StyledPanel)
        rightbar.setFixedHeight(45)
        rightbar.setObjectName("rightbar")

        button_layout = QHBoxLayout(rightbar)  # Use button_layout, not self.layout
        button_layout.setContentsMargins(5, 5, 5, 5)
        button_layout.setSpacing(5)

        # Icon colour from the theme, or the widget palette before the window exists
        if hasattr(self, 'main_window') and self.main_window and hasattr(self.main_window, '_get_icon_color'):
            icon_color = self.main_window._get_icon_color()
        else:
            icon_color = self.palette().color(QPalette.ColorRole.WindowText).name()
        
        # Store button references as instance attributes for later access
        # Launch button
        self.launch_btn = QPushButton("Launch Game")
        self.launch_btn.setIcon(SVGIconFactory.launch_icon(20, icon_color))
        self.launch_btn.setIconSize(QSize(20, 20))
        self.launch_btn.setMinimumHeight(30)
        self.launch_btn.setToolTip("Launch Emulator")
        self.launch_btn.setEnabled(False)  # Start disabled
        if hasattr(self, 'main_window') and self.main_window:
            self.launch_btn.clicked.connect(self.main_window._on_launch_game)
        button_layout.addWidget(self.launch_btn)

        # Load Core button
        self.load_core_btn = QPushButton("Load Core")
        self.load_core_btn.setIcon(SVGIconFactory.folder_icon(20, icon_color))
        self.load_core_btn.setIconSize(QSize(20, 20))
        self.load_core_btn.setMinimumHeight(30)
        self.load_core_btn.setToolTip("Browse and load emulator cores")
        if hasattr(self, 'main_window') and self.main_window:
            self.load_core_btn.clicked.connect(self.main_window._show_load_core)
        button_layout.addWidget(self.load_core_btn)

        # Art Manager button
        self.gameart_btn = QPushButton("Art Manager")
        self.gameart_btn.setIcon(SVGIconFactory.paint_icon(20, icon_color))
        self.gameart_btn.setIconSize(QSize(20, 20))
        self.gameart_btn.setMinimumHeight(30)
        self.gameart_btn.setToolTip("Download and manage game artwork")
        if hasattr(self, 'main_window') and self.main_window:
            self.gameart_btn.clicked.connect(self.main_window._download_game_artwork)
        button_layout.addWidget(self.gameart_btn)

        # Database Manager button
        self.database_btn = QPushButton("Database")
        self.database_btn.setIcon(SVGIconFactory.database_icon(20, icon_color))
        self.database_btn.setIconSize(QSize(20, 20))
        self.database_btn.setMinimumHeight(30)
        self.database_btn.setToolTip("Manage ROMs, BIOS, and paths database")
        if hasattr(self, 'main_window') and self.main_window:
            self.database_btn.clicked.connect(self.main_window._show_database_manager)
        button_layout.addWidget(self.database_btn)

        button_layout.addStretch()

        # Game Manager button
        self.manage_btn = QPushButton("Game Manager")
        self.manage_btn.setIcon(SVGIconFactory.manage_icon(20, icon_color))
        self.manage_btn.setIconSize(QSize(20, 20))
        self.manage_btn.setMinimumHeight(30)
        self.manage_btn.setToolTip("Configure game settings")
        if hasattr(self, 'main_window') and self.main_window:
            self.manage_btn.clicked.connect(self.main_window._show_game_manager)
        button_layout.addWidget(self.manage_btn)

        # Game Ports button
        self.ports_btn = QPushButton("Game Ports")
        self.ports_btn.setIcon(SVGIconFactory.package_icon(20, icon_color))
        self.ports_btn.setIconSize(QSize(20, 20))
        self.ports_btn.setMinimumHeight(30)
        self.ports_btn.setToolTip("View game ports across systems")
        if hasattr(self, 'main_window') and self.main_window:
            self.ports_btn.clicked.connect(self.main_window._show_ports_manager)
        button_layout.addWidget(self.ports_btn)

        # Stop button
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setIcon(SVGIconFactory.stop_icon(20, icon_color))
        self.stop_btn.setIconSize(QSize(20, 20))
        self.stop_btn.setMinimumHeight(30)
        self.stop_btn.setToolTip("Stop emulation")
        if hasattr(self, 'main_window') and self.main_window:
            self.stop_btn.clicked.connect(self.main_window._on_stop_emulation)
        button_layout.addWidget(self.stop_btn)

        return rightbar

    def _create_control_buttons(self): #vers 2
        """Create bottom control buttons"""
        controls_frame = QFrame()
        controls_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QHBoxLayout(controls_frame)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)

        # Launch button
        self.launch_btn = QPushButton("Launch Game")
        self.launch_btn.setEnabled(False)  # START DISABLED
        # Connect to main window's launch method
        if self.main_window:
            self.launch_btn.clicked.connect(self.main_window._on_launch_game)
        layout.addWidget(self.launch_btn)

        layout.addStretch()

        # Stop button
        stop_btn = QPushButton("Stop")
        # Connect to main window's stop method
        if self.main_window:
            stop_btn.clicked.connect(self.main_window._on_stop_emulation)
        layout.addWidget(stop_btn)

        # Edit Database button
        edit_db_btn = QPushButton("Edit Database")
        if self.main_window:
            edit_db_btn.clicked.connect(self.main_window._show_database_manager)
        layout.addWidget(edit_db_btn)

        return controls_frame

    
    def enable_launch_buttons(self, enabled=True): #vers 1
        """Enable/disable launch buttons"""
        if hasattr(self, 'launch_btn'):
            self.launch_btn.setEnabled(enabled)
        if hasattr(self, 'quick_launch_btn'):
            self.quick_launch_btn.setEnabled(enabled)


    def _on_launch_clicked(self): #vers 1
        """Handle launch button click"""
        if not self.main_window:
            return
            
        platform = self.main_window.current_platform
        rom_path = self.main_window.current_rom_path
        core_launcher = self.main_window.core_launcher
        
        if not all([platform, rom_path, core_launcher]):
            QMessageBox.warning(self, "Launch Error", 
                "Please select a platform and game first")
            return
            
        self.main_window.status_label.setText(f"Launching {rom_path.name}...")
        
        success = core_launcher.launch_game(platform, rom_path)
        
        if success:
            self.main_window.status_label.setText(f"Running: {rom_path.name}")
        else:
            self.main_window.status_label.setText(f"Launch failed: {rom_path.name}")
            QMessageBox.warning(self, "Launch Failed",
                f"Could not launch {rom_path.name}\n\n"
                f"Check that you have the required emulator installed.\n"
                f"See terminal output for details.")
    

    def _on_stop_clicked(self): #vers 1
        """Handle stop button click"""
        if not self.main_window or not self.main_window.core_launcher:
            return
            
        core_launcher = self.main_window.core_launcher
        
        if core_launcher.is_running():
            success = core_launcher.stop_emulation()
            if success:
                self.main_window.status_label.setText("Emulation stopped")
            else:
                self.main_window.status_label.setText("Failed to stop emulation")
        else:
            self.main_window.status_label.setText("No emulation running")

    def _on_artwork_double_clicked(self, event): #vers 1
        """Handle double-click on artwork for fullscreen"""
        if self.current_pixmap and not self.current_pixmap.isNull():
            # Create a fullscreen dialog to show the artwork
            fullscreen_dialog = QDialog(self)
            fullscreen_dialog.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint)
            
            layout = QVBoxLayout(fullscreen_dialog)
            
            # Create label to show the pixmap
            fullscreen_label = QLabel()
            fullscreen_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            fullscreen_label.setScaledContents(True)
            
            # Scale pixmap to screen size while maintaining aspect ratio
            screen_size = fullscreen_dialog.screen().size()
            scaled_pixmap = self.current_pixmap.scaled(
                screen_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            fullscreen_label.setPixmap(scaled_pixmap)
            
            layout.addWidget(fullscreen_label)
            fullscreen_dialog.setLayout(layout)
            
            # Close on escape key or click
            def close_dialog(e):
                fullscreen_dialog.close()
            
            fullscreen_label.mousePressEvent = close_dialog
            fullscreen_dialog.keyPressEvent = lambda e: (
                fullscreen_dialog.close() if e.key() == Qt.Key.Key_Escape else None
            )
            
            fullscreen_dialog.showFullScreen()


class EmuLauncherGUI(RibbonMixin, RibbonIconsMixin, QWidget): #vers 22
    """Main GUI window - Multi-Emulator Launcher"""

    window_closed = pyqtSignal()

    _ribbon_name = "mel"
    _RIBBON_LAYOUT_VERSION = 1

    def __init__(self, parent=None, main_window=None, core_downloader=None, platform_scanner=None,
                rom_loader=None, bios_manager=None, game_scanner=None, core_launcher=None, gamepad_config=None, game_config=None, system_core_scanner=None): #vers 14
        """Initialize Multi-Emulator Launcher GUI

        Args:
            parent: Parent widget (optional)
            main_window: Main window reference (optional)
            core_downloader: CoreDownloader instance (optional)
            core_launcher: CoreLauncher instance (optional)
            gamepad_config: GamepadConfig instance (optional)
            game_config: GameConfig instance (optional)
        """
        print(App_name, "Initializing ...")

        super().__init__(parent)

        # Store core systems passed from main launcher
        self.core_downloader = core_downloader if core_downloader else getattr(self, 'core_downloader', None)
        self.core_launcher = core_launcher if core_launcher else getattr(self, 'core_launcher', None)
        self.gamepad_config = gamepad_config if gamepad_config else getattr(self, 'gamepad_config', None)
        self.platform_scanner = platform_scanner if platform_scanner else getattr(self, 'platform_scanner', None)
        self.rom_loader = rom_loader if rom_loader else getattr(self, 'rom_loader', None)
        self.bios_manager = bios_manager if bios_manager else getattr(self, 'bios_manager', None)
        self.game_scanner = game_scanner if game_scanner else getattr(self, 'game_scanner', None)
        self.system_core_scanner = system_core_scanner if system_core_scanner else getattr(self, 'system_core_scanner', None)

        self.main_window = main_window

        self.button_display_mode = 'both'
        self.last_save_directory = None
        self.standalone_mode = (main_window is None)
        self.game_config = game_config if game_config else GameConfig("config")
        
        # Initialize database manager
        self.database_manager = DatabaseManager()
        
        self.setWindowIcon(generate_icon(64))

        # Set default fonts
        from PyQt6.QtGui import QFont
        default_font = QFont("Fira Sans Condensed", 14)
        self.setFont(default_font)
        self.title_font = QFont("Arial", 14)
        self.panel_font = QFont("Arial", 10)
        self.button_font = QFont("Arial", 10)
        self.infobar_font = QFont("Courier New", 9)

        # Initialize MEL Settings Manager FIRST
        self.mel_settings = MELSettingsManager()

        # Initialize PlatformScanner with MEL settings path (if not provided)
        if not self.platform_scanner:
            roms_dir = self.mel_settings.get_rom_path()
            self.platform_scanner = PlatformScanner(roms_dir)
            # Scan platforms immediately to build database for CoreLauncher
            self.platform_scanner.scan_platforms()

        # Initialize core systems (if not provided)
        if not self.core_downloader:
            self.core_downloader = CoreDownloader(Path.cwd())

        if not self.core_launcher:
            # Build core database from scanned platforms
            platform_db = {}
            if self.platform_scanner and hasattr(self.platform_scanner, 'platforms'):
                platform_db = self.platform_scanner.platforms
            
            self.core_launcher = CoreLauncher(
                Path.cwd(),
                platform_db,
                self.core_downloader
            )

        # Initialize other systems (if not provided)
        if not self.rom_loader:
            config = {
                'rom_path': str(Path.cwd() / "roms"),
                'cache_path': str(Path.cwd() / "cache")
            }
            dynamic_platforms = getattr(self.platform_scanner, 'scan_platforms', lambda: {})()
            self.rom_loader = RomLoader(config, dynamic_platforms)

        if not self.game_scanner:
            config = {
                'rom_path': str(Path.cwd() / "roms"),
                'cache_path': str(Path.cwd() / "cache")
            }
            dynamic_platforms = getattr(self.platform_scanner, 'scan_platforms', lambda: {})()
            self.game_scanner = GameScanner(config, dynamic_platforms)

        if not self.bios_manager:
            self.bios_manager = BiosManager(Path.cwd() / "bios")

        if not self.system_core_scanner:
            self.system_core_scanner = SystemCoreScanner(Path.cwd() / "cores")

        # Load saved configuration
        if 'hidden_platforms' in self.mel_settings.settings:
            self._saved_hidden_platforms = self.mel_settings.settings['hidden_platforms']

        if 'window_geometry' in self.mel_settings.settings:
            geom = self.mel_settings.settings['window_geometry']
            self.resize(geom.get('width', 1400), geom.get('height', 800))
            if 'x' in geom and 'y' in geom:
                self.move(geom['x'], geom['y'])

        # Keyboard shortcut for display mode toggle
        from PyQt6.QtGui import QShortcut, QKeySequence
        self.display_toggle_shortcut = QShortcut(QKeySequence("Ctrl+D"), self)
        self.display_toggle_shortcut.activated.connect(self._toggle_icon_display_mode)

        # Window settings
        self.use_system_titlebar = False
        self.window_always_on_top = False
        self.setWindowTitle(f"{App_name}: Ready")
        self.resize(1400, 800)

        # FIXED: Window flags - MUST include Window flag for KDE Plasma drag support
        self.setWindowFlags(
            Qt.WindowType.Window |  # CRITICAL - enables window manager integration
            Qt.WindowType.FramelessWindowHint  # Removes system decorations
        )

        # Corner resize variables
        self.dragging = False
        self.drag_position = None
        self.resizing = False
        self.resize_corner = None
        self.corner_size = 20
        self.hover_corner = None

        # State tracking for launch functionality
        self.current_platform = None
        self.current_rom_path = None
        self.available_roms = {}
        self.current_process = None  # Track custom emulator processes

        # Initialize icon factory and display mode
        self.platform_icons = PlatformIcons()
        self.icon_display_mode = self.mel_settings.settings.get(
            'icon_display_mode', 'icons_and_text')

        # Initialize artwork loader
        artwork_dir = Path.cwd() / "artwork"
        self.artwork_loader = ArtworkLoader(artwork_dir)

        # Initialize AppSettings
        if APPSETTINGS_AVAILABLE:
            try:
                self.app_settings = AppSettings()
                self._load_fonts_from_settings()
            except Exception as e:
                print(f"Warning: Could not load AppSettings: {e}")
                self.app_settings = None
                self.default_font = QFont("Segoe UI", 9)
                self.title_font = QFont("Adwaita Sans", 10)
                self.panel_font = QFont("Adwaita Sans", 9)
                self.button_font = QFont("Adwaita Sans", 9)
        else:
            self.app_settings = None
            self.default_font = QFont("Segoe UI", 9)
            self.title_font = QFont("Adwaita Sans", 10)
            self.panel_font = QFont("Adwaita Sans", 9)
            self.button_font = QFont("Adwaita Sans", 9)

        # Initialize features BEFORE setup_ui
        self._initialize_features()

        # Setup UI
        self.setup_ui()

        # Apply theme
        self._apply_theme()

        # Enable mouse tracking
        self.setMouseTracking(True)

        if DEBUG_STANDALONE:
            print(f"{App_name} initialized")

        init_logger(self.app_settings)

        # Ensure display_widget exists
        if not hasattr(self, 'display_widget'):
            print("WARNING: display_widget missing")
            self.display_widget = EmulatorDisplayWidget(main_window=self)

    def setup_ui(self): #vers 3
        """Setup main UI layout"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Combined titlebar with all controls
        titlebar = self._create_titlebar()
        main_layout.addWidget(titlebar)

        # Content area with margin
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(5, 5, 5, 5)
        content_layout.setSpacing(5)

        # Main 3-panel splitter
        main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Panel 1: Emulator platforms
        left_panel = self._create_left_panel()
        main_splitter.addWidget(left_panel)

        # Panel 2: Game list
        middle_panel = self._create_middle_panel()
        main_splitter.addWidget(middle_panel)

        # Panel 3: Display and controls
        right_panel = self._create_right_panel()
        main_splitter.addWidget(right_panel)

        # Set proportions (2:3:5)
        main_splitter.setStretchFactor(0, 2)
        main_splitter.setStretchFactor(1, 3)
        main_splitter.setStretchFactor(2, 5)

        content_layout.addWidget(main_splitter)

        # Status bar
        status_bar = self._create_status_bar()
        content_layout.addWidget(status_bar)

        # Ribbons live in an inner QMainWindow hosting the content
        self._ribbon_mw = self.ribbon_wrap(content_widget)
        self._build_ribbons()
        self._apply_ribbon_theme()
        self.ribbon_apply_display_mode()
        self._apply_custom_icons()
        self.ribbon_restore_state()

        main_layout.addWidget(self._ribbon_mw)


    def _load_fonts_from_settings(self): #vers 1
        """Load font settings from AppSettings"""
        if not self.app_settings:
            return

        settings = self.app_settings

        self.default_font = QFont(
            settings.get('default_font_family', 'Segoe UI'),
            settings.get('default_font_size', 9)
        )

        self.title_font = QFont(
            settings.get('title_font_family', 'Adwaita Sans'),
            settings.get('title_font_size', 10)
        )

        self.panel_font = QFont(
            settings.get('panel_font_family', 'Adwaita Sans'),
            settings.get('panel_font_size', 9)
        )

        self.button_font = QFont(
            settings.get('button_font_family', 'Adwaita Sans'),
            settings.get('button_font_size', 9)
        )

        self.setFont(self.default_font)


    def _create_titlebar(self): #vers 6
        """Create combined titlebar with all controls in one line - theme aware"""
        self.titlebar = QFrame()
        self.titlebar.setFrameStyle(QFrame.Shape.StyledPanel)
        self.titlebar.setFixedHeight(45)
        self.titlebar.setObjectName("titlebar")

        # Install event filter for drag detection
        self.titlebar.installEventFilter(self)
        self.titlebar.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.titlebar.setMouseTracking(True)

        self.layout = QHBoxLayout(self.titlebar)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)

        # Get icon color from theme
        icon_color = self._get_icon_color()

        # Menu drop-down - every MEL command, grouped like the ribbons
        self.menu_btn = QToolButton()
        self.menu_btn.setFont(self.button_font)
        self.menu_btn.setText("Menu")
        self.menu_btn.setIcon(SVGIconFactory.menu_icon(20, icon_color))
        self.menu_btn.setIconSize(QSize(20, 20))
        self.menu_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.menu_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.menu_btn.setMenu(QMenu(self.menu_btn))
        self.menu_btn.menu().aboutToShow.connect(
            lambda: (self.menu_btn.menu().clear(), self._build_full_menu(self.menu_btn.menu())))
        self.menu_btn.setToolTip("All Multi-Emulator Launcher commands")
        self.layout.addWidget(self.menu_btn)

        # Settings button
        self.settings_btn = QPushButton()
        self.settings_btn.setFont(self.button_font)
        self.settings_btn.setIcon(SVGIconFactory.settings_icon(20, icon_color))
        self.settings_btn.setText("Settings")
        self.settings_btn.setIconSize(QSize(30, 30))
        self.settings_btn.setToolTip("Settings")
        self.settings_btn.clicked.connect(self._open_mel_settings)
        self.settings_btn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.settings_btn.customContextMenuRequested.connect(self._show_settings_context_menu)
        self.layout.addWidget(self.settings_btn)

        self.layout.addStretch()

        # App title in center
        self.title_label = QLabel(App_name)
        self.title_label.setFont(self.title_font)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.title_label)

        self.layout.addStretch()

        self.detect_btn = QPushButton()
        self.detect_btn.setIcon(SVGIconFactory.search_icon(20, icon_color))
        self.detect_btn.setText("")
        self.detect_btn.setIconSize(QSize(20, 20))
        self.detect_btn.setFixedSize(32, 32)
        self.detect_btn.setToolTip("Detect Installed Emulators")
        self.detect_btn.clicked.connect(self._show_detection_results)
        self.layout.addWidget(self.detect_btn)

        # Scan ROMs button
        self.scan_roms_btn = QPushButton()
        self.scan_roms_btn.setFont(self.button_font)
        self.scan_roms_btn.setIcon(SVGIconFactory.folder_icon(20, icon_color))
        self.scan_roms_btn.setText("Scan ROMs")
        self.scan_roms_btn.setIconSize(QSize(30, 30))
        self.scan_roms_btn.setToolTip("Scan for ROM files")
        self.scan_roms_btn.clicked.connect(self._scan_roms)
        self.scan_roms_btn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.scan_roms_btn.customContextMenuRequested.connect(self._show_scan_roms_context_menu)
        self.layout.addWidget(self.scan_roms_btn)

        # BIOS Manager button
        self.scan_bios_btn = QPushButton()
        self.scan_bios_btn.setIcon(SVGIconFactory.chip_icon(20, icon_color))
        self.scan_bios_btn.setText("Scan BIOS")
        self.scan_bios_btn.setIconSize(QSize(30, 30))
        self.scan_bios_btn.setToolTip("Scan and manage system BIOS files")
        self.scan_bios_btn.clicked.connect(self._show_bios_manager)
        self.layout.addWidget(self.scan_bios_btn)

        # Save config button
        self.save_btn = QPushButton()
        self.save_btn.setFont(self.button_font)
        self.save_btn.setIcon(SVGIconFactory.save_icon(20, icon_color))
        self.save_btn.setText("Save Config")
        self.save_btn.setIconSize(QSize(30, 30))
        self.save_btn.setToolTip("Save Configuration")
        # self.save_btn.clicked.connect(self._save_config)  # Uncomment when ready
        self.layout.addWidget(self.save_btn)

        # Controller button
        self.controller_btn = QPushButton()
        self.controller_btn.setFont(self.button_font)
        self.controller_btn.setIcon(SVGIconFactory.controller_icon(20, icon_color))
        self.controller_btn.setText("Setup Controller")
        self.controller_btn.setIconSize(QSize(30, 30))
        self.controller_btn.setToolTip("Configure Controller")
        self.controller_btn.clicked.connect(self._setup_controller)
        self.layout.addWidget(self.controller_btn)

        self.layout.addSpacing(10)

        # Info button
        self.info_btn = QPushButton()
        self.info_btn.setIcon(SVGIconFactory.info_icon(24, icon_color))
        self.info_btn.setFixedSize(35, 35)
        self.info_btn.setIconSize(QSize(30, 30))
        self.info_btn.setToolTip("Information")
        self.info_btn.clicked.connect(self._show_about_dialog)
        self.layout.addWidget(self.info_btn)

        self.layout.addSpacing(10)

        # Properties/Theme button
        self.properties_btn = QPushButton()
        self.properties_btn.setFont(self.button_font)
        self.properties_btn.setIcon(SVGIconFactory.properties_icon(24, icon_color))
        self.properties_btn.setToolTip("Theme")
        self.properties_btn.setFixedSize(35, 35)
        self.properties_btn.clicked.connect(self._show_settings_dialog)
        self.properties_btn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.properties_btn.customContextMenuRequested.connect(self._show_settings_context_menu)
        self.layout.addWidget(self.properties_btn)

        # Window control buttons
        self.minimize_btn = QPushButton()
        self.minimize_btn.setIcon(SVGIconFactory.minimize_icon(20, icon_color))
        self.minimize_btn.setFixedSize(35, 35)
        self.minimize_btn.clicked.connect(self.showMinimized)
        self.minimize_btn.setToolTip("Minimize")
        self.layout.addWidget(self.minimize_btn)

        self.maximize_btn = QPushButton()
        self.maximize_btn.setIcon(SVGIconFactory.maximize_icon(20, icon_color))
        self.maximize_btn.setFixedSize(35, 35)
        self.maximize_btn.clicked.connect(self._toggle_maximize)
        self.maximize_btn.setToolTip("Maximize")
        self.layout.addWidget(self.maximize_btn)

        self.close_btn = QPushButton()
        self.close_btn.setIcon(SVGIconFactory.close_icon(20, icon_color))
        self.close_btn.setFixedSize(35, 35)
        self.close_btn.clicked.connect(self.close)
        self.close_btn.setToolTip("Close")
        self.layout.addWidget(self.close_btn)

        return self.titlebar


    def _create_left_panel(self): #vers 4
        """Create Panel 1: Emulator platforms list with icons"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.Shape.StyledPanel)
        panel.setMinimumWidth(250)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)

        # Header
        header = QLabel("Emulator Platforms")
        header.setFont(self.panel_font)
        header.setStyleSheet("font-weight: bold; padding: 5px;")
        layout.addWidget(header)

        # Platform list with icon support - names always shown
        self.platform_list = EmulatorListWidget(display_mode='icons_and_text')
        self.platform_list.platform_selected.connect(self._on_platform_selected)
        layout.addWidget(self.platform_list)

        # Scan for platforms dynamically
        discovered_platforms = self.platform_scanner.get_platforms()

        if discovered_platforms:
            # Pass icon_factory if available
            icon_factory = getattr(self, 'platform_icons', None)
            self.platform_list.populate_platforms(discovered_platforms, icon_factory)
            print(f"Loaded {len(discovered_platforms)} platform(s): {', '.join(discovered_platforms)}")
        else:
            # No platforms found - show helpful message
            self.platform_list.clear()
            placeholder = QListWidgetItem("No platforms found")
            placeholder.setFlags(Qt.ItemFlag.NoItemFlags)
            self.platform_list.addItem(placeholder)

            info = QListWidgetItem("Place ROMs in /roms/[Platform]/")
            info.setFlags(Qt.ItemFlag.NoItemFlags)
            self.platform_list.addItem(info)

            print("No platforms found. Create directories in /roms/")

        # Add refresh button
        refresh_btn = QPushButton("Refresh Platforms")
        refresh_btn.clicked.connect(self._refresh_platforms)
        layout.addWidget(refresh_btn)

        if hasattr(self, '_saved_hidden_platforms'):
            self.platform_list.hidden_platforms = set(self._saved_hidden_platforms)

        return panel


    def _create_middle_panel(self): #vers 1
        """Create Panel 2: Game list for selected platform"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.Shape.StyledPanel)
        panel.setMinimumWidth(250)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)

        # Header
        header = QLabel("Games")
        header.setFont(self.panel_font)
        header.setStyleSheet("font-weight: bold; padding: 5px;")
        layout.addWidget(header)

        # Game list
        self.game_list = GameListWidget()
        self.game_list.game_selected.connect(self._on_game_selected)
        layout.addWidget(self.game_list)

        return panel


    def _create_right_panel(self): #vers 5
        """Create Panel 3: tabbed viewport with vertical icon controls on right"""
        print("\n=== Creating Right Panel ===")

        panel = QFrame()
        panel.setFrameStyle(QFrame.Shape.StyledPanel)
        panel.setMinimumWidth(300)

        # Main horizontal layout (display + icons)
        main_layout = QHBoxLayout(panel)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        # Left side: tabbed viewport - display plus closable tool panels
        display_tab = QWidget()
        display_layout = QVBoxLayout(display_tab)
        display_layout.setContentsMargins(0, 0, 0, 0)

        # Header
        header = QLabel("Emulator Display")
        header.setFont(self.panel_font)
        header.setStyleSheet("font-weight: bold; padding: 5px;")
        display_layout.addWidget(header)

        # Create display widget - use EmulatorEmbedWidget for proper pop-out and fullscreen support
        print("Creating EmulatorEmbedWidget...")
        from apps.components.emulator_embed_widget import EmulatorEmbedWidget
        self.display_widget = EmulatorEmbedWidget(main_window=self, include_controls=False)

        display_layout.addWidget(self.display_widget)

        # Tool panels open as tabs beside the display and close on demand
        self.right_tabs = QTabWidget()
        self.right_tabs.setTabsClosable(True)
        self.right_tabs.setMovable(False)
        self.right_tabs.tabCloseRequested.connect(self._close_right_tab)
        self._right_display_tab = display_tab
        self.right_tabs.addTab(display_tab, "Emulator Display")
        main_layout.addWidget(self.right_tabs, stretch=1)

        # Right side: Vertical icon controls
        print("Creating icon controls...")
        icon_controls = self._create_icon_controls()
        main_layout.addWidget(icon_controls, stretch=0)

        print("=== Right Panel Created ===\n")
        return panel

    def _close_right_tab(self, index): #vers 1
        """Close a tool panel tab; the display tab stays open"""
        widget = self.right_tabs.widget(index)
        if widget is self._right_display_tab:
            return
        self.right_tabs.removeTab(index)
        widget.deleteLater()

    def _right_tabs_by_title(self) -> dict: #vers 1
        """Panel tabs keyed by title"""
        return {self.right_tabs.tabText(i): self.right_tabs.widget(i)
                for i in range(self.right_tabs.count())}

    def add_right_tab(self, title, widget): #vers 1
        """Add a closable panel tab, or focus the one already open"""
        existing = self._right_tabs_by_title().get(title)
        if existing is not None:
            self.right_tabs.setCurrentWidget(existing)
            return existing
        self.right_tabs.addTab(widget, title)
        self.right_tabs.setCurrentWidget(widget)
        return widget

    def _show_results_tab(self, title, text): #vers 1
        """Show read-only results in the right viewport instead of a dialog"""
        self._last_results = (title, text)
        browser = self._right_tabs_by_title().get(title)
        if browser is None:
            browser = QTextBrowser()
            browser.setOpenExternalLinks(False)
            self.add_right_tab(title, browser)
        browser.setPlainText(text)
        self.right_tabs.setCurrentWidget(browser)
        return browser

    def _reopen_last_results(self): #vers 1
        """Reopen the last results tab if it was closed"""
        if not getattr(self, '_last_results', None):
            self._set_status("No results yet - run a scan first")
            return
        title, text = self._last_results
        self._show_results_tab(title, text)


    def _create_icon_controls(self): #vers 7
        """Create vertical icon control buttons - theme aware + display mode buttons"""
        controls_frame = QFrame()
        controls_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        controls_frame.setMaximumWidth(50)
        controls_layout = QVBoxLayout(controls_frame)
        controls_layout.setContentsMargins(5, 5, 5, 5)
        controls_layout.setSpacing(5)

        # Get icon color from theme
        icon_color = self._get_icon_color()

        # Volume Up
        self.vol_up_btn = QPushButton()
        self.vol_up_btn.setIcon(SVGIconFactory.volume_up_icon(20, icon_color))
        self.vol_up_btn.setIconSize(QSize(20, 20))
        self.vol_up_btn.setFixedSize(40, 40)
        self.vol_up_btn.setToolTip("Volume Up")
        controls_layout.addWidget(self.vol_up_btn)

        # Volume Down
        self.vol_down_btn = QPushButton()
        self.vol_down_btn.setIcon(SVGIconFactory.volume_down_icon(20, icon_color))
        self.vol_down_btn.setIconSize(QSize(20, 20))
        self.vol_down_btn.setFixedSize(40, 40)
        self.vol_down_btn.setToolTip("Volume Down")
        controls_layout.addWidget(self.vol_down_btn)

        controls_layout.addSpacing(10)

        # Screenshot
        self.screenshot_btn = QPushButton()
        self.screenshot_btn.setIcon(SVGIconFactory.screenshot_icon(20, icon_color))
        self.screenshot_btn.setIconSize(QSize(20, 20))
        self.screenshot_btn.setFixedSize(40, 40)
        self.screenshot_btn.setToolTip("Screenshot")
        controls_layout.addWidget(self.screenshot_btn)

        # Record (always red, no color param)
        self.record_btn = QPushButton()
        self.record_btn.setIcon(SVGIconFactory.record_icon(20))
        self.record_btn.setIconSize(QSize(20, 20))
        self.record_btn.setFixedSize(40, 40)
        self.record_btn.setToolTip("Record")
        controls_layout.addWidget(self.record_btn)

        controls_layout.addSpacing(10)

        # Display Mode Buttons (Embedded, Pop-out, Fullscreen)
        # Embedded mode button
        self.embed_mode_btn = QPushButton()
        self.embed_mode_btn.setToolTip("Embedded mode (default)")
        self.embed_mode_btn.setIcon(self._create_embed_icon(icon_color))
        self.embed_mode_btn.setIconSize(QSize(20, 20))
        self.embed_mode_btn.setFixedSize(40, 40)
        self.embed_mode_btn.clicked.connect(lambda: self._set_display_mode('embedded'))
        controls_layout.addWidget(self.embed_mode_btn)

        # Pop-out button
        self.popout_mode_btn = QPushButton()
        self.popout_mode_btn.setToolTip("Pop-out to resizable window")
        self.popout_mode_btn.setIcon(self._create_popout_icon(icon_color))
        self.popout_mode_btn.setIconSize(QSize(20, 20))
        self.popout_mode_btn.setFixedSize(40, 40)
        self.popout_mode_btn.clicked.connect(lambda: self._set_display_mode('popout'))
        controls_layout.addWidget(self.popout_mode_btn)

        # Fullscreen button
        self.fullscreen_mode_btn = QPushButton()
        self.fullscreen_mode_btn.setToolTip("Fullscreen mode")
        self.fullscreen_mode_btn.setIcon(self._create_fullscreen_icon(icon_color))
        self.fullscreen_mode_btn.setIconSize(QSize(20, 20))
        self.fullscreen_mode_btn.setFixedSize(40, 40)
        self.fullscreen_mode_btn.clicked.connect(lambda: self._set_display_mode('fullscreen'))
        controls_layout.addWidget(self.fullscreen_mode_btn)

        controls_layout.addStretch()

        return controls_frame

    def _set_display_mode(self, mode): #vers 1
        """Set display mode via display_widget

        Args:
            mode: 'embedded', 'popout', or 'fullscreen'
        """
        if hasattr(self, 'display_widget'):
            if mode == 'embedded' and hasattr(self.display_widget, 'set_window_mode'):
                self.display_widget.set_window_mode('embedded')
            elif mode == 'popout' and hasattr(self.display_widget, 'set_popout'):
                self.display_widget.set_popout()
            elif mode == 'fullscreen' and hasattr(self.display_widget, 'set_fullscreen'):
                self.display_widget.set_fullscreen()

    def _create_embed_icon(self, color): #vers 1
        """Create embedded window icon"""
        from PyQt6.QtGui import QPixmap, QPainter
        from PyQt6.QtSvg import QSvgRenderer

        svg = f'''<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <rect x="2" y="2" width="20" height="20" fill="none" stroke="{color}" stroke-width="2"/>
            <rect x="5" y="5" width="14" height="14" fill="none" stroke="{color}" stroke-width="1.5"/>
        </svg>'''

        pixmap = QPixmap(24, 24)
        pixmap.fill(Qt.GlobalColor.transparent)

        renderer = QSvgRenderer(svg.encode())
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()

        return QIcon(pixmap)

    def _create_popout_icon(self, color): #vers 1
        """Create pop-out window icon"""
        from PyQt6.QtGui import QPixmap, QPainter
        from PyQt6.QtSvg import QSvgRenderer

        svg = f'''<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <rect x="2" y="6" width="14" height="14" fill="none" stroke="{color}" stroke-width="2"/>
            <polyline points="18,2 22,2 22,6" fill="none" stroke="{color}" stroke-width="2"/>
            <line x1="22" y1="2" x2="14" y2="10" stroke="{color}" stroke-width="2"/>
        </svg>'''

        pixmap = QPixmap(24, 24)
        pixmap.fill(Qt.GlobalColor.transparent)

        renderer = QSvgRenderer(svg.encode())
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()

        return QIcon(pixmap)

    def _create_fullscreen_icon(self, color): #vers 1
        """Create fullscreen icon"""
        from PyQt6.QtGui import QPixmap, QPainter
        from PyQt6.QtSvg import QSvgRenderer

        svg = f'''<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <polyline points="4,10 4,4 10,4" fill="none" stroke="{color}" stroke-width="2"/>
            <polyline points="20,14 20,20 14,20" fill="none" stroke="{color}" stroke-width="2"/>
            <polyline points="14,4 20,4 20,10" fill="none" stroke="{color}" stroke-width="2"/>
            <polyline points="10,20 4,20 4,14" fill="none" stroke="{color}" stroke-width="2"/>
        </svg>'''

        pixmap = QPixmap(24, 24)
        pixmap.fill(Qt.GlobalColor.transparent)

        renderer = QSvgRenderer(svg.encode())
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()

        return QIcon(pixmap)

    def _create_status_bar(self): #vers 1
        """Create bottom status bar"""
        status_bar = QFrame()
        status_bar.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Sunken)
        status_bar.setFixedHeight(22)

        layout = QHBoxLayout(status_bar)
        layout.setContentsMargins(5, 0, 5, 0)
        layout.setSpacing(15)

        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)

        layout.addStretch()

        self.platform_status = QLabel("Platform: None")
        layout.addWidget(self.platform_status)

        self.game_status = QLabel("Game: None")
        layout.addWidget(self.game_status)

        return status_bar


    def _refresh_platforms(self): #vers 3
        """Refresh platform list using current ROM path from settings"""
        # Get ROM path from MEL settings
        roms_dir = self.mel_settings.get_rom_path()

        # Update platform scanner with new path
        self.platform_scanner = PlatformScanner(roms_dir)

        # Scan for platforms - CORRECT METHOD NAME
        discovered_platforms = self.platform_scanner.scan_platforms()

        if discovered_platforms:
            platform_names = list(discovered_platforms.keys())
            # PASS icon_factory here
            self.platform_list.populate_platforms(platform_names, self.platform_icons)

            if hasattr(self, 'status_label'):
                self.status_label.setText(f"Found {len(platform_names)} platform(s)")
        else:
            self.platform_list.clear()
            placeholder = QListWidgetItem("No platforms found")
            placeholder.setFlags(Qt.ItemFlag.NoItemFlags)
            self.platform_list.addItem(placeholder)

            if hasattr(self, 'status_label'):
                self.status_label.setText("No platforms found")


    def _show_detection_results(self): #vers 1
        """Show comprehensive emulator detection results"""
        from apps.methods.emulator_detector import detect_all_emulators
        from PyQt6.QtWidgets import QDialog, QTextBrowser

        base_dir = "cores"

        # Get cores directory
        cores_dir = Path(base_dir) / "cores"

        # Detect all
        all_emulators, summary = detect_all_emulators(cores_dir)

        # Create results dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Emulator Detection Results")
        dialog.setMinimumSize(700, 600)

        layout = QVBoxLayout()

        # Summary at top
        summary_label = QLabel(
            f"<b>Found {summary['total']} total emulator(s)/core(s):</b><br>"
            f"  • System (pacman/yay): {summary['system']}<br>"
            f"  • Flatpak: {summary['flatpak']}<br>"
            f"  • Local Cores: {summary['local_cores']}"
        )
        summary_label.setStyleSheet("padding: 10px; background: #2a2a2a; border-radius: 5px;")
        layout.addWidget(summary_label)

        # Detailed list
        browser = QTextBrowser()
        browser.setOpenExternalLinks(False)

        html = "<h3>Detected Emulators</h3>"
        html += "<style>table { width: 100%; border-collapse: collapse; }"
        html += "th, td { padding: 8px; text-align: left; border-bottom: 1px solid #444; }"
        html += "th { background: #333; }</style>"
        html += "<table>"
        html += "<tr><th>Name</th><th>Platform</th><th>Source</th><th>Path</th></tr>"

        for emu_name, info in sorted(all_emulators.items()):
            source_badge = {
                'system': '🖥️ System',
                'flatpak': '📦 Flatpak',
                'local_core': '💾 Core'
            }.get(info['source'], info['source'])

            html += f"<tr>"
            html += f"<td><b>{emu_name}</b></td>"
            html += f"<td>{info['platform']}</td>"
            html += f"<td>{source_badge}</td>"
            html += f"<td><small>{info['path']}</small></td>"
            html += f"</tr>"

        html += "</table>"
        browser.setHtml(html)
        layout.addWidget(browser)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)

        dialog.setLayout(layout)
        dialog.exec()

    def _show_bios_manager(self): #vers 2
        """Show the BIOS manager in the right viewport as its own tab"""
        icon_color = self._get_icon_color()

        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)

        # BIOS path configuration
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("BIOS Path:"))

        self.bios_path_edit = QLineEdit()
        self.bios_path_edit.setText(self.mel_settings.settings.get('bios_path', str(Path.home() / 'bios')))
        path_layout.addWidget(self.bios_path_edit)

        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self._browse_bios_path)
        path_layout.addWidget(browse_btn)

        layout.addLayout(path_layout)

        # BIOS table
        self.bios_table = QTableWidget()
        self.bios_table.setColumnCount(5)
        self.bios_table.setHorizontalHeaderLabels([
            "System", "File Name", "Size", "MD5", "Status"
        ])
        self.bios_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.bios_table)

        # Buttons
        button_layout = QHBoxLayout()

        scan_btn = QPushButton("Scan BIOS Files")
        scan_btn.setIcon(SVGIconFactory.chip_icon(20, icon_color))
        scan_btn.clicked.connect(self._scan_bios_files)
        button_layout.addWidget(scan_btn)

        verify_btn = QPushButton("Verify All")
        verify_btn.clicked.connect(self._verify_all_bios)
        button_layout.addWidget(verify_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Load existing BIOS data
        self._load_bios_data()

        self.add_right_tab("BIOS Manager", panel)

    def _browse_bios_path(self): #vers 1
        """Browse for BIOS directory"""
        path = QFileDialog.getExistingDirectory(self,"Select BIOS Directory",str(Path.home()))
        if path:
            self.bios_path_edit.setText(path)
            self.mel_settings.settings['bios_path'] = path
            self.mel_settings.save_mel_settings()

    def _scan_bios_files(self): #vers 2
        """Scan BIOS directory and populate table with found files"""
        bios_path = Path(self.bios_path_edit.text())

        if not bios_path.exists():
            QMessageBox.warning(self, "Invalid Path", f"BIOS path does not exist: {bios_path}")
            return

        # Known BIOS files for various systems
        known_bios = {
            'PlayStation': {
                'scph1001.bin': {'size': 524288, 'md5': '924e392ed05558ffdb115408c263dccf'},
                'scph5501.bin': {'size': 524288, 'md5': '490f666e1afb15b7362b406ed1cea246'},
                'scph7001.bin': {'size': 524288, 'md5': '1e68c231d0896b7eadcad1d7d8e76129'},
            },
            'Amiga': {
                'kick31.rom': {'size': 524288, 'md5': '854e8a65f1e0e3e7193e522e93ba1e90'},
                'kick34005.A500': {'size': 524288, 'md5': 'c3c481160866e60d085e436a24db3617'},
            },
            'Sega CD': {
                'bios_CD_U.bin': {'size': 131072, 'md5': '2efd74e3232ff260e371b99f84024f7f'},
                'bios_CD_E.bin': {'size': 131072, 'md5': 'e66fa1dc5820d254611fdcdba0662372'},
                'bios_CD_J.bin': {'size': 131072, 'md5': '278a9397d192149e84e820ac621a8edd'},
            },
            'Sega Saturn': {
                'sega_101.bin': {'size': 524288, 'md5': '85ec9ca47d8f6807718151cbcca8b964'},
                'mpr-17933.bin': {'size': 524288, 'md5': '3240872c70984b6cbfda1586cab68dbe'},
            },
            'PC Engine CD': {
                'syscard3.pce': {'size': 262144, 'md5': '38179df8f4ac870017db21ebcbf53114'},
            },
            'Neo Geo CD': {
                'neocd_z.rom': {'size': 131072, 'md5': 'f39572af7584cb5b3f70ae8cc848aba2'},
                'neocd_f.rom': {'size': 524288, 'md5': '8834880c33164ccbe6476b559f3e37de'},
            },
        }

        # Clear table
        self.bios_table.setRowCount(0)

        # Database to save
        bios_database = {}

        # Scan for BIOS files
        found_files = list(bios_path.rglob('*'))

        for file_path in found_files:
            if file_path.is_file():
                # Check if this matches any known BIOS
                for system, bios_list in known_bios.items():
                    for bios_name, expected_info in bios_list.items():
                        if file_path.name.lower() == bios_name.lower():
                            # Calculate MD5
                            import hashlib
                            md5_hash = hashlib.md5()
                            with open(file_path, 'rb') as f:
                                for chunk in iter(lambda: f.read(4096), b""):
                                    md5_hash.update(chunk)
                            actual_md5 = md5_hash.hexdigest()

                            # Check status
                            if expected_info.get('md5') == actual_md5:
                                status = "Verified"
                            else:
                                status = "Unknown Version"

                            # Add to table
                            self._add_bios_to_table(system, file_path, expected_info, actual_md5, status)

                            # Save to database
                            if system not in bios_database:
                                bios_database[system] = {}

                            size_mb = file_path.stat().st_size / 1024 / 1024
                            bios_database[system][file_path.name] = {
                                'path': str(file_path),
                                'size': f"{size_mb:.2f} MB",
                                'md5': actual_md5,
                                'status': status
                            }

        # Save to settings
        self.mel_settings.settings['bios_database'] = bios_database
        self.mel_settings.save_mel_settings()

        if self.bios_table.rowCount() == 0:
            QMessageBox.information(self, "No BIOS Found",
                                   f"No recognized BIOS files found in:\n{bios_path}")
        else:
            QMessageBox.information(self, "BIOS Scan Complete",
                                   f"Found {self.bios_table.rowCount()} BIOS file(s)")

    def _add_bios_to_table(self, system, file_path, expected_info, actual_md5, status): #vers 2
        """Add BIOS file to table with all details"""
        row = self.bios_table.rowCount()
        self.bios_table.insertRow(row)

        # System
        self.bios_table.setItem(row, 0, QTableWidgetItem(system))

        # File name
        self.bios_table.setItem(row, 1, QTableWidgetItem(file_path.name))

        # Size
        size_mb = file_path.stat().st_size / 1024 / 1024
        self.bios_table.setItem(row, 2, QTableWidgetItem(f"{size_mb:.2f} MB"))

        # MD5 (truncated for display)
        self.bios_table.setItem(row, 3, QTableWidgetItem(actual_md5[:16] + "..."))

        # Status
        self.bios_table.setItem(row, 4, QTableWidgetItem(status))

    def _verify_all_bios(self): #vers 1
        """Verify all BIOS files in table"""
        verified = 0
        warnings = 0

        for row in range(self.bios_table.rowCount()):
            status_item = self.bios_table.item(row, 4)
            if status_item:
                if "Verified" in status_item.text():
                    verified += 1
                elif "Unknown Version" in status_item.text():
                    warnings += 1

        QMessageBox.information(self, "Verification Complete",
                               f"Verified: {verified}\nWarnings: {warnings}\nTotal: {self.bios_table.rowCount()}")

    def _load_bios_data(self): #vers 2
        """Load BIOS data from saved settings and populate table"""
        # Get BIOS database from MEL settings
        bios_db = self.mel_settings.settings.get('bios_database', {})

        if not bios_db:
            # No saved BIOS data, perform initial scan
            self._scan_bios_files()
            return

        # Populate table from saved data
        self.bios_table.setRowCount(0)

        for system, files in bios_db.items():
            for filename, info in files.items():
                row = self.bios_table.rowCount()
                self.bios_table.insertRow(row)

                self.bios_table.setItem(row, 0, QTableWidgetItem(system))
                self.bios_table.setItem(row, 1, QTableWidgetItem(filename))
                self.bios_table.setItem(row, 2, QTableWidgetItem(info.get('size', 'Unknown')))
                self.bios_table.setItem(row, 3, QTableWidgetItem(info.get('md5', 'Unknown')[:16] + "..."))
                self.bios_table.setItem(row, 4, QTableWidgetItem(info.get('status', '? Unverified')))


    def _set_icon_display_mode(self, mode): #vers 4
        """Set the ribbon icon display mode

        Args:
            mode: "icons_only", "text_only", or "icons_and_text"
        """
        self.icon_display_mode = mode

        # Ribbons follow the chosen style
        self.ribbon_apply_display_mode(mode)

        # Platform list keeps its names so the left bar stays readable
        if hasattr(self, 'platform_list') and hasattr(self.platform_list, 'set_display_mode'):
            self.platform_list.set_display_mode('icons_and_text')

        # Save to settings
        self.mel_settings.settings['icon_display_mode'] = mode
        self.mel_settings.save_mel_settings()

        # Update status
        if hasattr(self, 'status_label'):
            mode_names = {
                "icons_only": "Icons Only",
                "text_only": "Text Only",
                "icons_and_text": "Icons & Text"
            }
            self.status_label.setText(f"Display mode: {mode_names.get(mode, mode)}")

    def _toggle_icon_display_mode(self): #vers 2
        """Cycle through icon display modes"""
        modes = ["icons_and_text", "icons_only", "text_only"]

        # Get current mode
        if not hasattr(self, 'icon_display_mode'):
            self.icon_display_mode = self.mel_settings.settings.get('icon_display_mode', 'icons_and_text')

        # Find next mode
        try:
            current_index = modes.index(self.icon_display_mode)
        except ValueError:
            current_index = 0

        next_index = (current_index + 1) % len(modes)

        # Apply new mode
        self._set_icon_display_mode(modes[next_index])

    def _on_launch_game(self): #vers 3
        """Launch selected game with CoreLauncher and embed window"""
        if not self.current_platform or not self.current_rom_path:
            if hasattr(self, 'status_label'):
                self.status_label.setText("No game selected")
            return

        if not self.core_launcher:
            if hasattr(self, 'status_label'):
                self.status_label.setText("CoreLauncher not initialized")
            return

        # Load game config if available
        game_name = self.current_rom_path.stem
        game_config = None
        if self.game_config:
            game_config = self.game_config.get_config(self.current_platform, game_name)

        # Update status
        if hasattr(self, 'status_label'):
            self.status_label.setText(f"Launching {game_name}...")

        # Launch game with config
        success = self.core_launcher.launch_game(
            self.current_platform,
            self.current_rom_path,
            core_name=game_config.get("core") if game_config else None,
            game_config=game_config
        )

        # Embed the emulator window if launch was successful
        if success and self.core_launcher.current_process:
            if hasattr(self, 'display_widget') and hasattr(self.display_widget, 'embed_window'):
                self.display_widget.embed_window(self.core_launcher.current_process)

        # Update status
        if hasattr(self, 'status_label'):
            if success:
                self.status_label.setText(f"Running: {game_name}")
            else:
                self.status_label.setText(f"Launch failed: {game_name}")

    def _launch_with_custom_emulator(self, platform: str, rom_path: Path, emulator_path: str): #vers 1
        """Launch game with a custom emulator binary selected by user"""
        import subprocess
        from PyQt6.QtWidgets import QMessageBox
        
        # Update status
        if hasattr(self, 'status_label'):
            game_name = rom_path.stem
            self.status_label.setText(f"Launching {game_name} with custom emulator...")
        
        try:
            # Launch the custom emulator with the ROM
            cmd = [emulator_path, str(rom_path)]
            
            # Launch in background
            self.current_process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # Update status
            if hasattr(self, 'status_label'):
                self.status_label.setText(f"Running: {game_name} (Custom Emulator)")
            
            print(f"✓ Launched with custom emulator: {rom_path.name}")
            return True
            
        except Exception as e:
            error_msg = f"Failed to launch with custom emulator: {str(e)}"
            print(error_msg)
            
            if hasattr(self, 'status_label'):
                self.status_label.setText(f"Launch failed: {str(e)}")
            
            QMessageBox.critical(self, "Launch Error", error_msg)
            return False

    def _on_platform_selected(self, platform): #vers 5
        """Handle platform selection - scan for actual ROMs using discovered info"""
        self.current_platform = platform
        self.current_rom_path = None
        self.platform_status.setText(f"Platform: {platform}")

        # Disable launch button when platform is selected (until game is selected)
        if hasattr(self, 'launch_btn'):
            self.launch_btn.setEnabled(False)
        if hasattr(self, 'display_widget') and hasattr(self.display_widget, 'launch_btn'):
            self.display_widget.launch_btn.setEnabled(False)

        # Get platform info from scanner
        platform_info = self.platform_scanner.get_platform_info(platform)

        if not platform_info:
            self.game_list.populate_games([], self.artwork_loader, platform)
            self.status_label.setText(f"Platform info not found: {platform}")
            return

        # Get ROM directory from discovered info
        roms_dir = Path(platform_info['path'])

        if not roms_dir.exists():
            self.game_list.populate_games([], self.artwork_loader, platform)
            self.status_label.setText(f"ROM directory not found: {roms_dir}")
            return

        # Get valid extensions from discovered info
        extensions = platform_info.get('extensions', [])

        # Find all ROM files
        rom_files = []
        for ext in extensions:
            rom_files.extend(list(roms_dir.glob(f"*{ext}")))

        # Store ROM paths
        self.available_roms[platform] = rom_files

        # Populate game list with filenames AND artwork
        game_names = [rom.stem for rom in rom_files]
        self.game_list.populate_games(game_names, self.artwork_loader, platform)
        
        # Clear welcome message when games are loaded
        if hasattr(self, 'display_widget') and hasattr(self.display_widget, 'clear_welcome_message') and len(game_names) > 0:
            self.display_widget.clear_welcome_message()

        rom_count = platform_info.get('rom_count', len(rom_files))
        self.status_label.setText(f"Found {rom_count} ROM(s) for {platform}")


    def _on_game_selected(self, game): #vers 4
        """Handle game selection - find ROM path and enable launch"""
        self.game_status.setText(f"Game: {game}")

        if not self.current_platform:
            return

        # Find ROM path for this game
        if self.current_platform in self.available_roms:
            roms = self.available_roms[self.current_platform]

            # Match game name to ROM file
            for rom_path in roms:
                if rom_path.stem == game:
                    self.current_rom_path = rom_path
                    self.status_label.setText(f"Ready to launch: {game}")

                    # ENABLE LAUNCH BUTTON
                    if hasattr(self, 'display_widget') and hasattr(self.display_widget, 'launch_btn'):
                        self.display_widget.launch_btn.setEnabled(True)

                    break

        # Load and display title artwork
        if hasattr(self, 'artwork_loader') and hasattr(self, 'display_widget'):
            title_artwork = self.artwork_loader.get_title_artwork(game, self.current_platform)
            self.display_widget.show_title_artwork(title_artwork)


    def _on_stop_emulation(self): #vers 1
        """Stop current emulation"""
        if not self.core_launcher:
            return

        if self.core_launcher.is_running():
            success = self.core_launcher.stop_emulation()
            if hasattr(self, 'status_label'):
                if success:
                    self.status_label.setText("Emulation stopped")
                else:
                    self.status_label.setText("Failed to stop emulation")
        else:
            if hasattr(self, 'status_label'):
                self.status_label.setText("No emulation running")

    def _show_ports_manager(self): #vers 1
        """Show ports manager dialog"""
        if not self.available_roms:
            QMessageBox.information(
                self,
                "No Games Found",
                "No games found in any platform.\n\n"
                "Add ROMs to platform directories to see ports."
            )
            return

        # Check if any games have multiple ports
        game_counts = {}
        for platform, roms in self.available_roms.items():
            for rom in roms:
                game_name = rom.stem
                # Normalize name
                normalized = self._normalize_port_name(game_name)
                if normalized not in game_counts:
                    game_counts[normalized] = []
                game_counts[normalized].append((platform, game_name))

        # Filter to games with multiple ports
        multi_ports = {k: v for k, v in game_counts.items() if len(v) > 1}

        if not multi_ports:
            QMessageBox.information(
                self,
                "No Ports Found",
                "No games found on multiple platforms.\n\n"
                "Add the same game to different platform folders to see ports."
            )
            return

        # Show ports manager
        dialog = PortsManagerDialog(
            self.platform_scanner,
            self.available_roms,
            self.core_downloader,
            self
        )

        # Connect signal to switch platform/game
        dialog.port_selected.connect(self._on_port_selected)

        dialog.exec()

    def _normalize_port_name(self, game_name: str) -> str: #vers 1
        """Normalize game name for port matching

        Helper method for ports manager
        """
        import re

        name = game_name

        # Remove common ROM tags
        patterns = [
            r'\(USA\)', r'\(Europe\)', r'\(Japan\)', r'\(World\)',
            r'\[!\]', r'\[a\d*\]', r'\[b\d*\]', r'\[t\d*\]',
            r'\(Disk \d+\)', r'\(Disc \d+\)', r'\(Side \w\)',
        ]

        for pattern in patterns:
            name = re.sub(pattern, '', name, flags=re.IGNORECASE)

        name = re.sub(r'[\s_]+', ' ', name).strip()
        return name.lower()

    def _on_port_selected(self, platform: str, game_name: str): #vers 1
        """Handle port selection from ports manager"""
        # Switch to selected platform
        self.current_platform = platform
        self.platform_status.setText(f"Platform: {platform}")

        # Trigger platform selection
        self._on_platform_selected(platform)

        # Find and select the game
        if hasattr(self, 'game_list'):
            for i in range(self.game_list.count()):
                item = self.game_list.item(i)
                if item.text() == game_name:
                    self.game_list.setCurrentRow(i)
                    break

        # Update status
        if hasattr(self, 'status_label'):
            self.status_label.setText(f"Switched to: {platform} - {game_name}")

    def _download_game_artwork(self): #vers 1
        """Download artwork from IGDB for current game"""
        if not self.current_platform or not self.current_rom_path:
            QMessageBox.warning(
                self,
                "No Game Selected",
                "Please select a game first."
            )
            return

        game_name = self.current_rom_path.stem

        # Check if IGDB downloader is initialized
        if not hasattr(self, 'igdb_downloader'):
            # Initialize on first use
            from apps.methods.igdb_downloader import IGDBDownloader
            self.igdb_downloader = IGDBDownloader(self.artwork_loader.artwork_dir)

        # Check if IGDB credentials are configured
        if not self.igdb_downloader.client_id or not self.igdb_downloader.client_secret:
            QMessageBox.warning(
                self,
                "IGDB Not Configured",
                "IGDB API credentials not found.\n\n"
                "The developer needs to add their API key,\n"
                "or you can add your own credentials to:\n"
                "config/igdb_credentials.json\n\n"
                "Get free credentials at:\n"
                "https://dev.twitch.tv/console/apps"
            )
            return

        # Show search dialog
        dialog = IGDBSearchDialog(
            game_name,
            self.current_platform,
            self.igdb_downloader,
            self
        )

        # Connect signal to refresh artwork
        dialog.artwork_downloaded.connect(self._on_artwork_downloaded)

        dialog.exec()

    def _on_artwork_downloaded(self, game_name: str, platform: str): #vers 1
        """Handle artwork download completion"""
        # Clear artwork cache
        if hasattr(self, 'artwork_loader'):
            self.artwork_loader.clear_cache()

        # Reload artwork for current game
        if game_name == self.current_rom_path.stem and platform == self.current_platform:
            title_artwork = self.artwork_loader.get_title_artwork(game_name, platform)
            if title_artwork and hasattr(self, 'display_widget'):
                self.display_widget.show_title_artwork(title_artwork)

        # Refresh game list to show new thumbnails
        if hasattr(self, 'game_list') and self.current_platform:
            current_selection = self.game_list.currentRow()
            # Repopulate with artwork
            game_names = [rom.stem for rom in self.available_roms.get(self.current_platform, [])]
            self.game_list.populate_games(game_names, self.artwork_loader, self.current_platform)
            self.game_list.setCurrentRow(current_selection)

        # Update status
        if hasattr(self, 'status_label'):
            self.status_label.setText(f"Artwork downloaded for: {game_name}")


    def _adjust_brightness(self, hex_color, factor=None): #vers 1
        """Adjust color brightness for alternate row colors
        
        Args:
            hex_color: Hex color string (#RRGGBB)
            factor: Brightness factor (None for auto-detect based on luminance)
            
        Returns:
            Adjusted hex color string
        """
        try:
            # Convert hex to RGB
            rgb = tuple(int(hex_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
            
            # Calculate luminance to determine if we should lighten or darken
            luminance = (0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]) / 255
            
            # Auto-detect factor if not provided
            if factor is None:
                if luminance > 0.5:  # Light theme - darken alternate rows
                    factor = 0.95
                else:  # Dark theme - lighten alternate rows
                    factor = 1.05
            
            # Apply factor
            new_rgb = tuple(min(255, max(0, int(c * factor))) for c in rgb)
            return f"#{new_rgb[0]:02x}{new_rgb[1]:02x}{new_rgb[2]:02x}"
        except:
            # Return original on error
            return hex_color


    def apply_table_theme(self): #vers 2
        """Legacy method - Apply theme styling to table and related components

        Called by the AppSettings system after a theme change.
        """
        self._apply_theme()


    def _safe_log(self, message): #vers 1
        """Safe logging that won't cause circular dependency"""
        if hasattr(self.main_window, 'log_message') and hasattr(self.main_window, 'gui_layout'):
            self.main_window.log_message(message)
        else:
            print(f"GUI Layout: {message}")


    def log_message(self, message): #vers 2
        """Add message to activity log"""
        from PyQt6.QtCore import QDateTime
        timestamp = QDateTime.currentDateTime().toString("hh:mm:ss")
        print(f"[{timestamp}] {message}")


    def _is_dark_theme(self):
        """
        Returns True if the current theme name ends with _Dark.
        Works with hundreds of themes: Retro_Dark, Amiga_Dark, etc.
        Defaults to dark if theme settings are unavailable.
        """
        if APPSETTINGS_AVAILABLE and hasattr(self, "app_settings") and self.app_settings:
            theme_name = self.app_settings.current_settings.get("theme", "").lower()
            return theme_name.endswith("_dark")

        return True

    def _get_theme_colors(self, theme_name: str): #vers 9
        """Returns a dictionary of theme colors from AppSettings current theme"""

        # Complete theme palette - AppSettings guarantees every key
        theme_data = {}
        if APPSETTINGS_AVAILABLE and self.app_settings:
            theme_data.update(self.app_settings.get_theme_colors())
            theme_data.setdefault('accent', theme_data['accent_primary'])
        if not theme_data:
            return {}

        # Determine if this theme is dark or light
        is_dark = self._is_dark_theme()
        debug(f"Theme is dark: {is_dark}", "THEME")
        
        # Build tearoff button stylesheet
        if is_dark:
            button_style = f"""
                QPushButton {{
                    border: 1px solid {theme_data['border']};
                    border-radius: 1px;
                    background-color: {theme_data['bg_secondary']};
                    color: {theme_data['text_primary']};
                    font-size: 12px;
                    font-weight: bold;
                    padding: 0px;
                    margin: 2px;
                }}
                QPushButton:hover {{
                    background-color: {theme_data['accent']};
                    border: 1px solid {theme_data['border']};
                    color: {theme_data['text_secondary']};
                }}
                QPushButton:pressed {{
                    background-color: {theme_data['bg_primary']};
                    border: 1px solid {theme_data['border']};
                    color: {theme_data['text_primary']};
                }}
            """
        else:
            button_style = f"""
                QPushButton {{
                    border: 1px solid {theme_data['border']};
                    border-radius: 1px;
                    background-color: {theme_data['bg_primary']};
                    color: {theme_data['text_primary']};
                    font-size: 12px;
                    font-weight: bold;
                    padding: 0px;
                    margin: 2px;
                }}
                QPushButton:hover {{
                    background-color: {theme_data['accent']};
                    border: 1px solid {theme_data['border']};
                    color: {theme_data['text_secondary']};
                }}
                QPushButton:pressed {{
                    background-color: {theme_data['bg_secondary']};
                    border: 1px solid {theme_data['border']};
                    color: {theme_data['text_primary']};
                }}
            """

        # Inject button style into theme data
        theme_data["button_style"] = button_style

        return theme_data

    def _apply_theme(self): #vers 11
        """Apply comprehensive theme to all GUI elements with direct widget styling"""

        if self.app_settings and APPSETTINGS_AVAILABLE:
            # Get base AppSettings stylesheet
            base_stylesheet = self.app_settings.get_stylesheet()

            # Get theme colors for MEL-specific styling
            theme_colors = self._get_theme_colors("default")
            
            # Calculate alternate row color
            panel_bg = theme_colors['panel_bg']
            panel_bg_alt = self._adjust_brightness(panel_bg)
            
            # Get other themed colors
            text_primary = theme_colors['text_primary']
            border = theme_colors['border']
            accent = theme_colors['accent_primary']
            bg_primary = theme_colors['bg_primary']
            
            # Calculate button color with good contrast
            # Check if theme is light or dark
            bg_rgb = tuple(int(bg_primary.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
            luminance = (0.299 * bg_rgb[0] + 0.587 * bg_rgb[1] + 0.114 * bg_rgb[2]) / 255
            
            if luminance > 0.5:
                # Light theme - darken button background significantly for visibility
                button_bg = self._adjust_brightness(bg_primary, 0.85)  # Much darker
            else:
                # Dark theme - lighten button background
                button_bg = self._adjust_brightness(bg_primary, 1.15)
            
            print(f"Button background calculated: {button_bg} (from bg_primary {bg_primary}, luminance {luminance:.2f})")
            
            # Calculate hover/pressed colors
            accent_hover = self._adjust_brightness(accent, 0.9)
            button_hover = self._adjust_brightness(button_bg, 0.95)

            # Apply base stylesheet first
            self.setStyleSheet(base_stylesheet)

            # Now apply MEL-specific styling DIRECTLY to widgets to override AppSettings
            # This ensures our styles take precedence
            
            # Style platform list
            if hasattr(self, 'platform_list'):
                self.platform_list.setStyleSheet(f"""
                    QListWidget {{
                        background-color: {bg_primary} !important;
                        color: {text_primary} !important;
                        border: 1px solid {border} !important;
                        border-radius: 4px;
                        padding: 2px;
                    }}
                    QListWidget::item {{
                        padding: 5px;
                        border-radius: 3px;
                        color: {text_primary} !important;
                    }}
                    QListWidget::item:alternate {{
                        background-color: {panel_bg_alt} !important;
                    }}
                    QListWidget::item:selected {{
                        background-color: {accent} !important;
                        color: #FFFFFF !important;
                    }}
                    QListWidget::item:hover {{
                        background-color: {accent_hover} !important;
                    }}
                """)
            
            # Style game list
            if hasattr(self, 'game_list'):
                self.game_list.setStyleSheet(f"""
                    QListWidget {{
                        background-color: {bg_primary} !important;
                        color: {text_primary} !important;
                        border: 1px solid {border} !important;
                        border-radius: 4px;
                        padding: 2px;
                    }}
                    QListWidget::item {{
                        padding: 5px;
                        border-radius: 3px;
                        color: {text_primary} !important;
                    }}
                    QListWidget::item:alternate {{
                        background-color: {panel_bg_alt} !important;
                    }}
                    QListWidget::item:selected {{
                        background-color: {accent} !important;
                        color: #FFFFFF !important;
                    }}
                    QListWidget::item:hover {{
                        background-color: {accent_hover} !important;
                    }}
                """)
            
            # Style display widget frame
            if hasattr(self, 'display_widget') and hasattr(self.display_widget, 'display_frame'):
                self.display_widget.display_frame.setStyleSheet(f"""
                    QFrame {{
                        background-color: {bg_primary} !important;
                        border: 2px solid {border} !important;
                        border-radius: 4px;
                    }}
                """)
            
            # Apply titlebar colors
            self._apply_titlebar_colors()
            
            # Style bottom control buttons for better visibility
            #self._style_control_buttons(button_bg, text_primary, accent, border)
            
            # Apply fonts from AppSettings to widgets
            self._apply_fonts_to_widgets()
            self._apply_ribbon_theme()
    

    def _get_icon_color(self): #vers 2
        """Icon colour from the current theme, or the widget palette"""
        if APPSETTINGS_AVAILABLE and self.app_settings:
            return self.app_settings.get_theme_colors()['text_primary']
        return self.palette().color(QPalette.ColorRole.WindowText).name()


    def _apply_fonts_to_widgets(self): #vers 1
        """Apply fonts from AppSettings to all widgets"""
        if not hasattr(self, 'default_font'):
            return
        
        print("\n=== Applying Fonts ===")
        print(f"Default font: {self.default_font.family()} {self.default_font.pointSize()}pt")
        print(f"Title font: {self.title_font.family()} {self.title_font.pointSize()}pt")
        print(f"Panel font: {self.panel_font.family()} {self.panel_font.pointSize()}pt")
        print(f"Button font: {self.button_font.family()} {self.button_font.pointSize()}pt")
        
        # Apply default font to main window
        self.setFont(self.default_font)
        
        # Apply title font to titlebar
        if hasattr(self, 'title_label'):
            self.title_label.setFont(self.title_font)
        
        # Apply panel font to lists
        if hasattr(self, 'platform_list'):
            self.platform_list.setFont(self.panel_font)
        if hasattr(self, 'game_list'):
            self.game_list.setFont(self.panel_font)
        
        # Apply button font to all buttons
        for btn in self.findChildren(QPushButton):
            btn.setFont(self.button_font)
        
        print("Fonts applied to widgets")
        print("======================\n")
    
    def _style_control_buttons(self, button_bg, text_color, accent_color, border_color): #vers 4
        """Style control buttons to match titlebar buttons exactly

        Args:
            button_bg: Background color from titlebar calculation
            text_color: Text color from titlebar calculation
            accent_color: Accent color for hover
            border_color: Border color from theme
        """

        # Use exact same style as titlebar buttons
        button_style = f"""
            QPushButton {{
                background-color: {button_bg} !important;
                border: 1px solid {border_color} !important;
                border-radius: 3px;
                color: {text_color} !important;
                padding: 5px 10px;
                font-weight: bold;
                min-height: 30px;
            }}
            QPushButton:hover {{
                background-color: {accent_color} !important;
                border-color: {border_color} !important;
                color: #FFFFFF !important;
            }}
            QPushButton:pressed {{
                background-color: {self._adjust_brightness(accent_color, 0.85)} !important;
            }}
            QPushButton:disabled {{
                background-color: {self._adjust_brightness(button_bg, 1.05)} !important;
                color: #888888 !important;
                border-color: #555555 !important;
            }}
        """

        # Apply to all buttons in display widget
        if hasattr(self, 'display_widget'):
            for btn in self.display_widget.findChildren(QPushButton):
                btn.setStyleSheet(button_style)

    def _apply_titlebar_colors(self): #vers 9
        """Apply theme colors to titlebar elements - respects themed setting and detects light/dark"""
        if not self.app_settings:
            return

        # Check if themed titlebar is enabled from MEL settings
        use_themed = self.mel_settings.settings.get('use_themed_titlebar', True)

        # Get theme colors
        theme_colors = self._get_theme_colors("default")

        if not use_themed:
            # Theme's dedicated titlebar colours
            text_color = theme_colors['gadgetbar_text']
            bg_color = theme_colors['gadgetbar_bg']
            accent_color = theme_colors['accent_primary']
            button_text_color = theme_colors['button_text_color']
            button_bg_color = theme_colors['button_normal']
            border_color = theme_colors['border']
        else:
            # Themed colours - the theme's text/button pair contrasts
            text_color = theme_colors['text_primary']
            bg_color = theme_colors['panel_bg']
            accent_color = theme_colors['accent_primary']
            border_color = theme_colors['border']
            button_text_color = theme_colors['button_text_color']
            button_bg_color = theme_colors['button_normal']

        # Apply to title label
        if hasattr(self, 'title_label'):
            self.title_label.setStyleSheet(f"""
                QLabel {{
                    color: {text_color} !important;
                    background-color: {bg_color} !important;
                    font-weight: bold;
                    padding: 5px;
                }}
            """)

        # Create unified button style for ALL buttons
        button_style = f"""
            QPushButton {{
                background-color: {button_bg_color} !important;
                border: 1px solid {border_color} !important;
                border-radius: 3px;
                color: {button_text_color} !important;
                padding: 2px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {accent_color} !important;
                border-color: {border_color} !important;
                color: #FFFFFF !important;
            }}
            QPushButton:pressed {{
                background-color: {self._adjust_brightness(accent_color, 0.85)} !important;
            }}
        """

        # Apply to ALL titlebar buttons
        titlebar_buttons = [
            'settings_btn', 'scan_bios_btn', 'scan_roms_btn', 'save_btn', 'controller_btn',
            'properties_btn', 'minimize_btn', 'maximize_btn', 'close_btn'
        ]

        for btn_name in titlebar_buttons:
            if hasattr(self, btn_name):
                btn = getattr(self, btn_name)
                btn.setStyleSheet(button_style)

        # Apply to sidebar control buttons
        sidebar_buttons = ['vol_up_btn', 'vol_down_btn', 'screenshot_btn', 'record_btn']
        for btn_name in sidebar_buttons:
            if hasattr(self, btn_name):
                btn = getattr(self, btn_name)
                btn.setStyleSheet(button_style)

        # Now style the bottom buttons with the same colors
        self._style_control_buttons(button_bg_color, button_text_color, accent_color, border_color)

    def _on_theme_changed(self): #vers 4
        """Handle theme changes - refresh everything including icons"""
        self._apply_theme()
        self._apply_titlebar_colors()

        # Refresh ALL icons with new theme color
        icon_color = self._get_icon_color()

        # Titlebar button icons
        if hasattr(self, 'settings_btn'):
            self.settings_btn.setIcon(SVGIconFactory.settings_icon(20, icon_color))
        if hasattr(self, 'scan_bios_btn'):
            self.scan_bios_btn.setIcon(SVGIconFactory.chip_icon(20, icon_color))
        if hasattr(self, 'scan_roms_btn'):
            self.scan_roms_btn.setIcon(SVGIconFactory.folder_icon(20, icon_color))
        if hasattr(self, 'save_btn'):
            self.save_btn.setIcon(SVGIconFactory.save_icon(20, icon_color))
        if hasattr(self, 'controller_btn'):
            self.controller_btn.setIcon(SVGIconFactory.controller_icon(20, icon_color))
        if hasattr(self, 'info_btn'):
            self.info_btn.setIcon(SVGIconFactory.info_icon(24, icon_color))
        if hasattr(self, 'properties_btn'):
            self.properties_btn.setIcon(SVGIconFactory.properties_icon(24, icon_color))

        # Window control icons
        if hasattr(self, 'minimize_btn'):
            self.minimize_btn.setIcon(SVGIconFactory.minimize_icon(20, icon_color))
        if hasattr(self, 'maximize_btn'):
            self.maximize_btn.setIcon(SVGIconFactory.maximize_icon(20, icon_color))
        if hasattr(self, 'close_btn'):
            self.close_btn.setIcon(SVGIconFactory.close_icon(20, icon_color))

        # Icon control panel icons
        if hasattr(self, 'vol_up_btn'):
            self.vol_up_btn.setIcon(SVGIconFactory.volume_up_icon(20, icon_color))
        if hasattr(self, 'vol_down_btn'):
            self.vol_down_btn.setIcon(SVGIconFactory.volume_down_icon(20, icon_color))
        if hasattr(self, 'screenshot_btn'):
            self.screenshot_btn.setIcon(SVGIconFactory.screenshot_icon(20, icon_color))


    def _refresh_svg_icons(self): #vers 5
        """Recreate all SVG icons with current theme colors"""

        # Titlebar window controls
        if hasattr(self, 'minimize_btn'):
            self.minimize_btn.setIcon(SVGIconFactory.minimize_icon(20, icon_color))
            self.minimize_btn.repaint()  # Force visual update
        if hasattr(self, 'maximize_btn'):
            self.maximize_btn.setIcon(SVGIconFactory.maximize_icon(20, icon_color))
            self.maximize_btn.repaint()
        if hasattr(self, 'close_btn'):
            self.close_btn.setIcon(SVGIconFactory.close_icon(20, icon_color))
            self.close_btn.repaint()
        if hasattr(self, 'properties_btn'):
            self.properties_btn.setIcon(SVGIconFactory.properties_icon(24, icon_color))
            self.properties_btn.repaint()
        if hasattr(self, 'info_btn'):
            self.info_btn.setIcon(SVGIconFactory.info_icon(24, icon_color))
            self.info_btn.repaint()


        # Titlebar main buttons
        if hasattr(self, 'scan_bios_btn'):
            self.scan_bios_btn.setIcon(SVGIconFactory.chip_icon(20, icon_color))
            self.scan_bios_btn.repaint()

        if hasattr(self, 'scan_roms_btn'):
            self.scan_roms_btn.setIcon(SVGIconFactory.folder_icon(16, icon_color))
        if hasattr(self, 'save_btn'):
            self.save_btn.setIcon(SVGIconFactory.save_icon(16, icon_color))
        if hasattr(self, 'controller_btn'):
            self.controller_btn.setIcon(SVGIconFactory.controller_icon(16, icon_color))
        if hasattr(self, 'settings_btn'):
            self.settings_btn.setIcon(SVGIconFactory.settings_icon(16, icon_color))


        # Sidebar control buttons - FORCE REFRESH
        if hasattr(self, 'vol_up_btn'):
            self.vol_up_btn.setIcon(SVGIconFactory.volume_up_icon(20, icon_color))
            self.vol_up_btn.update()  # Force Qt to redraw
            self.vol_up_btn.repaint()
        if hasattr(self, 'vol_down_btn'):
            self.vol_down_btn.setIcon(SVGIconFactory.volume_down_icon(20, icon_color))
            self.vol_down_btn.update()
            self.vol_down_btn.repaint()
        if hasattr(self, 'screenshot_btn'):
            self.screenshot_btn.setIcon(SVGIconFactory.screenshot_icon(20, icon_color))
            self.screenshot_btn.update()
            self.screenshot_btn.repaint()
        if hasattr(self, 'record_btn'):
            self.record_btn.setIcon(SVGIconFactory.record_icon(20))
            self.record_btn.update()
            self.record_btn.repaint()

        # Bottom panel buttons
        if hasattr(self, 'display_widget'):
            icon_color = self._get_icon_color()
            if hasattr(self.display_widget, 'launch_btn'):
                self.display_widget.launch_btn.setIcon(SVGIconFactory.launch_icon(20, icon_color))
                self.display_widget.launch_btn.repaint()
            if hasattr(self.display_widget, 'load_core_btn'):
                self.display_widget.load_core_btn.setIcon(SVGIconFactory.folder_icon(20, icon_color))
                self.display_widget.load_core_btn.repaint()
            if hasattr(self.display_widget, 'gameart_btn'):
                self.display_widget.gameart_btn.setIcon(SVGIconFactory.paint_icon(20, icon_color))
                self.display_widget.gameart_btn.repaint()
            if hasattr(self.display_widget, 'manage_btn'):
                self.display_widget.manage_btn.setIcon(SVGIconFactory.manage_icon(20, icon_color))
                self.display_widget.manage_btn.repaint()
            if hasattr(self.display_widget, 'ports_btn'):
                self.display_widget.ports_btn.setIcon(SVGIconFactory.package_icon(20, icon_color))
                self.display_widget.ports_btn.repaint()
            if hasattr(self.display_widget, 'stop_btn'):
                self.display_widget.stop_btn.setIcon(SVGIconFactory.stop_icon(20, icon_color))
                self.display_widget.stop_btn.repaint()

    def _open_mel_settings(self): #vers 2
        """Open MEL settings dialog for path configuration"""
        dialog = MELSettingsDialog(self.mel_settings, self)
        if dialog.exec():
            # Settings saved, refresh platforms with new ROM path
            self._refresh_platforms()

            # Reapply icon display mode (lists + ribbons)
            self._set_icon_display_mode(self.mel_settings.get_icon_display_mode())

            # Reapply titlebar colors (in case themed setting changed)
            self._apply_titlebar_colors()

            # Update status
            if hasattr(self, 'status_label'):
                self.status_label.setText("Settings saved - platforms refreshed")

    def _show_settings_dialog(self): #vers 2
        """Show settings dialog with theme and preferences"""
        if not APPSETTINGS_AVAILABLE:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Settings", "AppSettings system not available")
            return

        dialog = SettingsDialog(self.app_settings, self)
        # Connect to _on_theme_changed to get theme name and status updates
        dialog.themeChanged.connect(self._on_theme_changed)

        if dialog.exec():
            # Settings were applied
            self.app_settings.save_settings()
            self._apply_theme()


    def _show_settings_context_menu(self, pos): #vers 1
        """Show context menu for Settings button"""
        from PyQt6.QtWidgets import QMenu

        menu = QMenu(self)

        # Move window action
        move_action = menu.addAction("Move Window")
        move_action.triggered.connect(self._enable_move_mode)

        # Maximize window action
        max_action = menu.addAction("Maximize Window")
        max_action.triggered.connect(self._toggle_maximize)

        # Minimize action
        min_action = menu.addAction("Minimize")
        min_action.triggered.connect(self.showMinimized)

        menu.addSeparator()

        # Upscale Native action
        upscale_action = menu.addAction("Upscale Native")
        upscale_action.setCheckable(True)
        upscale_action.setChecked(False)
        upscale_action.triggered.connect(self._toggle_upscale_native)

        # Shaders action
        shaders_action = menu.addAction("Shaders")
        shaders_action.triggered.connect(self._show_shaders_dialog)

        menu.addSeparator()

        # Icon display mode submenu # TODO icon only system is missing.
        display_menu = menu.addMenu("Platform Display")

        icons_text_action = display_menu.addAction("Icons & Text")
        icons_text_action.setCheckable(True)
        icons_text_action.setChecked(self.icon_display_mode == "icons_and_text")
        icons_text_action.triggered.connect(lambda: self._set_icon_display_mode("icons_and_text"))

        icons_only_action = display_menu.addAction("Icons Only")
        icons_only_action.setCheckable(True)
        icons_only_action.setChecked(self.icon_display_mode == "icons_only")
        icons_only_action.triggered.connect(lambda: self._set_icon_display_mode("icons_only"))

        text_only_action = display_menu.addAction("Text Only")
        text_only_action.setCheckable(True)
        text_only_action.setChecked(self.icon_display_mode == "text_only")
        text_only_action.triggered.connect(lambda: self._set_icon_display_mode("text_only"))

        # Show menu at button position
        menu.exec(self.settings_btn.mapToGlobal(pos))

    def _enable_move_mode(self): #vers 2
        """Enable move window mode using system move"""
        # Use Qt's system move which works on Windows, Linux, etc.
        if hasattr(self.windowHandle(), 'startSystemMove'):
            self.windowHandle().startSystemMove()
        else:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(self, "Move Window",
                "Drag the titlebar to move the window")

    def _toggle_upscale_native(self): #vers 1
        """Toggle upscale native resolution"""
        # Placeholder for upscale native functionality
        print("Upscale Native toggled")

    def _show_shaders_dialog(self): #vers 1
        """Show shaders configuration dialog"""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Shaders",
            "Shader configuration coming soon!\n\nThis will allow you to:\n"
            "- Select shader presets\n"
            "- Configure CRT effects\n"
            "- Adjust visual filters")

    def _show_window_context_menu(self, pos): #vers 1
        """Show context menu for titlebar right-click"""
        from PyQt6.QtWidgets import QMenu


        # Move window action
        move_action = menu.addAction("Move Window")
        move_action.triggered.connect(self._enable_move_mode)

        # Maximize/Restore action
        if self.isMaximized():
            max_action = menu.addAction("Restore Window")
        else:
            max_action = menu.addAction("Maximize Window")
        max_action.triggered.connect(self._toggle_maximize)

        # Minimize action
        min_action = menu.addAction("Minimize")
        min_action.triggered.connect(self.showMinimized)

        menu.addSeparator()

        # Close action
        close_action = menu.addAction("Close")
        close_action.triggered.connect(self.close)

        # Show menu at global position
        menu.exec(self.mapToGlobal(pos))

    def _scan_roms(self): #vers 2
        """Scan for ROMs in configured directory with option to browse"""
        from PyQt6.QtWidgets import QMessageBox, QFileDialog, QProgressDialog
        from pathlib import Path

        # Get ROM path from MEL settings
        roms_dir = self.mel_settings.get_rom_path()

        # Check if path exists
        if not roms_dir.exists():
            response = QMessageBox.question(
                self,
                "ROM Directory Not Found",
                f"ROM directory not found:\n{roms_dir}\n\n"
                "Would you like to select a different directory?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if response == QMessageBox.StandardButton.Yes:
                # Let user browse for ROMs directory
                selected_dir = QFileDialog.getExistingDirectory(
                    self,
                    "Select ROM Directory",
                    str(Path.home()),
                    QFileDialog.Option.ShowDirsOnly
                )

                if selected_dir:
                    roms_dir = Path(selected_dir)
                    # Save this path to settings
                    self.mel_settings.set_rom_path(selected_dir)
                    self.status_label.setText(f"ROM path updated: {selected_dir}")
                else:
                    return
            else:
                return

        # Progress dialog
        progress = QProgressDialog("Scanning for ROMs...", "Cancel", 0, 100, self)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setValue(10)

        # Update scanner with current path
        self.platform_scanner = PlatformScanner(roms_dir)
        progress.setValue(30)

        # Scan platforms
        discovered_platforms = self.platform_scanner.scan_platforms()
        progress.setValue(60)
        
        # Update CoreLauncher with new platform database
        if self.core_launcher and discovered_platforms:
            self.core_launcher.update_database(discovered_platforms)

        if discovered_platforms:
            # Count total ROMs
            total_roms = sum(info['rom_count'] for info in discovered_platforms.values())

            # Refresh platform list
            platform_names = list(discovered_platforms.keys())
            icon_factory = getattr(self, 'platform_icons', None)
            self.platform_list.populate_platforms(platform_names, icon_factory)

            progress.setValue(100)

            # Show results
            result = f"Found {total_roms} ROM(s) across {len(discovered_platforms)} platform(s):\n\n"
            for platform, info in sorted(discovered_platforms.items()):
                result += f"- {platform}: {info['rom_count']} ROM(s)\n"

            self._show_results_tab("Scan Results", result)
            self.status_label.setText(f"Found {len(discovered_platforms)} platform(s) with {total_roms} ROM(s)")
        else:
            progress.setValue(100)

            # Offer to browse for ROMs
            response = QMessageBox.question(
                self,
                "No ROMs Found",
                f"No ROM files found in:\n{roms_dir}\n\n"
                "Would you like to select a different directory?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if response == QMessageBox.StandardButton.Yes:
                # Recursively call to browse
                self._scan_roms()
            else:
                self.status_label.setText("No ROMs found")


    def _show_scan_roms_context_menu(self, position): #vers 1
        """Context menu for Scan ROMs button"""
        from PyQt6.QtWidgets import QMenu

        menu = QMenu(self)

        # Scan current path
        scan_action = menu.addAction("Scan Current ROM Path")
        scan_action.triggered.connect(self._scan_roms)

        # Browse and scan
        browse_action = menu.addAction("Browse for ROM Directory...")
        browse_action.triggered.connect(self._browse_and_scan)

        menu.addSeparator()

        # Open ROM folder
        open_action = menu.addAction("Open ROM Folder")
        open_action.triggered.connect(self._open_rom_folder)

        menu.exec(self.scan_roms_btn.mapToGlobal(position))


    def _browse_and_scan(self): #vers 1
        """Browse for ROM directory and scan"""
        from PyQt6.QtWidgets import QFileDialog
        from pathlib import Path

        selected_dir = QFileDialog.getExistingDirectory(
            self,
            "Select ROM Directory",
            str(self.mel_settings.get_rom_path()),
            QFileDialog.Option.ShowDirsOnly
        )

        if selected_dir:
            self.mel_settings.set_rom_path(selected_dir)
            self._scan_roms()


    def _open_rom_folder(self): #vers 1
        """Open ROM folder in file manager"""
        import subprocess
        import platform
        from pathlib import Path

        roms_dir = self.mel_settings.get_rom_path()

        if not roms_dir.exists():
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Folder Not Found",
                f"ROM folder does not exist:\n{roms_dir}")
            return

        # Open in file manager
        system = platform.system()
        try:
            if system == "Windows":
                subprocess.run(["explorer", str(roms_dir)])
            elif system == "Darwin":  # macOS
                subprocess.run(["open", str(roms_dir)])
            else:  # Linux
                subprocess.run(["xdg-open", str(roms_dir)])
        except Exception as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Error", f"Could not open folder:\n{e}")


    def _show_game_manager(self): #vers 1
        """Show game manager dialog for current platform"""
        if not self.current_platform:
            QMessageBox.warning(
                self,
                "No Platform Selected",
                "Please select a platform first."
            )
            return

        # Get all games for current platform
        if self.current_platform not in self.available_roms:
            QMessageBox.warning(
                self,
                "No Games Found",
                f"No games found for {self.current_platform}"
            )
            return

        # Get game names
        game_names = [rom.stem for rom in self.available_roms[self.current_platform]]

        if not game_names:
            QMessageBox.information(
                self,
                "No Games",
                f"No games found for {self.current_platform}\n\n"
                f"Add ROMs to: roms/{self.current_platform}/"
            )
            return

        # Show manager dialog
        dialog = GameManagerDialog(
            self.current_platform,
            game_names,
            self.core_downloader,
            self.core_launcher,
            self.game_config,
            self
        )

        # Connect signal
        dialog.config_saved.connect(self._on_game_config_saved)

        dialog.exec()

    def _on_game_config_saved(self, platform: str, game_name: str): #vers 1
        """Handle game configuration saved"""
        print(f"Configuration saved for {game_name} on {platform}")

        # Update status
        if hasattr(self, 'status_label'):
            self.status_label.setText(f"Configuration saved for {game_name}")

    def _show_load_core(self): #vers 1
        """Show load core dialog"""
        from apps.gui.load_core_dialog import LoadCoreDialog

        if not self.core_launcher:
            QMessageBox.warning(
                self,
                "Core Launcher Not Available",
                "Core launcher system not initialized."
            )
            return

        cores_dir = self.core_launcher.cores_dir

        dialog = LoadCoreDialog(cores_dir, self)
        dialog.exec()

    def _on_core_loaded(self, core_name: str, core_path: str): #vers 1
        """Handle core loaded from dialog"""
        # Update status
        if hasattr(self, 'status_label'):
            self.status_label.setText(f"Loaded core: {core_name}")

        # You can store this for next launch
        self.preferred_core = core_name

        QMessageBox.information(
            self,
            "Core Loaded",
            f"Core loaded: {core_name}\n\n"
            f"This core will be used for the next game launch.\n"
            f"Or configure it per-game in Game Manager."
        )

    def _save_config(self): #vers 1
            """Save current MEL configuration"""
            from PyQt6.QtWidgets import QMessageBox

            try:
                # Save MEL settings
                self.mel_settings.save_mel_settings()

                # Save hidden platforms list
                if hasattr(self.platform_list, 'hidden_platforms'):
                    hidden_list = list(self.platform_list.hidden_platforms)
                    self.mel_settings.settings['hidden_platforms'] = hidden_list
                    self.mel_settings.save_mel_settings()

                # Save window geometry
                geometry = {
                    'width': self.width(),
                    'height': self.height(),
                    'x': self.x(),
                    'y': self.y()
                }
                self.mel_settings.settings['window_geometry'] = geometry
                self.mel_settings.save_mel_settings()

                QMessageBox.information(self, "Configuration Saved",
                    "All settings have been saved successfully!")

                if hasattr(self, 'status_label'):
                    self.status_label.setText("Configuration saved")

            except Exception as e:
                QMessageBox.critical(self, "Save Failed",
                    f"Failed to save configuration:\n{e}")


    def _setup_controller(self): #vers 1
        """Setup and configure game controller"""
        from PyQt6.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QLabel, QPushButton, QListWidget

        from apps.gui.controller_config_dialog import ControllerConfigDialog
        dialog = ControllerConfigDialog(self.gamepad_config, self)

        if not self.gamepad_config:
            QMessageBox.warning(self, "Controller Setup", "Gamepad config not initialized")
            return

        # Detect controllers
        controllers = self.gamepad_config.detect_controllers()

        if not controllers:
            QMessageBox.information(self, "No Controllers",
                "No controllers detected.\n\nPlease connect a controller and try again.")
            return

        if dialog.exec():
            if hasattr(self, 'status_label'):
                self.status_label.setText("Controller configuration updated")

        # Show controller selection dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Controller Setup")
        dialog.setMinimumWidth(400)
        dialog.setMinimumHeight(300)

        layout = QVBoxLayout(dialog)

        info_label = QLabel(f"Detected {len(controllers)} controller(s):")
        layout.addWidget(info_label)

        # List controllers
        controller_list = QListWidget()
        for ctrl in controllers:
            item_text = f"{ctrl['name']} - {ctrl['buttons']} buttons, {ctrl['axes']} axes"
            controller_list.addItem(item_text)
        layout.addWidget(controller_list)

        # Test button
        test_btn = QPushButton("Test Selected Controller")
        test_btn.clicked.connect(lambda: self._test_selected_controller(controller_list.currentRow()))
        layout.addWidget(test_btn)

        # Save button
        save_btn = QPushButton("Save Configuration")
        save_btn.clicked.connect(lambda: self._save_controller_config(controller_list.currentRow()))
        layout.addWidget(save_btn)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)

        dialog.exec()


    def _show_about_dialog(self): #vers 1
        """Show about/info dialog"""
        from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTabWidget, QWidget, QGroupBox, QFormLayout, QSpinBox, QComboBox, QSlider, QLabel, QCheckBox, QFontComboBox)
        from PyQt6.QtCore import Qt
        from PyQt6.QtGui import QFont

        dialog = QDialog(self)
        dialog.setWindowTitle("About Multi-Emulator Launcher")
        dialog.setMinimumSize(600, 500)

        layout = QVBoxLayout()

        # Title
        title = QLabel("Multi-Emulator Launcher 1.0")
        title_font = QFont(self.title_font)
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Author info
        author = QLabel("Created by X-Seti")
        author.setAlignment(Qt.AlignmentFlag.AlignCenter)
        author_font = QFont(self.panel_font)
        author_font.setPointSize(12)
        author.setFont(author_font)
        layout.addWidget(author)

        # Year
        year = QLabel("Â© 2025")
        year.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(year)

        layout.addSpacing(20)

        # Info browser
        info_browser = QTextBrowser()
        info_browser.setOpenExternalLinks(True)

        info_html = """
        <h3>About This Tool</h3>
        <p>Multi-Emulator Launcher (MEL) is a comprehensive emulation management system
        that provides a unified interface for launching games across multiple retro gaming platforms.</p>

        <h3>Key Features</h3>
        <ul>
            <li><b>Multi-Platform Support</b> - Support for 20+ gaming systems including:
                <ul>
                    <li>Commodore Amiga, Atari ST, Amstrad CPC</li>
                    <li>PlayStation 1/2/3, Nintendo 64, SNES, Genesis</li>
                    <li>Game Boy Advance, PSP, Dreamcast, and more</li>
                </ul>
            </li>
            <li><b>Dynamic Platform Discovery</b> - Automatically detects platforms from ROM directory structure</li>
            <li><b>Custom Emulator Launching</b> - Direct core launching without RetroArch dependency</li>
            <li><b>ROM Management</b> - Intelligent scanning, ZIP support, multi-disk game handling</li>
            <li><b>BIOS Management</b> - Organized BIOS file structure matching platforms</li>
            <li><b>Controller Support</b> - Full gamepad configuration with per-platform overrides</li>
            <li><b>Customizable Interface</b>
                <ul>
                    <li>Multiple display modes: Icons & Text, Icons Only, Text Only</li>
                    <li>Theme system with light/dark modes</li>
                    <li>SVG-based platform icons</li>
                    <li>Frameless window with custom controls</li>
                </ul>
            </li>
            <li><b>Platform Organization</b>
                <ul>
                    <li>Hide/show individual platforms</li>
                    <li>Right-click context menus</li>
                    <li>Platform-specific controller configuration</li>
                </ul>
            </li>
            <li><b>Configuration Management</b>
                <ul>
                    <li>Save/load complete settings</li>
                    <li>Persistent hidden platforms list</li>
                    <li>Window geometry memory</li>
                    <li>Icon display preferences</li>
                </ul>
            </li>
        </ul>

        <h3>Technical Details</h3>
        <ul>
            <li><b>Framework:</b> PyQt6</li>
            <li><b>Architecture:</b> Modular design with separated concerns</li>
            <li><b>Graphics:</b> SVG-based scalable icons</li>
            <li><b>Theme Engine:</b> App-System-Settings integration</li>
            <li><b>Platform:</b> Cross-platform (Linux, Windows, macOS)</li>
        </ul>

        <h3>Project Structure</h3>
        <ul>
            <li><b>core/</b> - Core functionality (launchers, downloaders, configs)</li>
            <li><b>gui/</b> - GUI components and dialogs</li>
            <li><b>methods/</b> - Shared utility methods</li>
            <li><b>components/</b> - Reusable UI components</li>
            <li><b>utils/</b> - Settings and theme management</li>
            <li><b>themes/</b> - Theme JSON files</li>
        </ul>

        <h3>GitHub Repository</h3>
        <p><a href="https://github.com/X-Seti/Multi-Emulator-Launcher">
        https://github.com/X-Seti/Multi-Emulator-Launcher</a></p>

        <h3>License</h3>
        <p>This project follows clean code conventions with strict organizational rules:</p>
        <ul>
            <li>File headers with "X-Seti - [Date] 2025" format</li>
            <li>Alphabetical method listings with version tracking</li>
            <li>No "Enhanced/Fixed/Improved" naming patterns</li>
            <li>Organized folder structure</li>
            <li>SVG icons only (no emojis)</li>
        </ul>

        <br>
        <p><i>Built with attention to detail and commitment to quality code.</i></p>
        """

        info_browser.setHtml(info_html)
        layout.addWidget(info_browser)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)

        dialog.setLayout(layout)

        dialog.exec()


    def _test_selected_controller(self, controller_id): #vers 1
        """Test controller input"""
        from PyQt6.QtWidgets import QMessageBox

        if controller_id < 0:
            QMessageBox.warning(self, "Test Controller", "Please select a controller first")
            return

        QMessageBox.information(self, "Test Controller",
            f"Testing controller {controller_id}...\n\n"
            "Press buttons and move sticks.\n"
            "Check terminal for output.\n\n"
            "Test will run for 10 seconds...")

        if self.gamepad_config:
            inputs = self.gamepad_config.test_controller_input(controller_id, 10)

            if inputs:
                result = "Detected inputs:\n\n"
                for key, value in list(inputs.items())[:10]:  # Show first 10
                    result += f"{key}: {value}\n"
                QMessageBox.information(self, "Test Results", result)
            else:
                QMessageBox.information(self, "Test Results", "No inputs detected")


    def _save_controller_config(self, controller_id): #vers 1
        """Save controller configuration"""
        from PyQt6.QtWidgets import QMessageBox

        if controller_id < 0:
            QMessageBox.warning(self, "Save Config", "Please select a controller first")
            return

        # Get controller info
        ctrl_info = self.gamepad_config.get_controller_info(controller_id)

        if ctrl_info:
            # Save configuration
            success = self.gamepad_config.save_config(controller_id, ctrl_info)

            if success:
                QMessageBox.information(self, "Configuration Saved",
                    f"Controller {controller_id} configuration saved successfully!")
            else:
                QMessageBox.warning(self, "Save Failed", "Failed to save controller configuration")
        else:
            QMessageBox.warning(self, "Save Failed", "Controller information not available")

# - Settings Reusable
    def _apply_window_flags(self): #vers 2
        """Apply window flags based on settings"""
        # Save current geometry
        current_geometry = self.geometry()
        was_visible = self.isVisible()

        if self.use_system_titlebar:
            # Use system window with title bar
            self.setWindowFlags(
                Qt.WindowType.Window |
                Qt.WindowType.WindowMinimizeButtonHint |
                Qt.WindowType.WindowMaximizeButtonHint |
                Qt.WindowType.WindowCloseButtonHint
            )
        else:
            # FIXED: Custom frameless window - must include Window flag
            self.setWindowFlags(
                Qt.WindowType.Window |  # Enables proper window manager integration
                Qt.WindowType.FramelessWindowHint  # Removes decorations
            )

        # Restore geometry and visibility
        self.setGeometry(current_geometry)

        if was_visible:
            self.show()

        if self.main_window and hasattr(self.main_window, 'log_message'):
            mode = "System title bar" if self.use_system_titlebar else "Custom frameless"
            self.main_window.log_message(f"Window mode: {mode}")


    def _apply_always_on_top(self): #vers 1
        """Apply always on top window flag"""
        current_flags = self.windowFlags()

        if self.window_always_on_top:
            new_flags = current_flags | Qt.WindowType.WindowStaysOnTopHint
        else:
            new_flags = current_flags & ~Qt.WindowType.WindowStaysOnTopHint

        if new_flags != current_flags:
            # Save state
            current_geometry = self.geometry()
            was_visible = self.isVisible()

            self.setWindowFlags(new_flags)

            self.setGeometry(current_geometry)
            if was_visible:
                self.show()


    def _scan_available_locales(self): #vers 2
        """Scan locale folder and return list of available languages"""
        import os
        import configparser

        locales = []
        locale_path = os.path.join(os.path.dirname(__file__), 'locale')

        if not os.path.exists(locale_path):
            # Easter egg: Amiga Workbench 3.1 style error
            self._show_amiga_locale_error()
            # Return default English
            return [("English", "en", None)]

        try:
            for filename in os.listdir(locale_path):
                if filename.endswith('.lang'):
                    filepath = os.path.join(locale_path, filename)

                    try:
                        config = configparser.ConfigParser()
                        config.read(filepath, encoding='utf-8')

                        if 'Metadata' in config:
                            lang_name = config['Metadata'].get('LanguageName', 'Unknown')
                            lang_code = config['Metadata'].get('LanguageCode', 'unknown')
                            locales.append((lang_name, lang_code, filepath))

                    except Exception as e:
                        if self.main_window and hasattr(self.main_window, 'log_message'):
                            self.main_window.log_message(f"Failed to load locale {filename}: {e}")

        except Exception as e:
            if self.main_window and hasattr(self.main_window, 'log_message'):
                self.main_window.log_message(f"Locale scan error: {e}")

        locales.sort(key=lambda x: x[0])

        if not locales:
            locales = [("English", "en", None)]

        return locales


    def _show_amiga_locale_error(self): #vers 1
        """Show Amiga Workbench 3.1 style error dialog"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
        from PyQt6.QtCore import Qt
        from PyQt6.QtGui import QFont

        dialog = QDialog(self)
        dialog.setWindowTitle("Workbench Request")
        dialog.setFixedSize(450, 150)

        # Amiga Workbench styling
        dialog.setStyleSheet("""
            QDialog {
                background-color: #aaaaaa;
                border: 2px solid #ffffff;
            }
            QLabel {
                color: #000000;
                background-color: #aaaaaa;
            }
            QPushButton {
                background-color: #8899aa;
                color: #000000;
                border: 2px outset #ffffff;
                padding: 5px 15px;
                min-width: 80px;
            }
            QPushButton:pressed {
                border: 2px inset #555555;
            }
        """)

        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Amiga Topaz font style
        amiga_font = QFont("Courier", 10, QFont.Weight.Normal)

        # Error message
        message = QLabel("Workbench 3.1 installer\n\nPlease insert Local disk in any drive")
        message.setFont(amiga_font)
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(message)

        layout.addStretch()

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        # Retry and Cancel buttons (Amiga style)
        retry_btn = QPushButton("Retry")
        retry_btn.setFont(amiga_font)
        retry_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(retry_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFont(amiga_font)
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        dialog.exec()


    def _apply_button_mode(self, dialog): #vers 1
        """Apply button display mode"""
        mode_index = self.button_mode_combo.currentIndex()
        mode_map = {0: 'both', 1: 'icons', 2: 'text'}

        new_mode = mode_map[mode_index]

        if new_mode != self.button_display_mode:
            self.button_display_mode = new_mode
            self._update_all_buttons()

            if self.main_window and hasattr(self.main_window, 'log_message'):
                mode_names = {0: 'Icons + Text', 1: 'Icons Only', 2: 'Text Only'}
                self.main_window.log_message(f"Button style: {mode_names[mode_index]}")

        dialog.close()

# - Window functionality

    def _initialize_features(self): #vers 4
        """Initialize all features after UI setup"""
        try:
            self._apply_theme()
            self.log_message("All features initialized")

        except Exception as e:
            self.log_message(f"Feature init error: {str(e)}")


    def _is_on_draggable_area(self, pos): #vers 7
        """Check if position is on draggable titlebar area

        Args:
            pos: Position in titlebar coordinates (from eventFilter)

        Returns:
            True if position is on titlebar but not on any button
        """
        if not hasattr(self, 'titlebar'):
            print("[DRAG] No titlebar attribute")
            return False

        # Verify pos is within titlebar bounds
        if not self.titlebar.rect().contains(pos):
            print(f"[DRAG] Position {pos} outside titlebar rect {self.titlebar.rect()}")
            return False

        # Check if clicking on any button - if so, NOT draggable
        for widget in self.titlebar.findChildren(QPushButton):
            if widget.isVisible():
                # Get button geometry in titlebar coordinates
                button_rect = widget.geometry()
                if button_rect.contains(pos):
                    print(f"[DRAG] Clicked on button: {widget.toolTip()}")
                    return False

        # Not on any button = draggable
        print(f"[DRAG] On draggable area at {pos}")
        return True


    def _update_all_buttons(self): #vers 4
        """Update all buttons to match display mode"""
        buttons_to_update = [
            # Toolbar buttons
            ('open_btn', 'Open'),
            ('save_btn', 'Save'),
        ]

    def paintEvent(self, event): #vers 2
        """Paint corner resize triangles"""
        super().paintEvent(event)
        from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QPainterPath

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Corner indicator colours from the theme, or the widget palette
        theme_colors = self._get_theme_colors("default")
        palette = self.palette()
        if theme_colors:
            accent_color = QColor(theme_colors['accent_primary'])
            normal_color = QColor(theme_colors['border'])
            hover_color = QColor(theme_colors['button_hover'])
        else:
            accent_color = palette.color(QPalette.ColorRole.Highlight)
            normal_color = palette.color(QPalette.ColorRole.Mid)
            hover_color = palette.color(QPalette.ColorRole.Light)

        accent_color.setAlpha(180)
        normal_color.setAlpha(150)
        hover_color.setAlpha(200)

        w = self.width()
        h = self.height()
        grip_size = 8  # Make corners visible (8x8px)
        size = self.corner_size

        # Define corner triangles
        corners = {
            "top-left": [(0, grip_size), (0, 0), (grip_size, 0)],
            "top-right": [(w-grip_size, 0), (w, 0), (w, grip_size)],
            "bottom-left": [(0, h-grip_size), (0, h), (grip_size, h)],
            "bottom-right": [(w-grip_size, h), (w, h), (w, h-grip_size)]
        }

        # Draw all corners with hover effect
        for corner_name, points in corners.items():
            path = QPainterPath()
            path.moveTo(points[0][0], points[0][1])
            path.lineTo(points[1][0], points[1][1])
            path.lineTo(points[2][0], points[2][1])
            path.closeSubpath()

            # Use hover color if mouse is over this corner
            color = hover_color if self.hover_corner == corner_name else accent_color

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(color))
            painter.drawPath(path)

        painter.end()

    def _get_resize_corner(self, pos): #vers 2
        """Determine which corner is under mouse position"""
        size = self.corner_size
        w = self.width()
        h = self.height()

        if pos.x() < size and pos.y() < size:
            return "top-left"

        if pos.x() > w - size and pos.y() < size:
            return "top-right"

        if pos.x() < size and pos.y() > h - size:
            return "bottom-left"

        if pos.x() > w - size and pos.y() > h - size:
            return "bottom-right"

        return None


    # KEEP ONLY mousePressEvent with this logic:
    def mousePressEvent(self, event): #vers 7
        """Handle ALL mouse press - dragging and resizing"""
        if event.button() != Qt.MouseButton.LeftButton:
            super().mousePressEvent(event)
            return

        pos = event.pos()

        # Check corner resize FIRST
        self.resize_corner = self._get_resize_corner(pos)
        if self.resize_corner:
            self.resizing = True
            self.drag_position = event.globalPosition().toPoint()
            self.initial_geometry = self.geometry()
            event.accept()
            return

        # Check if on titlebar
        if hasattr(self, 'titlebar') and self.titlebar.geometry().contains(pos):
            titlebar_pos = self.titlebar.mapFromParent(pos)
            if self._is_on_draggable_area(titlebar_pos):
                self.windowHandle().startSystemMove()
                event.accept()
                return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event): #vers 4
        """Handle mouse move for resizing and hover effects

        Window dragging is handled by eventFilter to avoid conflicts
        """
        if event.buttons() == Qt.MouseButton.LeftButton:
            if self.resizing and self.resize_corner:
                self._handle_corner_resize(event.globalPosition().toPoint())
                event.accept()
                return
        else:
            # Update hover state and cursor
            corner = self._get_resize_corner(event.pos())
            if corner != self.hover_corner:
                self.hover_corner = corner
                self.update()  # Trigger repaint for hover effect
            self._update_cursor(corner)

        # Let parent handle everything else
        super().mouseMoveEvent(event)


    def mouseReleaseEvent(self, event): #vers 4
        """Handle mouse release for resizing only

        Window dragging is handled by eventFilter to avoid conflicts
        """
        if event.button() == Qt.MouseButton.LeftButton:
            if self.resizing:
                print(f"[RESIZE] Ended at: {self.geometry()}")
            self.resizing = False
            self.resize_corner = None
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
            return

        # Let parent handle everything else
        super().mouseReleaseEvent(event)


    def mouseDoubleClickEvent(self, event): #vers 2
        """Handle double-click - maximize/restore

        Handled here instead of eventFilter for better control
        """
        if event.button() == Qt.MouseButton.LeftButton:
            # Convert to titlebar coordinates if needed
            if hasattr(self, 'titlebar'):
                titlebar_pos = self.titlebar.mapFromParent(event.pos())
                if self._is_on_draggable_area(titlebar_pos):
                    self._toggle_maximize()
                    event.accept()
                    return

        super().mouseDoubleClickEvent(event)


    def resizeEvent(self, event): #vers 1
        '''Keep resize grip in bottom-right corner'''
        super().resizeEvent(event)
        if hasattr(self, 'size_grip'):
            self.size_grip.move(self.width() - 16, self.height() - 16)


    def _handle_corner_resize(self, global_pos): #vers 2
        """Handle window resizing from corners"""
        if not self.resize_corner or not self.drag_position:
            return

        delta = global_pos - self.drag_position
        geometry = self.initial_geometry

        min_width = 800
        min_height = 600

        # Calculate new geometry based on corner
        if self.resize_corner == "top-left":
            new_x = geometry.x() + delta.x()
            new_y = geometry.y() + delta.y()
            new_width = geometry.width() - delta.x()
            new_height = geometry.height() - delta.y()

            if new_width >= min_width and new_height >= min_height:
                self.setGeometry(new_x, new_y, new_width, new_height)

        elif self.resize_corner == "top-right":
            new_y = geometry.y() + delta.y()
            new_width = geometry.width() + delta.x()
            new_height = geometry.height() - delta.y()

            if new_width >= min_width and new_height >= min_height:
                self.setGeometry(geometry.x(), new_y, new_width, new_height)

        elif self.resize_corner == "bottom-left":
            new_x = geometry.x() + delta.x()
            new_width = geometry.width() - delta.x()
            new_height = geometry.height() + delta.y()

            if new_width >= min_width and new_height >= min_height:
                self.setGeometry(new_x, geometry.y(), new_width, new_height)

        elif self.resize_corner == "bottom-right":
            new_width = geometry.width() + delta.x()
            new_height = geometry.height() + delta.y()

            if new_width >= min_width and new_height >= min_height:
                self.resize(new_width, new_height)


    def _update_cursor(self, direction): #vers 1
        """Update cursor based on resize direction"""
        if direction == "top" or direction == "bottom":
            self.setCursor(Qt.CursorShape.SizeVerCursor)
        elif direction == "left" or direction == "right":
            self.setCursor(Qt.CursorShape.SizeHorCursor)
        elif direction == "top-left" or direction == "bottom-right":
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif direction == "top-right" or direction == "bottom-left":
            self.setCursor(Qt.CursorShape.SizeBDiagCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)


    def _toggle_maximize(self): #vers 1
        """Toggle window maximize state"""
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def closeEvent(self, event): #vers 2
        """Handle close event"""
        self.ribbon_save_state()
        self.window_closed.emit()
        event.accept()

# - RIBBONS -- Section.

    def _build_ribbons(self): #vers 1
        """Declare the ribbons and their buttons"""
        tb_platforms = self.ribbon_toolbar("Platforms")
        self.ribbon_button(tb_platforms, "refresh_icon",
                           "Rescan platforms and games", self._refresh_platforms,
                           text="Rescan")
        self.ribbon_button(tb_platforms, "manage_icon",
                           "Cycle icon display mode", self._toggle_icon_display_mode,
                           text="Icon Style")
        self.ribbon_button(tb_platforms, "search_icon",
                           "Detect installed emulators", self._show_detection_results,
                           text="Detect")
        tb_platforms.addSeparator()
        self.ribbon_button(tb_platforms, "folder_icon", "Scan for ROM files",
                           self._scan_roms, text="Scan ROMs")
        self.ribbon_button(tb_platforms, "chip_icon",
                           "Scan and manage system BIOS files", self._show_bios_manager,
                           text="Scan BIOS")
        self.ribbon_button(tb_platforms, "database_icon",
                           "BIOS and core database manager", self._show_database_manager,
                           text="Database")
        self.ribbon_button(tb_platforms, "file_icon", "Reopen the last scan results",
                           self._reopen_last_results, text="Results")

        tb_games = self.ribbon_toolbar("Games")
        self.ribbon_button(tb_games, "launch_icon",
                           "Launch selected game", self._on_launch_game, text="Launch")
        self.ribbon_button(tb_games, "stop_icon",
                           "Stop emulation", self._on_stop_emulation, text="Stop")
        tb_games.addSeparator()
        self.ribbon_button(tb_games, "manage_icon", "Game manager",
                           self._show_game_manager, text="Games")
        self.ribbon_button(tb_games, "package_icon", "Ports manager",
                           self._show_ports_manager, text="Ports")
        self.ribbon_button(tb_games, "save_icon", "Save configuration",
                           self._save_config, text="Save Config")

        tb_view = self.ribbon_toolbar("View", new_row=True)
        self.ribbon_button(tb_view, lambda size, color: self._create_embed_icon(color),
                           "Embedded window mode",
                           lambda: self._set_display_mode('embedded'), text="Embed")
        self.ribbon_button(tb_view, lambda size, color: self._create_popout_icon(color),
                           "Pop-out to resizable window",
                           lambda: self._set_display_mode('popout'), text="Pop-out")
        self.ribbon_button(tb_view, lambda size, color: self._create_fullscreen_icon(color),
                           "Fullscreen mode",
                           lambda: self._set_display_mode('fullscreen'), text="Fullscreen")

        tb_tools = self.ribbon_toolbar("Tools")
        self.ribbon_button(tb_tools, "manage_icon", "Arrange ribbons and choose icons",
                           self.open_ribbon_manager, text="Ribbons")
        self.ribbon_button(tb_tools, "settings_icon", "Multi-Emulator Launcher settings",
                           self._open_mel_settings, text="Settings")
        self.ribbon_button(tb_tools, "properties_icon", "Theme and preferences",
                           self._show_settings_dialog, text="Theme")
        self.ribbon_button(tb_tools, "controller_icon", "Configure game controller",
                           self._setup_controller, text="Controller")
        self.ribbon_button(tb_tools, "info_icon", "About Multi-Emulator Launcher",
                           self._show_about_dialog, text="About")

    def _build_full_menu(self, parent_menu): #vers 1
        """File menu, then one sub-menu per ribbon"""
        fm = parent_menu.addMenu("File")
        fm.addAction("Settings...", self._open_mel_settings)
        fm.addAction("Theme Settings...", self._show_settings_dialog)
        fm.addSeparator()
        fm.addAction("Scan ROMs", self._scan_roms)
        fm.addAction("Rescan Platforms", self._refresh_platforms)
        fm.addAction("Save Configuration", self._save_config)
        fm.addSeparator()
        fm.addAction("About...", self._show_about_dialog)
        fm.addAction("Quit", self.close)

        for tb in self.ribbon_toolbars():
            entries = list(tb.actions())
            if not any(not a.isSeparator() for a in entries):
                continue
            sub = parent_menu.addMenu(tb.windowTitle() or tb.objectName())
            for act in entries:
                if act.isSeparator():
                    sub.addSeparator()
                elif act.isVisible():
                    sub.addAction(act)

        parent_menu.addSeparator()
        parent_menu.addAction("Ribbon Manager...", self.open_ribbon_manager)
        parent_menu.addAction("Save Ribbon Config", self.ribbon_save_state)

    def _apply_ribbon_theme(self): #vers 3
        """Style ribbons and re-render their icons from the theme"""
        mw = getattr(self, '_ribbon_mw', None)
        if mw is None:
            return
        colors = self._get_theme_colors("default")
        if not colors:
            return
        border = colors['border']
        text = colors['button_text_color']
        hover = colors['button_hover']
        pressed = colors['button_pressed']
        mw.setStyleSheet(f"""
            QToolBar QToolButton {{
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 3px;
                padding: 3px;
                color: {text};
            }}
            QToolBar QToolButton:hover {{
                background-color: {hover};
                border: 1px solid {border};
            }}
            QToolBar QToolButton:pressed, QToolBar QToolButton:checked {{
                background-color: {pressed};
                border: 1px solid {border};
            }}
            QToolBar::separator {{
                background-color: {border};
                width: 1px;
                margin: 4px 3px;
            }}
        """)
        self._render_ribbon_icons()
        self._apply_custom_icon_images()

# - SVG ICONS -- Section.
    def _create_theme_aware_icon(self, svg_data, size=20): #vers 4
        """Create theme-aware SVG icon that adapts to light/dark themes

        Args:
            svg_data: SVG data as bytes with 'currentColor' placeholder
            size: Icon size in pixels

        Returns:
            QIcon with proper theme colors
        """
        from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor
        from PyQt6.QtSvg import QSvgRenderer
        from PyQt6.QtCore import QByteArray

        try:
            # Icon colour is the theme's text colour
            theme_colors = self._get_theme_colors("default")
            icon_color = theme_colors['text_primary']
            # Replace currentColor with actual color
            svg_str = svg_data.decode('utf-8')
            svg_str = svg_str.replace('currentColor', icon_color)
            svg_data_colored = svg_str.encode('utf-8')

            # Render SVG
            renderer = QSvgRenderer(QByteArray(svg_data_colored))
            if not renderer.isValid():
                return QIcon()

            pixmap = QPixmap(size, size)
            pixmap.fill(Qt.GlobalColor.transparent)

            painter = QPainter(pixmap)
            renderer.render(painter)
            painter.end()

            return QIcon(pixmap)

        except Exception as e:
            print(f"Error creating theme-aware icon: {e}")
            return QIcon()


    def _show_database_manager(self): #vers 1
        """Show database manager dialog for managing ROMs, BIOS, and paths"""
        try:
            from PyQt6.QtWidgets import QMessageBox
            
            dialog = DatabaseManagerDialog(self.database_manager, self)
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Database Manager Error",
                f"Failed to open database manager:\n{str(e)}"
            )


# Standalone execution
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EmuLauncherGUI()
    window.show()
    sys.exit(app.exec())
