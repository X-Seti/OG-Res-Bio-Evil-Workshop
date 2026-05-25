#!/usr/bin/env python3
#this belongs in apps/core/re_item_icons.py - Version: 1
# X-Seti - May25 2026 - ResBio-Evil-Workshop - Item Icon Loader
"""
Item Icon Loader - Extracts item icons from RE2 STATUS.TIM sprite sheet.
STATUS.TIM (/PSX/DATA/STATUS.TIM) contains all item icons in a grid.
Icons are sliced by item_type and cached as QPixmap.

RE1 uses TYPE00.TIM for the same purpose.
Icon grid layout determined from community research on RE2 inventory screen.
"""

import os
from typing import Optional, Dict, Tuple

##Methods list -
# load_status_tim
# get_icon
# find_status_tim
# clear_cache

##class ItemIconCache:


# RE2 STATUS.TIM icon grid layout
# Each icon slot is 32x32 pixels (before scaling)
# Grid is 8 icons wide, rows from top
# item_type maps to (col, row) in the grid
# Based on RE2 inventory screen layout research

RE2_ICON_GRID: Dict[int, Tuple[int, int]] = {
    # Row 0 - Weapons
    0x01: (0, 0),  # Handgun
    0x02: (1, 0),  # Shotgun
    0x03: (2, 0),  # Magnum
    0x04: (3, 0),  # Flamethrower
    0x05: (4, 0),  # Sparkthrower
    0x06: (5, 0),  # Rocket Launcher
    0x07: (6, 0),  # Gatling Gun
    0x08: (7, 0),  # Knife
    # Row 1 - Ammo
    0x09: (0, 1),  # Handgun Rounds
    0x0A: (1, 1),  # Shotgun Shells
    0x0B: (2, 1),  # Magnum Rounds
    0x0C: (3, 1),  # Fuel
    0x0D: (4, 1),  # Spark Rounds
    0x0E: (5, 1),  # Explosive Rounds
    0x0F: (6, 1),  # Ink Ribbon
    # Row 2 - Healing
    0x10: (0, 2),  # First Aid Spray
    0x11: (1, 2),  # Red Herb
    0x12: (2, 2),  # Green Herb
    0x13: (3, 2),  # Blue Herb
    0x14: (4, 2),  # Mixed R+G
    0x15: (5, 2),  # Mixed R+G+B
    0x16: (6, 2),  # Mixed G+B
    0x17: (7, 2),  # Mixed G+G
    # Row 3 - Keys
    0x1A: (0, 3),  # Small Key
    0x1B: (1, 3),  # Handcuffs
    0x30: (2, 3),  # Armor Key
    0x31: (3, 3),  # Locker Key
    0x32: (4, 3),  # Basement Key
    0x33: (5, 3),  # Spade Key
    0x34: (6, 3),  # Diamond Key
    0x35: (7, 3),  # Heart Key
    # Row 4 - Keys cont / medals
    0x36: (0, 4),  # Club Key
    0x46: (1, 4),  # Cabin Key
    0x20: (2, 4),  # Unicorn Medal
    0x21: (3, 4),  # Eagle Medal
    0x22: (4, 4),  # Wolf Medal
    0x40: (5, 4),  # STARS Badge
    0x3F: (6, 4),  # Emblem
    0x3C: (7, 4),  # Womens Statue
    # Row 5 - Plugs
    0x37: (0, 5),  # Rook Plug
    0x38: (1, 5),  # Knight Plug
    0x39: (2, 5),  # Bishop Plug
    0x3A: (3, 5),  # Queen Plug
    0x3B: (4, 5),  # King Plug
    0x2D: (5, 5),  # Joint Plug
    0x41: (6, 5),  # T-Bar Tool
    0x26: (7, 5),  # Manhole Opener
    # Row 6 - Quest items
    0x2B: (0, 6),  # G-Virus
    0x2A: (1, 6),  # Vaccine
    0x29: (2, 6),  # Vaccine Base
    0x4B: (3, 6),  # Red Jewel
    0x4D: (4, 6),  # Green Jewel
    0x4F: (5, 6),  # Blue Jewel
    0x51: (6, 6),  # Stone & Metal
    0x3D: (7, 6),  # Gold Cogwheel
    # Row 7 - Cards / tools
    0x52: (0, 7),  # Red Card Key
    0x53: (1, 7),  # Blue Card Key
    0x2C: (2, 7),  # Special Key
    0x25: (3, 7),  # Power Room Key
    0x27: (4, 7),  # Main Fuse
    0x28: (5, 7),  # Fuse Case
    0x43: (6, 7),  # Detonator
    0x44: (7, 7),  # C4 Bomb
}

# Icon dimensions in STATUS.TIM
ICON_W = 32
ICON_H = 32
GRID_W = 8   # icons per row


class ItemIconCache: #vers 1
    """Loads and caches item icons from STATUS.TIM."""

    def __init__(self): #vers 1
        self._cache: Dict[int, object] = {}   # item_type -> QPixmap
        self._sheet = None                     # QImage of full sprite sheet
        self._loaded = False
        self._tim_path = ''

    def load_status_tim(self, tim_path: str) -> bool: #vers 1
        """Load the STATUS.TIM sprite sheet. Returns True on success."""
        if not os.path.exists(tim_path):
            return False
        try:
            from apps.core.re1_formats import parse_tim
            from PyQt6.QtGui import QImage
            tim = parse_tim(tim_path)
            if not tim.valid or not tim.rgba_data:
                return False
            self._sheet = QImage(
                tim.rgba_data, tim.width, tim.height,
                tim.width * 4, QImage.Format.Format_RGBA8888)
            self._tim_path = tim_path
            self._loaded = True
            self._cache.clear()
            return True
        except Exception as e:
            print(f"ItemIconCache: load error: {e}")
            return False

    def find_status_tim(self, search_roots: list) -> bool: #vers 1
        """Search for STATUS.TIM in common locations."""
        candidates = [
            'PSX/DATA/STATUS.TIM',
            'DATA/STATUS.TIM',
            'STATUS.TIM',
        ]
        for root in search_roots:
            if not root or not os.path.isdir(root):
                continue
            for candidate in candidates:
                path = os.path.join(root, candidate)
                if os.path.exists(path):
                    return self.load_status_tim(path)
            # Walk up to 2 levels
            for dirpath, dirs, files in os.walk(root):
                depth = dirpath[len(root):].count(os.sep)
                if depth > 2:
                    dirs.clear()
                    continue
                for fname in files:
                    if fname.upper() == 'STATUS.TIM':
                        return self.load_status_tim(
                            os.path.join(dirpath, fname))
        return False

    def get_icon(self, item_type: int,
                 size: int = 24) -> Optional[object]: #vers 1
        """Return QPixmap icon for item_type, scaled to size x size.
        Returns None if not available.
        """
        cache_key = (item_type, size)
        if cache_key in self._cache:
            return self._cache[cache_key]

        if not self._loaded or self._sheet is None:
            return None

        grid_pos = RE2_ICON_GRID.get(item_type)
        if grid_pos is None:
            return None

        col, row = grid_pos
        x = col * ICON_W
        y = row * ICON_H

        if x + ICON_W > self._sheet.width() or y + ICON_H > self._sheet.height():
            return None

        try:
            from PyQt6.QtGui import QPixmap
            from PyQt6.QtCore import QRect
            cropped = self._sheet.copy(QRect(x, y, ICON_W, ICON_H))
            pixmap  = QPixmap.fromImage(cropped).scaled(
                size, size,
                aspectRatioMode=__import__('PyQt6.QtCore', fromlist=['Qt']).Qt.AspectRatioMode.KeepAspectRatio,
                transformMode=__import__('PyQt6.QtCore', fromlist=['Qt']).Qt.TransformationMode.SmoothTransformation,
            )
            self._cache[cache_key] = pixmap
            return pixmap
        except Exception as e:
            print(f"ItemIconCache: icon error type={item_type}: {e}")
            return None

    def clear_cache(self): #vers 1
        self._cache.clear()

    @property
    def loaded(self) -> bool:
        return self._loaded


# Global singleton
_icon_cache = ItemIconCache()


def get_item_icon(item_type: int, size: int = 24) -> Optional[object]: #vers 1
    """Get icon QPixmap for an item type. Returns None if cache not loaded."""
    return _icon_cache.get_icon(item_type, size)


def init_icon_cache(search_roots: list) -> bool: #vers 1
    """Initialise the global icon cache from a list of search folders."""
    return _icon_cache.find_status_tim(search_roots)


def is_cache_loaded() -> bool: #vers 1
    return _icon_cache.loaded
