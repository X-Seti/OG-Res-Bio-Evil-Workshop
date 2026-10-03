#!/usr/bin/env python3
#this belongs in apps/methods/controller_layouts.py - Version: 2
# X-Seti - November27 2025 - Multi-Emulator Launcher - Controller Layouts

"""
Controller Layout SVG Factory
Generates simplified button layout diagrams without controller bodies
"""

from PyQt6.QtGui import QPixmap, QPainter
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtCore import QByteArray, QSize, QPointF
from typing import Dict, Tuple

##Methods list -
# get_8bitdo_layout
# get_cd32_layout
# get_dreamcast_layout
# get_gamecube_layout
# get_generic_layout
# get_playstation_layout
# get_steam_layout
# get_xbox_layout
# render_layout

class ControllerLayouts: #vers 2
    """Factory for generating simplified controller button layouts"""
    
    @staticmethod
    def get_playstation_layout(width=800, height=400): #vers 2
        """Get PlayStation button layout - buttons only, no controller body"""
        svg = f'''<?xml version="1.0" encoding="UTF-8"?>
        <svg width="{width}" height="{height}" viewBox="0 0 800 400" xmlns="http://www.w3.org/2000/svg">
            <!-- Title -->
            <text x="400" y="40" font-size="20" font-weight="bold" fill="#AAAAAA" text-anchor="middle">PlayStation Controller</text>
            
            <!-- Group labels -->
            <text x="280" y="140" font-size="12" fill="#888888" text-anchor="middle">D-Pad</text>
            <text x="520" y="140" font-size="12" fill="#888888" text-anchor="middle">Face Buttons</text>
            <text x="280" y="90" font-size="12" fill="#888888" text-anchor="middle">L1 / L2</text>
            <text x="520" y="90" font-size="12" fill="#888888" text-anchor="middle">R1 / R2</text>
            <text x="320" y="250" font-size="12" fill="#888888" text-anchor="middle">L3</text>
            <text x="480" y="250" font-size="12" fill="#888888" text-anchor="middle">R3</text>
            <text x="400" y="190" font-size="12" fill="#888888" text-anchor="middle">Touchpad / Options / Share / PS</text>
        </svg>'''
        
        positions = {
            'cross': (520, 230), 'circle': (550, 200), 
            'square': (520, 170), 'triangle': (490, 200),
            'dpad_up': (280, 170), 'dpad_down': (280, 230),
            'dpad_left': (250, 200), 'dpad_right': (310, 200),
            'l1': (280, 110), 'r1': (520, 110),
            'l2': (280, 80), 'r2': (520, 80),
            'l3': (320, 280), 'r3': (480, 280),
            'share': (360, 210), 'options': (440, 210),
            'ps': (400, 210), 'touchpad': (400, 170)
        }
        return svg, positions
    
    @staticmethod
    def get_xbox_layout(width=800, height=400): #vers 2
        """Get Xbox button layout - buttons only"""
        svg = f'''<?xml version="1.0" encoding="UTF-8"?>
        <svg width="{width}" height="{height}" viewBox="0 0 800 400" xmlns="http://www.w3.org/2000/svg">
            <text x="400" y="40" font-size="20" font-weight="bold" fill="#AAAAAA" text-anchor="middle">Xbox Controller</text>
            <text x="300" y="140" font-size="12" fill="#888888" text-anchor="middle">D-Pad</text>
            <text x="500" y="140" font-size="12" fill="#888888" text-anchor="middle">Face Buttons</text>
            <text x="280" y="90" font-size="12" fill="#888888" text-anchor="middle">LB / LT</text>
            <text x="520" y="90" font-size="12" fill="#888888" text-anchor="middle">RB / RT</text>
            <text x="340" y="250" font-size="12" fill="#888888" text-anchor="middle">Left Stick</text>
            <text x="460" y="110" font-size="12" fill="#888888" text-anchor="middle">Right Stick</text>
        </svg>'''
        
        positions = {
            'a': (500, 230), 'b': (530, 200),
            'x': (470, 200), 'y': (500, 170),
            'dpad_up': (300, 170), 'dpad_down': (300, 230),
            'dpad_left': (270, 200), 'dpad_right': (330, 200),
            'lb': (280, 110), 'rb': (520, 110),
            'lt': (280, 80), 'rt': (520, 80),
            'left_stick': (340, 280), 'right_stick': (460, 140),
            'view': (360, 200), 'menu': (440, 200), 'xbox': (400, 200)
        }
        return svg, positions
    
    @staticmethod
    def get_gamecube_layout(width=800, height=400): #vers 2
        """Get GameCube button layout - buttons only"""
        svg = f'''<?xml version="1.0" encoding="UTF-8"?>
        <svg width="{width}" height="{height}" viewBox="0 0 800 400" xmlns="http://www.w3.org/2000/svg">
            <text x="400" y="40" font-size="20" font-weight="bold" fill="#AAAAAA" text-anchor="middle">GameCube Controller</text>
            <text x="280" y="130" font-size="12" fill="#888888" text-anchor="middle">D-Pad</text>
            <text x="510" y="130" font-size="12" fill="#888888" text-anchor="middle">A/B/X/Y</text>
            <text x="310" y="200" font-size="12" fill="#888888" text-anchor="middle">Analog</text>
            <text x="470" y="150" font-size="12" fill="#888888" text-anchor="middle">C-Stick</text>
            <text x="280" y="90" font-size="12" fill="#888888" text-anchor="middle">L / R</text>
            <text x="570" y="230" font-size="12" fill="#888888" text-anchor="middle">Z</text>
        </svg>'''
        
        positions = {
            'a': (510, 200), 'b': (475, 220),
            'x': (510, 160), 'y': (475, 170),
            'dpad_up': (280, 136), 'dpad_down': (280, 184),
            'dpad_left': (256, 160), 'dpad_right': (304, 160),
            'analog': (310, 230), 'c_stick': (470, 180),
            'l': (280, 110), 'r': (495, 110), 'z': (570, 250),
            'start': (400, 190)
        }
        return svg, positions
    
    @staticmethod
    def get_dreamcast_layout(width=800, height=400): #vers 2
        """Get Dreamcast button layout - buttons only"""
        svg = f'''<?xml version="1.0" encoding="UTF-8"?>
        <svg width="{width}" height="{height}" viewBox="0 0 800 400" xmlns="http://www.w3.org/2000/svg">
            <text x="400" y="40" font-size="20" font-weight="bold" fill="#AAAAAA" text-anchor="middle">Dreamcast Controller</text>
            <text x="290" y="200" font-size="12" fill="#888888" text-anchor="middle">D-Pad</text>
            <text x="510" y="140" font-size="12" fill="#888888" text-anchor="middle">A/B/X/Y</text>
            <text x="290" y="280" font-size="12" fill="#888888" text-anchor="middle">Analog</text>
            <text x="295" y="90" font-size="12" fill="#888888" text-anchor="middle">L</text>
            <text x="505" y="90" font-size="12" fill="#888888" text-anchor="middle">R</text>
        </svg>'''
        
        positions = {
            'a': (510, 225), 'b': (535, 200),
            'x': (485, 200), 'y': (510, 175),
            'dpad_up': (290, 200), 'dpad_down': (290, 240),
            'dpad_left': (270, 220), 'dpad_right': (310, 220),
            'analog': (290, 310), 'l': (295, 110), 'r': (505, 110),
            'start': (400, 250)
        }
        return svg, positions
    
    @staticmethod
    def get_cd32_layout(width=800, height=400): #vers 2
        """Get Amiga CD32 button layout - buttons only"""
        svg = f'''<?xml version="1.0" encoding="UTF-8"?>
        <svg width="{width}" height="{height}" viewBox="0 0 800 400" xmlns="http://www.w3.org/2000/svg">
            <text x="400" y="40" font-size="20" font-weight="bold" fill="#AAAAAA" text-anchor="middle">Amiga CD32 Controller</text>
            <text x="290" y="190" font-size="12" fill="#888888" text-anchor="middle">D-Pad</text>
            <text x="450" y="190" font-size="12" fill="#888888" text-anchor="middle">Face Buttons</text>
            <text x="265" y="120" font-size="12" fill="#888888" text-anchor="middle">L / R</text>
            <text x="352" y="180" font-size="12" fill="#888888" text-anchor="middle">CD Controls</text>
        </svg>'''
        
        positions = {
            'green': (430, 220), 'red': (470, 220),
            'blue': (510, 220), 'yellow': (390, 220),
            'dpad_up': (290, 198), 'dpad_down': (290, 242),
            'dpad_left': (268, 220), 'dpad_right': (312, 220),
            'l': (265, 140), 'r': (535, 140),
            'play': (352, 206), 'rewind': (352, 224), 'forward': (352, 242)
        }
        return svg, positions
    
    @staticmethod
    def get_steam_layout(width=800, height=400): #vers 2
        """Get Steam Controller button layout - buttons only"""
        svg = f'''<?xml version="1.0" encoding="UTF-8"?>
        <svg width="{width}" height="{height}" viewBox="0 0 800 400" xmlns="http://www.w3.org/2000/svg">
            <text x="400" y="40" font-size="20" font-weight="bold" fill="#AAAAAA" text-anchor="middle">Steam Controller</text>
            <text x="300" y="170" font-size="12" fill="#888888" text-anchor="middle">Left Touchpad</text>
            <text x="500" y="140" font-size="12" fill="#888888" text-anchor="middle">A/B/X/Y</text>
            <text x="500" y="170" font-size="12" fill="#888888" text-anchor="middle">Right Touchpad</text>
            <text x="400" y="260" font-size="12" fill="#888888" text-anchor="middle">Analog Stick</text>
            <text x="295" y="120" font-size="12" fill="#888888" text-anchor="middle">LB / LT</text>
            <text x="545" y="120" font-size="12" fill="#888888" text-anchor="middle">RB / RT</text>
        </svg>'''
        
        positions = {
            'a': (500, 130), 'b': (530, 100),
            'x': (470, 100), 'y': (500, 70),
            'left_pad': (300, 200), 'right_pad': (500, 200),
            'stick': (400, 290), 'lb': (255, 140), 'rb': (545, 140),
            'lt': (240, 110), 'rt': (560, 110),
            'left_grip': (255, 168), 'right_grip': (545, 168),
            'steam': (400, 190)
        }
        return svg, positions
    
    @staticmethod
    def get_8bitdo_layout(width=800, height=400): #vers 2
        """Get 8BitDo button layout - buttons only"""
        svg = f'''<?xml version="1.0" encoding="UTF-8"?>
        <svg width="{width}" height="{height}" viewBox="0 0 800 400" xmlns="http://www.w3.org/2000/svg">
            <text x="400" y="40" font-size="20" font-weight="bold" fill="#AAAAAA" text-anchor="middle">8BitDo Controller (SNES Style)</text>
            <text x="280" y="180" font-size="12" fill="#888888" text-anchor="middle">D-Pad</text>
            <text x="520" y="180" font-size="12" fill="#888888" text-anchor="middle">A/B/X/Y</text>
            <text x="250" y="110" font-size="12" fill="#888888" text-anchor="middle">L / ZL</text>
            <text x="550" y="110" font-size="12" fill="#888888" text-anchor="middle">R / ZR</text>
            <text x="377" y="180" font-size="12" fill="#888888" text-anchor="middle">Select</text>
            <text x="422" y="180" font-size="12" fill="#888888" text-anchor="middle">Start</text>
        </svg>'''
        
        positions = {
            'a': (540, 210), 'b': (520, 235),
            'x': (520, 185), 'y': (500, 210),
            'dpad_up': (280, 180), 'dpad_down': (280, 240),
            'dpad_left': (250, 210), 'dpad_right': (310, 210),
            'l': (250, 130), 'r': (550, 130),
            'zl': (235, 100), 'zr': (565, 100),
            'select': (377, 200), 'start': (422, 200), 'home': (400, 230)
        }
        return svg, positions
    
    @staticmethod
    def get_generic_layout(width=800, height=400): #vers 2
        """Get generic button layout - buttons only"""
        svg = f'''<?xml version="1.0" encoding="UTF-8"?>
        <svg width="{width}" height="{height}" viewBox="0 0 800 400" xmlns="http://www.w3.org/2000/svg">
            <text x="400" y="40" font-size="20" font-weight="bold" fill="#AAAAAA" text-anchor="middle">Generic Gamepad</text>
            <text x="300" y="140" font-size="12" fill="#888888" text-anchor="middle">D-Pad</text>
            <text x="500" y="140" font-size="12" fill="#888888" text-anchor="middle">Face Buttons</text>
            <text x="265" y="90" font-size="12" fill="#888888" text-anchor="middle">L1 / L2</text>
            <text x="535" y="90" font-size="12" fill="#888888" text-anchor="middle">R1 / R2</text>
            <text x="350" y="200" font-size="12" fill="#888888" text-anchor="middle">Left Stick</text>
            <text x="450" y="200" font-size="12" fill="#888888" text-anchor="middle">Right Stick</text>
        </svg>'''
        
        positions = {
            'button_0': (500, 170), 'button_1': (530, 200),
            'button_2': (500, 230), 'button_3': (470, 200),
            'dpad_up': (300, 170), 'dpad_down': (300, 230),
            'dpad_left': (270, 200), 'dpad_right': (330, 200),
            'l1': (265, 110), 'r1': (535, 110),
            'l2': (250, 80), 'r2': (550, 80),
            'left_stick': (350, 230), 'right_stick': (450, 230),
            'select': (375, 180), 'start': (425, 180), 'home': (400, 200)
        }
        return svg, positions
    
    @staticmethod
    def render_layout(svg_string, width, height): #vers 1
        """Render SVG layout string to QPixmap"""
        svg_bytes = QByteArray(svg_string.encode('utf-8'))
        renderer = QSvgRenderer(svg_bytes)
        
        pixmap = QPixmap(QSize(width, height))
        pixmap.fill(0x00000000)  # Transparent
        
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        
        return pixmap
