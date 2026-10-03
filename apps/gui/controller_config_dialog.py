#!/usr/bin/env python3
#this belongs in apps/gui/controller_config_dialog.py - Version: 2
# X-Seti - November27 2025 - Multi-Emulator Launcher - Controller Config Dialog

"""
Controller Configuration Dialog
- Global controller button mapping
- Per-platform controller overrides
- Visual layout viewer with real-time input
- Save/load controller profiles
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QGroupBox, QListWidget, QListWidgetItem,
                             QTabWidget, QWidget, QComboBox, QMessageBox)
from PyQt6.QtCore import Qt
from pathlib import Path
import json

##Methods list -
# __init__
# _create_button_mapping_row
# _create_global_tab
# _create_layout_tab
# _create_platform_tab
# _detect_controller
# _get_settings
# _on_platform_selected
# _remap_button
# _save_settings
# _setup_ui

class ControllerConfigDialog(QDialog): #vers 2
    """Controller configuration dialog with visual layout viewer"""
    
    # Standard controller buttons
    CONTROLLER_BUTTONS = [
        "A / Cross",
        "B / Circle", 
        "X / Square",
        "Y / Triangle",
        "L1 / LB",
        "R1 / RB",
        "L2 / LT",
        "R2 / RT",
        "L3 / LS",
        "R3 / RS",
        "D-Pad Up",
        "D-Pad Down",
        "D-Pad Left",
        "D-Pad Right",
        "Start",
        "Select / Back",
        "Guide / Home"
    ]
    
    # Emulator actions
    EMULATOR_ACTIONS = [
        "Not Mapped",
        "Accept / Confirm",
        "Cancel / Back",
        "Menu",
        "Fast Forward",
        "Rewind",
        "Save State",
        "Load State",
        "Screenshot",
        "Pause",
        "Reset",
        "Quit Emulator",
        "Next State Slot",
        "Previous State Slot",
        "Toggle Fullscreen",
        "Toggle FPS Display"
    ]
    
    def __init__(self, gamepad_config, parent=None): #vers 2
        """Initialize controller config dialog
        
        Args:
            gamepad_config: GamepadConfig instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.gamepad_config = gamepad_config
        self.setWindowTitle("Controller Configuration")
        self.setMinimumSize(900, 600)
        self.setModal(True)
        
        # Controller mappings
        self.global_mapping = {}
        self.platform_mappings = {}
        
        # Button combo boxes (for global tab)
        self.global_button_combos = {}
        
        # Platform combo boxes (for platform tab)
        self.platform_button_combos = {}
        
        self._setup_ui()
        self._get_settings()
    
    def _setup_ui(self): #vers 2
        """Setup dialog UI with three tabs"""
        layout = QVBoxLayout(self)
        
        # Tab widget
        tabs = QTabWidget()
        tabs.addTab(self._create_global_tab(), "Global Mapping")
        tabs.addTab(self._create_platform_tab(), "Platform Overrides")
        tabs.addTab(self._create_layout_tab(), "Visual Layout")
        layout.addWidget(tabs)
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self._save_settings)
        save_btn.setDefault(True)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def _create_global_tab(self): #vers 1
        """Create global controller mapping tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Controller detection
        detect_group = QGroupBox("Connected Controller")
        detect_layout = QHBoxLayout()
        
        self.controller_label = QLabel("No controller detected")
        detect_layout.addWidget(self.controller_label)
        
        detect_btn = QPushButton("Detect Controller")
        detect_btn.clicked.connect(self._detect_controller)
        detect_layout.addWidget(detect_btn)
        
        detect_group.setLayout(detect_layout)
        layout.addWidget(detect_group)
        
        # Global button mappings
        mapping_group = QGroupBox("Global Button Mapping")
        mapping_layout = QVBoxLayout()
        
        for button in self.CONTROLLER_BUTTONS:
            combo = self._create_button_mapping_row(button, mapping_layout)
            self.global_button_combos[button] = combo
        
        mapping_layout.addStretch()
        mapping_group.setLayout(mapping_layout)
        layout.addWidget(mapping_group)
        
        return tab
    
    def _create_platform_tab(self): #vers 1
        """Create platform-specific override tab"""
        tab = QWidget()
        layout = QHBoxLayout(tab)
        
        # Platform list
        platform_group = QGroupBox("Platform")
        platform_layout = QVBoxLayout()
        
        self.platform_list = QListWidget()
        self.platform_list.addItems([
            "PlayStation", "PlayStation 2", "PSP",
            "Nintendo 64", "GameCube", "Wii",
            "SNES", "Genesis", "Game Boy Advance",
            "Amiga", "Atari ST", "C64"
        ])
        self.platform_list.currentItemChanged.connect(self._on_platform_selected)
        platform_layout.addWidget(self.platform_list)
        
        platform_group.setLayout(platform_layout)
        layout.addWidget(platform_group, 1)
        
        # Platform-specific mappings
        mapping_group = QGroupBox("Platform Override Mapping")
        mapping_layout = QVBoxLayout()
        
        info_label = QLabel("Select a platform to configure platform-specific button mappings.\nLeave as 'Not Mapped' to use global mapping.")
        info_label.setWordWrap(True)
        mapping_layout.addWidget(info_label)
        
        use_global_btn = QPushButton("Reset to Global Mapping")
        mapping_layout.addWidget(use_global_btn)
        
        mapping_layout.addSpacing(10)
        
        # Show first 8 buttons for platform overrides
        self.platform_button_combos = {}
        for button in self.CONTROLLER_BUTTONS[:8]:
            combo = self._create_button_mapping_row(button, mapping_layout)
            self.platform_button_combos[button] = combo
        
        mapping_layout.addStretch()
        mapping_group.setLayout(mapping_layout)
        layout.addWidget(mapping_group, 2)
        
        return tab
    
    def _create_layout_tab(self): #vers 1
        """Create visual layout tab with controller viewer"""
        from apps.gui.controller_layout_viewer import ControllerLayoutViewer
        
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Info label
        info_label = QLabel("Visual controller layout with real-time button detection")
        info_label.setStyleSheet("padding: 10px; font-weight: bold;")
        layout.addWidget(info_label)
        
        # Add controller viewer widget
        self.layout_viewer = ControllerLayoutViewer(self.gamepad_config, self)
        layout.addWidget(self.layout_viewer)
        
        return tab
    
    def _create_button_mapping_row(self, button_name, parent_layout): #vers 1
        """Create a button mapping row
        
        Args:
            button_name: Name of the button
            parent_layout: Layout to add the row to
            
        Returns:
            QComboBox for the action selection
        """
        row = QHBoxLayout()
        
        # Button label
        label = QLabel(button_name)
        label.setMinimumWidth(150)
        row.addWidget(label)
        
        # Action dropdown
        action_combo = QComboBox()
        action_combo.addItems(self.EMULATOR_ACTIONS)
        row.addWidget(action_combo)
        
        # Remap button
        remap_btn = QPushButton("Remap")
        remap_btn.setMaximumWidth(80)
        remap_btn.clicked.connect(lambda: self._remap_button(button_name, action_combo))
        row.addWidget(remap_btn)
        
        parent_layout.addLayout(row)
        
        return action_combo
    
    def _detect_controller(self): #vers 1
        """Detect connected controller"""
        if self.gamepad_config:
            controllers = self.gamepad_config.detect_controllers()
            if controllers:
                ctrl = controllers[0]
                self.controller_label.setText(
                    f"Controller: {ctrl['name']} ({ctrl['buttons']} buttons, {ctrl['axes']} axes)"
                )
            else:
                self.controller_label.setText("No controller detected")
                QMessageBox.information(self, "No Controller", 
                    "No controller detected. Please connect a controller and try again.")
    
    def _get_settings(self): #vers 1
        """Load current controller settings"""
        # Load from gamepad_config if available
        if self.gamepad_config:
            # TODO: Load mappings from gamepad_config
            pass
        
        # Set default mappings
        if "A / Cross" in self.global_button_combos:
            self.global_button_combos["A / Cross"].setCurrentText("Accept / Confirm")
        if "B / Circle" in self.global_button_combos:
            self.global_button_combos["B / Circle"].setCurrentText("Cancel / Back")
        if "Start" in self.global_button_combos:
            self.global_button_combos["Start"].setCurrentText("Menu")
        if "Select / Back" in self.global_button_combos:
            self.global_button_combos["Select / Back"].setCurrentText("Pause")
    
    def _on_platform_selected(self, current, previous): #vers 1
        """Handle platform selection for override mapping
        
        Args:
            current: Current QListWidgetItem
            previous: Previous QListWidgetItem
        """
        if current:
            platform = current.text()
            # Load platform-specific mappings if they exist
            if platform in self.platform_mappings:
                for button, action in self.platform_mappings[platform].items():
                    if button in self.platform_button_combos:
                        self.platform_button_combos[button].setCurrentText(action)
    
    def _remap_button(self, button_name, action_combo): #vers 1
        """Remap a button by detecting controller input
        
        Args:
            button_name: Name of button to remap
            action_combo: QComboBox to update with new mapping
        """
        QMessageBox.information(self, "Remap Button",
            f"Press the button you want to map to '{button_name}'...\n\n"
            "(This feature requires controller input detection)\n\n"
            "For now, use the dropdown to select an action.")
        # TODO: Implement actual button detection with pygame
    
    def _save_settings(self): #vers 1
        """Save controller configuration"""
        # Build global mapping dict
        self.global_mapping = {}
        for button, combo in self.global_button_combos.items():
            self.global_mapping[button] = combo.currentText()
        
        # Build platform mappings dict
        if hasattr(self, 'platform_list') and self.platform_list.currentItem():
            current_platform = self.platform_list.currentItem().text()
            platform_mapping = {}
            for button, combo in self.platform_button_combos.items():
                action = combo.currentText()
                if action != "Not Mapped":
                    platform_mapping[button] = action
            
            if platform_mapping:
                self.platform_mappings[current_platform] = platform_mapping
        
        # Save to file
        try:
            config_file = Path("config/controller_config.json")
            config_file.parent.mkdir(parents=True, exist_ok=True)
            
            config = {
                "global_mapping": self.global_mapping,
                "platform_mappings": self.platform_mappings
            }
            
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            QMessageBox.information(self, "Saved", 
                "Controller configuration saved successfully!")
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Save Failed",
                f"Failed to save controller configuration:\n{e}")
