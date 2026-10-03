#!/usr/bin/env python3
#this belongs in apps/methods/controller_buttons.py - Version: 1
# X-Seti - November27 2025 - Multi-Emulator Launcher - Controller Button SVGs

"""
Controller Button SVG Factory
Generates SVG icons for different controller button types
"""

from PyQt6.QtGui import QIcon, QPixmap, QPainter
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtCore import QByteArray, QSize

##Methods list -
# create_8bitdo_a_button
# create_8bitdo_b_button
# create_8bitdo_x_button
# create_8bitdo_y_button
# create_dpad_down
# create_dpad_left
# create_dpad_right
# create_dpad_up
# create_generic_button
# create_playstation_circle
# create_playstation_cross
# create_playstation_l1
# create_playstation_l2
# create_playstation_r1
# create_playstation_r2
# create_playstation_square
# create_playstation_triangle
# create_steam_a_button
# create_steam_b_button
# create_steam_x_button
# create_steam_y_button
# create_trigger_button
# create_xbox_a_button
# create_xbox_b_button
# create_xbox_x_button
# create_xbox_y_button

class ControllerButtons: #vers 1
    """Factory for generating controller button SVG icons"""
    
    @staticmethod
    def create_playstation_cross(size=32, pressed=False): #vers 1
        """PlayStation X button - blue cross"""
        color = "#0070DD" if not pressed else "#00A0FF"
        svg = f'''<?xml version="1.0" encoding="UTF-8"?>
        <svg width="{size}" height="{size}" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
            <circle cx="16" cy="16" r="15" fill="{color}" stroke="#ffffff" stroke-width="2"/>
            <g transform="translate(16,16)">
                <line x1="-6" y1="-6" x2="6" y2="6" stroke="#ffffff" stroke-width="3" stroke-linecap="round"/>
                <line x1="-6" y1="6" x2="6" y2="-6" stroke="#ffffff" stroke-width="3" stroke-linecap="round"/>
            </g>
        </svg>'''
        return ControllerButtons._svg_to_icon(svg, size)
    
    @staticmethod
    def create_playstation_circle(size=32, pressed=False): #vers 1
        """PlayStation Circle button - red"""
        color = "#DD0000" if not pressed else "#FF3333"
        svg = f'''<?xml version="1.0" encoding="UTF-8"?>
        <svg width="{size}" height="{size}" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
            <circle cx="16" cy="16" r="15" fill="{color}" stroke="#ffffff" stroke-width="2"/>
            <circle cx="16" cy="16" r="7" fill="none" stroke="#ffffff" stroke-width="3"/>
        </svg>'''
        return ControllerButtons._svg_to_icon(svg, size)
    
    @staticmethod
    def create_playstation_square(size=32, pressed=False): #vers 1
        """PlayStation Square button - pink"""
        color = "#DD00AA" if not pressed else "#FF33CC"
        svg = f'''<?xml version="1.0" encoding="UTF-8"?>
        <svg width="{size}" height="{size}" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
            <circle cx="16" cy="16" r="15" fill="{color}" stroke="#ffffff" stroke-width="2"/>
            <rect x="10" y="10" width="12" height="12" fill="none" stroke="#ffffff" stroke-width="3"/>
        </svg>'''
        return ControllerButtons._svg_to_icon(svg, size)
    
    @staticmethod
    def create_playstation_triangle(size=32, pressed=False): #vers 1
        """PlayStation Triangle button - green"""
        color = "#00AA00" if not pressed else "#33DD33"
        svg = f'''<?xml version="1.0" encoding="UTF-8"?>
        <svg width="{size}" height="{size}" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
            <circle cx="16" cy="16" r="15" fill="{color}" stroke="#ffffff" stroke-width="2"/>
            <polygon points="16,9 23,22 9,22" fill="none" stroke="#ffffff" stroke-width="3" stroke-linejoin="round"/>
        </svg>'''
        return ControllerButtons._svg_to_icon(svg, size)
    
    @staticmethod
    def create_playstation_l1(size=32, pressed=False): #vers 1
        """PlayStation L1 shoulder button"""
        color = "#555555" if not pressed else "#888888"
        svg = f'''<?xml version="1.0" encoding="UTF-8"?>
        <svg width="{size}" height="{size}" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
            <rect x="2" y="8" width="28" height="16" rx="4" fill="{color}" stroke="#ffffff" stroke-width="2"/>
            <text x="16" y="20" font-size="12" font-weight="bold" fill="#ffffff" text-anchor="middle">L1</text>
        </svg>'''
        return ControllerButtons._svg_to_icon(svg, size)
    
    @staticmethod
    def create_playstation_l2(size=32, pressed=False): #vers 1
        """PlayStation L2 trigger button"""
        color = "#666666" if not pressed else "#999999"
        svg = f'''<?xml version="1.0" encoding="UTF-8"?>
        <svg width="{size}" height="{size}" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
            <rect x="2" y="8" width="28" height="16" rx="4" fill="{color}" stroke="#ffffff" stroke-width="2"/>
            <text x="16" y="20" font-size="12" font-weight="bold" fill="#ffffff" text-anchor="middle">L2</text>
        </svg>'''
        return ControllerButtons._svg_to_icon(svg, size)
    
    @staticmethod
    def create_playstation_r1(size=32, pressed=False): #vers 1
        """PlayStation R1 shoulder button"""
        color = "#555555" if not pressed else "#888888"
        svg = f'''<?xml version="1.0" encoding="UTF-8"?>
        <svg width="{size}" height="{size}" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
            <rect x="2" y="8" width="28" height="16" rx="4" fill="{color}" stroke="#ffffff" stroke-width="2"/>
            <text x="16" y="20" font-size="12" font-weight="bold" fill="#ffffff" text-anchor="middle">R1</text>
        </svg>'''
        return ControllerButtons._svg_to_icon(svg, size)
    
    @staticmethod
    def create_playstation_r2(size=32, pressed=False): #vers 1
        """PlayStation R2 trigger button"""
        color = "#666666" if not pressed else "#999999"
        svg = f'''<?xml version="1.0" encoding="UTF-8"?>
        <svg width="{size}" height="{size}" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
            <rect x="2" y="8" width="28" height="16" rx="4" fill="{color}" stroke="#ffffff" stroke-width="2"/>
            <text x="16" y="20" font-size="12" font-weight="bold" fill="#ffffff" text-anchor="middle">R2</text>
        </svg>'''
        return ControllerButtons._svg_to_icon(svg, size)
    
    @staticmethod
    def create_xbox_a_button(size=32, pressed=False): #vers 1
        """Xbox A button - green"""
        color = "#00AA00" if not pressed else "#33DD33"
        svg = f'''<?xml version="1.0" encoding="UTF-8"?>
        <svg width="{size}" height="{size}" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
            <circle cx="16" cy="16" r="15" fill="{color}" stroke="#ffffff" stroke-width="2"/>
            <text x="16" y="22" font-size="18" font-weight="bold" fill="#ffffff" text-anchor="middle">A</text>
        </svg>'''
        return ControllerButtons._svg_to_icon(svg, size)
    
    @staticmethod
    def create_xbox_b_button(size=32, pressed=False): #vers 1
        """Xbox B button - red"""
        color = "#DD0000" if not pressed else "#FF3333"
        svg = f'''<?xml version="1.0" encoding="UTF-8"?>
        <svg width="{size}" height="{size}" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
            <circle cx="16" cy="16" r="15" fill="{color}" stroke="#ffffff" stroke-width="2"/>
            <text x="16" y="22" font-size="18" font-weight="bold" fill="#ffffff" text-anchor="middle">B</text>
        </svg>'''
        return ControllerButtons._svg_to_icon(svg, size)
    
    @staticmethod
    def create_xbox_x_button(size=32, pressed=False): #vers 1
        """Xbox X button - blue"""
        color = "#0070DD" if not pressed else "#00A0FF"
        svg = f'''<?xml version="1.0" encoding="UTF-8"?>
        <svg width="{size}" height="{size}" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
            <circle cx="16" cy="16" r="15" fill="{color}" stroke="#ffffff" stroke-width="2"/>
            <text x="16" y="22" font-size="18" font-weight="bold" fill="#ffffff" text-anchor="middle">X</text>
        </svg>'''
        return ControllerButtons._svg_to_icon(svg, size)
    
    @staticmethod
    def create_xbox_y_button(size=32, pressed=False): #vers 1
        """Xbox Y button - yellow"""
        color = "#DDAA00" if not pressed else "#FFCC33"
        svg = f'''<?xml version="1.0" encoding="UTF-8"?>
        <svg width="{size}" height="{size}" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
            <circle cx="16" cy="16" r="15" fill="{color}" stroke="#ffffff" stroke-width="2"/>
            <text x="16" y="22" font-size="18" font-weight="bold" fill="#ffffff" text-anchor="middle">Y</text>
        </svg>'''
        return ControllerButtons._svg_to_icon(svg, size)
    
    @staticmethod
    def create_steam_a_button(size=32, pressed=False): #vers 1
        """Steam Controller A button"""
        color = "#1B2838" if not pressed else "#2A475E"
        svg = f'''<?xml version="1.0" encoding="UTF-8"?>
        <svg width="{size}" height="{size}" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
            <circle cx="16" cy="16" r="15" fill="{color}" stroke="#66C0F4" stroke-width="2"/>
            <text x="16" y="22" font-size="18" font-weight="bold" fill="#66C0F4" text-anchor="middle">A</text>
        </svg>'''
        return ControllerButtons._svg_to_icon(svg, size)
    
    @staticmethod
    def create_steam_b_button(size=32, pressed=False): #vers 1
        """Steam Controller B button"""
        color = "#1B2838" if not pressed else "#2A475E"
        svg = f'''<?xml version="1.0" encoding="UTF-8"?>
        <svg width="{size}" height="{size}" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
            <circle cx="16" cy="16" r="15" fill="{color}" stroke="#66C0F4" stroke-width="2"/>
            <text x="16" y="22" font-size="18" font-weight="bold" fill="#66C0F4" text-anchor="middle">B</text>
        </svg>'''
        return ControllerButtons._svg_to_icon(svg, size)
    
    @staticmethod
    def create_steam_x_button(size=32, pressed=False): #vers 1
        """Steam Controller X button"""
        color = "#1B2838" if not pressed else "#2A475E"
        svg = f'''<?xml version="1.0" encoding="UTF-8"?>
        <svg width="{size}" height="{size}" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
            <circle cx="16" cy="16" r="15" fill="{color}" stroke="#66C0F4" stroke-width="2"/>
            <text x="16" y="22" font-size="18" font-weight="bold" fill="#66C0F4" text-anchor="middle">X</text>
        </svg>'''
        return ControllerButtons._svg_to_icon(svg, size)
    
    @staticmethod
    def create_steam_y_button(size=32, pressed=False): #vers 1
        """Steam Controller Y button"""
        color = "#1B2838" if not pressed else "#2A475E"
        svg = f'''<?xml version="1.0" encoding="UTF-8"?>
        <svg width="{size}" height="{size}" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
            <circle cx="16" cy="16" r="15" fill="{color}" stroke="#66C0F4" stroke-width="2"/>
            <text x="16" y="22" font-size="18" font-weight="bold" fill="#66C0F4" text-anchor="middle">Y</text>
        </svg>'''
        return ControllerButtons._svg_to_icon(svg, size)
    
    @staticmethod
    def create_8bitdo_a_button(size=32, pressed=False): #vers 1
        """8BitDo A button - red"""
        color = "#DD0000" if not pressed else "#FF3333"
        svg = f'''<?xml version="1.0" encoding="UTF-8"?>
        <svg width="{size}" height="{size}" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
            <circle cx="16" cy="16" r="15" fill="{color}" stroke="#ffffff" stroke-width="2"/>
            <text x="16" y="22" font-size="18" font-weight="bold" fill="#ffffff" text-anchor="middle">A</text>
        </svg>'''
        return ControllerButtons._svg_to_icon(svg, size)
    
    @staticmethod
    def create_8bitdo_b_button(size=32, pressed=False): #vers 1
        """8BitDo B button - yellow"""
        color = "#DDAA00" if not pressed else "#FFCC33"
        svg = f'''<?xml version="1.0" encoding="UTF-8"?>
        <svg width="{size}" height="{size}" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
            <circle cx="16" cy="16" r="15" fill="{color}" stroke="#ffffff" stroke-width="2"/>
            <text x="16" y="22" font-size="18" font-weight="bold" fill="#ffffff" text-anchor="middle">B</text>
        </svg>'''
        return ControllerButtons._svg_to_icon(svg, size)
    
    @staticmethod
    def create_8bitdo_x_button(size=32, pressed=False): #vers 1
        """8BitDo X button - blue"""
        color = "#0070DD" if not pressed else "#00A0FF"
        svg = f'''<?xml version="1.0" encoding="UTF-8"?>
        <svg width="{size}" height="{size}" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
            <circle cx="16" cy="16" r="15" fill="{color}" stroke="#ffffff" stroke-width="2"/>
            <text x="16" y="22" font-size="18" font-weight="bold" fill="#ffffff" text-anchor="middle">X</text>
        </svg>'''
        return ControllerButtons._svg_to_icon(svg, size)
    
    @staticmethod
    def create_8bitdo_y_button(size=32, pressed=False): #vers 1
        """8BitDo Y button - green"""
        color = "#00AA00" if not pressed else "#33DD33"
        svg = f'''<?xml version="1.0" encoding="UTF-8"?>
        <svg width="{size}" height="{size}" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
            <circle cx="16" cy="16" r="15" fill="{color}" stroke="#ffffff" stroke-width="2"/>
            <text x="16" y="22" font-size="18" font-weight="bold" fill="#ffffff" text-anchor="middle">Y</text>
        </svg>'''
        return ControllerButtons._svg_to_icon(svg, size)
    
    @staticmethod
    def create_dpad_up(size=32, pressed=False): #vers 1
        """D-Pad Up button"""
        color = "#333333" if not pressed else "#666666"
        svg = f'''<?xml version="1.0" encoding="UTF-8"?>
        <svg width="{size}" height="{size}" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
            <rect x="10" y="2" width="12" height="28" rx="2" fill="{color}" stroke="#ffffff" stroke-width="1"/>
            <rect x="2" y="10" width="28" height="12" rx="2" fill="{color}" stroke="#ffffff" stroke-width="1"/>
            <polygon points="16,8 20,14 12,14" fill="#ffffff"/>
        </svg>'''
        return ControllerButtons._svg_to_icon(svg, size)
    
    @staticmethod
    def create_dpad_down(size=32, pressed=False): #vers 1
        """D-Pad Down button"""
        color = "#333333" if not pressed else "#666666"
        svg = f'''<?xml version="1.0" encoding="UTF-8"?>
        <svg width="{size}" height="{size}" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
            <rect x="10" y="2" width="12" height="28" rx="2" fill="{color}" stroke="#ffffff" stroke-width="1"/>
            <rect x="2" y="10" width="28" height="12" rx="2" fill="{color}" stroke="#ffffff" stroke-width="1"/>
            <polygon points="16,24 12,18 20,18" fill="#ffffff"/>
        </svg>'''
        return ControllerButtons._svg_to_icon(svg, size)
    
    @staticmethod
    def create_dpad_left(size=32, pressed=False): #vers 1
        """D-Pad Left button"""
        color = "#333333" if not pressed else "#666666"
        svg = f'''<?xml version="1.0" encoding="UTF-8"?>
        <svg width="{size}" height="{size}" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
            <rect x="10" y="2" width="12" height="28" rx="2" fill="{color}" stroke="#ffffff" stroke-width="1"/>
            <rect x="2" y="10" width="28" height="12" rx="2" fill="{color}" stroke="#ffffff" stroke-width="1"/>
            <polygon points="8,16 14,12 14,20" fill="#ffffff"/>
        </svg>'''
        return ControllerButtons._svg_to_icon(svg, size)
    
    @staticmethod
    def create_dpad_right(size=32, pressed=False): #vers 1
        """D-Pad Right button"""
        color = "#333333" if not pressed else "#666666"
        svg = f'''<?xml version="1.0" encoding="UTF-8"?>
        <svg width="{size}" height="{size}" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
            <rect x="10" y="2" width="12" height="28" rx="2" fill="{color}" stroke="#ffffff" stroke-width="1"/>
            <rect x="2" y="10" width="28" height="12" rx="2" fill="{color}" stroke="#ffffff" stroke-width="1"/>
            <polygon points="24,16 18,20 18,12" fill="#ffffff"/>
        </svg>'''
        return ControllerButtons._svg_to_icon(svg, size)
    
    @staticmethod
    def create_generic_button(size=32, label="", pressed=False): #vers 1
        """Generic button with custom label"""
        color = "#555555" if not pressed else "#888888"
        svg = f'''<?xml version="1.0" encoding="UTF-8"?>
        <svg width="{size}" height="{size}" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
            <circle cx="16" cy="16" r="15" fill="{color}" stroke="#ffffff" stroke-width="2"/>
            <text x="16" y="21" font-size="14" font-weight="bold" fill="#ffffff" text-anchor="middle">{label}</text>
        </svg>'''
        return ControllerButtons._svg_to_icon(svg, size)
    
    @staticmethod
    def create_trigger_button(size=32, label="", pressed=False): #vers 1
        """Trigger button (L2/R2 style)"""
        color = "#666666" if not pressed else "#999999"
        svg = f'''<?xml version="1.0" encoding="UTF-8"?>
        <svg width="{size}" height="{size}" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
            <path d="M 4,12 L 4,20 L 12,28 L 20,28 L 28,20 L 28,12 Z" 
                  fill="{color}" stroke="#ffffff" stroke-width="2"/>
            <text x="16" y="22" font-size="12" font-weight="bold" fill="#ffffff" text-anchor="middle">{label}</text>
        </svg>'''
        return ControllerButtons._svg_to_icon(svg, size)
    
    @staticmethod
    def _svg_to_icon(svg_string, size): #vers 1
        """Convert SVG string to QIcon"""
        svg_bytes = QByteArray(svg_string.encode('utf-8'))
        renderer = QSvgRenderer(svg_bytes)
        
        pixmap = QPixmap(QSize(size, size))
        pixmap.fill(0x00000000)  # Transparent
        
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        
        return QIcon(pixmap)
