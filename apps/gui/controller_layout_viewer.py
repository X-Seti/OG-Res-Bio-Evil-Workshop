#!/usr/bin/env python3
#this belongs in apps/gui/controller_layout_viewer.py - Version: 1
# X-Seti - November27 2025 - Multi-Emulator Launcher - Controller Layout Viewer

"""
Controller Layout Viewer Widget
Displays controller layout with button positions and real-time input visualization
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QFrame
from PyQt6.QtGui import QPixmap, QPainter, QPen, QColor, QFont
from PyQt6.QtCore import Qt, QTimer, QPoint
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from apps.methods.controller_layouts import ControllerLayouts
from apps.methods.controller_buttons import ControllerButtons

##Methods list -
# __init__
# paintEvent
# set_controller_type
# start_input_test
# stop_input_test
# update_button_states
# _draw_button_overlay
# _poll_controller_input
# _update_display

##class ControllerLayoutViewer -

class ControllerLayoutViewer(QWidget): #vers 1
    """Widget for displaying controller layout with button overlays"""
    
    # Controller type mapping
    CONTROLLER_TYPES = {
        'PlayStation': 'playstation',
        'PlayStation 2': 'playstation',
        'PlayStation 3': 'playstation',
        'Xbox': 'xbox',
        'Xbox 360': 'xbox',
        'Xbox One': 'xbox',
        'GameCube': 'gamecube',
        'Dreamcast': 'dreamcast',
        'Amiga CD32': 'cd32',
        'Steam': 'steam',
        '8BitDo': '8bitdo',
        'Generic': 'generic'
    }
    
    def __init__(self, gamepad_config=None, parent=None): #vers 1
        """Initialize controller layout viewer
        
        Args:
            gamepad_config: GamepadConfig instance for controller detection
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.gamepad_config = gamepad_config
        self.current_type = 'playstation'
        self.current_svg = None
        self.button_positions = {}
        self.button_states = {}  # Track which buttons are pressed
        self.controller_pixmap = None
        
        # Input polling
        self.input_timer = QTimer()
        self.input_timer.timeout.connect(self._poll_controller_input)
        self.controller_id = 0
        
        self._setup_ui()
        self._load_controller_layout('playstation')
        self._update_display()  # Show layout immediately
    
    def _setup_ui(self): #vers 1
        """Setup the UI layout"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Top controls
        controls_layout = QHBoxLayout()
        
        # Controller type selector
        type_label = QLabel("Controller Type:")
        controls_layout.addWidget(type_label)
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(self.CONTROLLER_TYPES.keys())
        self.type_combo.currentTextChanged.connect(self._on_type_changed)
        controls_layout.addWidget(self.type_combo)
        
        controls_layout.addStretch()
        
        # Test button
        self.test_btn = QPushButton("Start Input Test")
        self.test_btn.setCheckable(True)
        self.test_btn.toggled.connect(self._on_test_toggled)
        controls_layout.addWidget(self.test_btn)
        
        layout.addLayout(controls_layout)
        
        # Display area
        self.display_frame = QFrame()
        self.display_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        self.display_frame.setMinimumSize(800, 400)
        display_layout = QVBoxLayout(self.display_frame)
        display_layout.setContentsMargins(0, 0, 0, 0)
        
        self.display_label = QLabel()
        self.display_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.display_label.setMinimumSize(800, 400)
        display_layout.addWidget(self.display_label)
        
        layout.addWidget(self.display_frame)
        
        # Info label
        self.info_label = QLabel("Select controller type to view layout")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.info_label)
    
    def _on_type_changed(self, type_name): #vers 1
        """Handle controller type change"""
        controller_type = self.CONTROLLER_TYPES.get(type_name, 'generic')
        self.set_controller_type(controller_type)
    
    def _on_test_toggled(self, checked): #vers 1
        """Handle test button toggle"""
        if checked:
            self.start_input_test()
            self.test_btn.setText("Stop Input Test")
        else:
            self.stop_input_test()
            self.test_btn.setText("Start Input Test")
    
    def set_controller_type(self, controller_type): #vers 1
        """Set and display controller layout
        
        Args:
            controller_type: Type of controller ('playstation', 'xbox', etc.)
        """
        self.current_type = controller_type
        self._load_controller_layout(controller_type)
        self._update_display()
    
    def _load_controller_layout(self, controller_type): #vers 2
        """Load controller layout SVG and button positions"""
        # Get layout based on type
        if controller_type == 'playstation':
            svg, positions = ControllerLayouts.get_playstation_layout()
        elif controller_type == 'xbox':
            svg, positions = ControllerLayouts.get_xbox_layout()
        elif controller_type == 'gamecube':
            svg, positions = ControllerLayouts.get_gamecube_layout()
        elif controller_type == 'dreamcast':
            svg, positions = ControllerLayouts.get_dreamcast_layout()
        elif controller_type == 'cd32':
            svg, positions = ControllerLayouts.get_cd32_layout()
        elif controller_type == 'steam':
            svg, positions = ControllerLayouts.get_steam_layout()
        elif controller_type == '8bitdo':
            svg, positions = ControllerLayouts.get_8bitdo_layout()
        else:
            svg, positions = ControllerLayouts.get_generic_layout()
        
        self.current_svg = svg
        self.button_positions = positions
        
        # Render layout to pixmap
        self.controller_pixmap = ControllerLayouts.render_layout(svg, 800, 400)
        
        # Clear button states
        self.button_states = {btn: False for btn in positions.keys()}
        
        self.info_label.setText(f"{controller_type.title()} Controller Layout - {len(positions)} buttons mapped")
    
    def _update_display(self): #vers 1
        """Update the display with current controller and button states"""
        if not self.controller_pixmap:
            return
        
        # Create a copy to draw on
        display_pixmap = QPixmap(self.controller_pixmap)
        painter = QPainter(display_pixmap)
        
        # Draw button overlays
        for button_name, (x, y) in self.button_positions.items():
            pressed = self.button_states.get(button_name, False)
            self._draw_button_overlay(painter, button_name, x, y, pressed)
        
        painter.end()
        
        # Update display
        self.display_label.setPixmap(display_pixmap)
    
    def _draw_button_overlay(self, painter, button_name, x, y, pressed): #vers 1
        """Draw button icon overlay at position
        
        Args:
            painter: QPainter to draw with
            button_name: Name of button
            x, y: Position to draw at
            pressed: Whether button is currently pressed
        """
        # Get appropriate button icon based on controller type and button name
        icon = None
        size = 32
        
        if self.current_type == 'playstation':
            if button_name == 'cross':
                icon = ControllerButtons.create_playstation_cross(size, pressed)
            elif button_name == 'circle':
                icon = ControllerButtons.create_playstation_circle(size, pressed)
            elif button_name == 'square':
                icon = ControllerButtons.create_playstation_square(size, pressed)
            elif button_name == 'triangle':
                icon = ControllerButtons.create_playstation_triangle(size, pressed)
            elif button_name == 'l1':
                icon = ControllerButtons.create_playstation_l1(size, pressed)
            elif button_name == 'l2':
                icon = ControllerButtons.create_playstation_l2(size, pressed)
            elif button_name == 'r1':
                icon = ControllerButtons.create_playstation_r1(size, pressed)
            elif button_name == 'r2':
                icon = ControllerButtons.create_playstation_r2(size, pressed)
            elif 'dpad' in button_name:
                if 'up' in button_name:
                    icon = ControllerButtons.create_dpad_up(size, pressed)
                elif 'down' in button_name:
                    icon = ControllerButtons.create_dpad_down(size, pressed)
                elif 'left' in button_name:
                    icon = ControllerButtons.create_dpad_left(size, pressed)
                elif 'right' in button_name:
                    icon = ControllerButtons.create_dpad_right(size, pressed)
        
        elif self.current_type == 'xbox':
            if button_name == 'a':
                icon = ControllerButtons.create_xbox_a_button(size, pressed)
            elif button_name == 'b':
                icon = ControllerButtons.create_xbox_b_button(size, pressed)
            elif button_name == 'x':
                icon = ControllerButtons.create_xbox_x_button(size, pressed)
            elif button_name == 'y':
                icon = ControllerButtons.create_xbox_y_button(size, pressed)
            elif 'dpad' in button_name:
                if 'up' in button_name:
                    icon = ControllerButtons.create_dpad_up(size, pressed)
                elif 'down' in button_name:
                    icon = ControllerButtons.create_dpad_down(size, pressed)
                elif 'left' in button_name:
                    icon = ControllerButtons.create_dpad_left(size, pressed)
                elif 'right' in button_name:
                    icon = ControllerButtons.create_dpad_right(size, pressed)
        
        elif self.current_type == 'steam':
            if button_name == 'a':
                icon = ControllerButtons.create_steam_a_button(size, pressed)
            elif button_name == 'b':
                icon = ControllerButtons.create_steam_b_button(size, pressed)
            elif button_name == 'x':
                icon = ControllerButtons.create_steam_x_button(size, pressed)
            elif button_name == 'y':
                icon = ControllerButtons.create_steam_y_button(size, pressed)
        
        elif self.current_type == '8bitdo':
            if button_name == 'a':
                icon = ControllerButtons.create_8bitdo_a_button(size, pressed)
            elif button_name == 'b':
                icon = ControllerButtons.create_8bitdo_b_button(size, pressed)
            elif button_name == 'x':
                icon = ControllerButtons.create_8bitdo_x_button(size, pressed)
            elif button_name == 'y':
                icon = ControllerButtons.create_8bitdo_y_button(size, pressed)
            elif 'dpad' in button_name:
                if 'up' in button_name:
                    icon = ControllerButtons.create_dpad_up(size, pressed)
                elif 'down' in button_name:
                    icon = ControllerButtons.create_dpad_down(size, pressed)
                elif 'left' in button_name:
                    icon = ControllerButtons.create_dpad_left(size, pressed)
                elif 'right' in button_name:
                    icon = ControllerButtons.create_dpad_right(size, pressed)
        
        # Draw generic button if no specific icon found
        if not icon:
            icon = ControllerButtons.create_generic_button(size, button_name[:3].upper(), pressed)
        
        # Draw icon at position (centered)
        if icon:
            pixmap = icon.pixmap(size, size)
            painter.drawPixmap(int(x - size/2), int(y - size/2), pixmap)
        
        # Draw button name label if pressed
        if pressed:
            painter.setPen(QPen(QColor(255, 255, 0), 2))
            font = QFont()
            font.setBold(True)
            font.setPointSize(10)
            painter.setFont(font)
            painter.drawText(int(x - 30), int(y + size/2 + 15), button_name.upper())
    
    def start_input_test(self, controller_id=0): #vers 1
        """Start polling controller input
        
        Args:
            controller_id: ID of controller to test
        """
        self.controller_id = controller_id
        
        if not self.gamepad_config:
            self.info_label.setText("⚠️ No gamepad config available - cannot test input")
            return
        
        # Detect controllers
        controllers = self.gamepad_config.detect_controllers()
        if not controllers:
            self.info_label.setText("⚠️ No controllers detected - please connect a controller")
            return
        
        self.info_label.setText(f"Testing: {controllers[0]['name']} - Press buttons to see them highlight")
        
        # Start polling at 60 FPS
        self.input_timer.start(16)
    
    def stop_input_test(self): #vers 1
        """Stop polling controller input"""
        self.input_timer.stop()
        
        # Clear all button states
        for button in self.button_states:
            self.button_states[button] = False
        
        self._update_display()
        self.info_label.setText(f"{self.current_type.title()} Controller Layout")
    
    def _poll_controller_input(self): #vers 2
        """Poll controller for button presses"""
        if not self.gamepad_config:
            return
        
        try:
            import pygame
            
            # Initialize pygame if not already done
            if not pygame.get_init():
                pygame.init()
            if not pygame.joystick.get_init():
                pygame.joystick.init()
            
            pygame.event.pump()
            
            # Get joystick
            if self.controller_id >= pygame.joystick.get_count():
                return
            
            joystick = pygame.joystick.Joystick(self.controller_id)
            if not joystick.get_init():
                joystick.init()
            
            # Update button states based on controller type
            if self.current_type == 'playstation':
                self._poll_playstation(joystick)
            elif self.current_type == 'xbox':
                self._poll_xbox(joystick)
            elif self.current_type == 'steam':
                self._poll_steam(joystick)
            elif self.current_type == '8bitdo':
                self._poll_8bitdo(joystick)
            else:
                self._poll_generic(joystick)
            
            # Update display
            self._update_display()
            
        except Exception as e:
            from apps.utils.debug_logger import error
            error(f"Error polling controller: {e}", "INPUT")
    
    def _poll_playstation(self, joystick): #vers 1
        """Poll PlayStation controller buttons"""
        # Face buttons
        self.button_states['cross'] = joystick.get_button(0)
        self.button_states['circle'] = joystick.get_button(1)
        self.button_states['square'] = joystick.get_button(2)
        self.button_states['triangle'] = joystick.get_button(3)
        
        # Shoulder buttons
        self.button_states['l1'] = joystick.get_button(4)
        self.button_states['r1'] = joystick.get_button(5)
        self.button_states['l2'] = joystick.get_button(6)
        self.button_states['r2'] = joystick.get_button(7)
        
        # D-Pad (hat)
        if joystick.get_numhats() > 0:
            hat = joystick.get_hat(0)
            self.button_states['dpad_up'] = hat[1] > 0
            self.button_states['dpad_down'] = hat[1] < 0
            self.button_states['dpad_left'] = hat[0] < 0
            self.button_states['dpad_right'] = hat[0] > 0
    
    def _poll_xbox(self, joystick): #vers 1
        """Poll Xbox controller buttons"""
        # Face buttons (Xbox layout)
        self.button_states['a'] = joystick.get_button(0)
        self.button_states['b'] = joystick.get_button(1)
        self.button_states['x'] = joystick.get_button(2)
        self.button_states['y'] = joystick.get_button(3)
        
        # Shoulder buttons
        self.button_states['lb'] = joystick.get_button(4)
        self.button_states['rb'] = joystick.get_button(5)
        
        # Triggers (axis)
        if joystick.get_numaxes() >= 6:
            self.button_states['lt'] = joystick.get_axis(4) > 0.5
            self.button_states['rt'] = joystick.get_axis(5) > 0.5
        
        # D-Pad
        if joystick.get_numhats() > 0:
            hat = joystick.get_hat(0)
            self.button_states['dpad_up'] = hat[1] > 0
            self.button_states['dpad_down'] = hat[1] < 0
            self.button_states['dpad_left'] = hat[0] < 0
            self.button_states['dpad_right'] = hat[0] > 0
    
    def _poll_steam(self, joystick): #vers 1
        """Poll Steam Controller buttons"""
        # Face buttons
        self.button_states['a'] = joystick.get_button(0)
        self.button_states['b'] = joystick.get_button(1)
        self.button_states['x'] = joystick.get_button(2)
        self.button_states['y'] = joystick.get_button(3)
        
        # Shoulder buttons
        self.button_states['lb'] = joystick.get_button(4)
        self.button_states['rb'] = joystick.get_button(5)
    
    def _poll_8bitdo(self, joystick): #vers 1
        """Poll 8BitDo controller buttons"""
        # Face buttons (SNES style)
        self.button_states['b'] = joystick.get_button(0)
        self.button_states['a'] = joystick.get_button(1)
        self.button_states['y'] = joystick.get_button(2)
        self.button_states['x'] = joystick.get_button(3)
        
        # Shoulder buttons
        self.button_states['l'] = joystick.get_button(4)
        self.button_states['r'] = joystick.get_button(5)
        self.button_states['zl'] = joystick.get_button(6)
        self.button_states['zr'] = joystick.get_button(7)
        
        # D-Pad
        if joystick.get_numhats() > 0:
            hat = joystick.get_hat(0)
            self.button_states['dpad_up'] = hat[1] > 0
            self.button_states['dpad_down'] = hat[1] < 0
            self.button_states['dpad_left'] = hat[0] < 0
            self.button_states['dpad_right'] = hat[0] > 0
    
    def _poll_generic(self, joystick): #vers 1
        """Poll generic controller buttons"""
        # Map first 8 buttons
        for i in range(min(8, joystick.get_numbuttons())):
            self.button_states[f'button_{i}'] = joystick.get_button(i)
        
        # D-Pad
        if joystick.get_numhats() > 0:
            hat = joystick.get_hat(0)
            self.button_states['dpad_up'] = hat[1] > 0
            self.button_states['dpad_down'] = hat[1] < 0
            self.button_states['dpad_left'] = hat[0] < 0
            self.button_states['dpad_right'] = hat[0] > 0
    
    def update_button_states(self, button_states_dict): #vers 1
        """Manually update button states (for external updates)
        
        Args:
            button_states_dict: Dict of button_name: bool pairs
        """
        self.button_states.update(button_states_dict)
        self._update_display()
    
    def paintEvent(self, event): #vers 1
        """Custom paint event"""
        super().paintEvent(event)
