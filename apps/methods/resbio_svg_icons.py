#!/usr/bin/env python3
#this belongs in apps/methods/resbio_svg_icons.py - Version: 1
# X-Seti - February19 2025 - ResBio-Evil-Workshop - SVG Icons Factory

from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtGui import QPixmap, QPainter, QIcon
from PyQt6.QtCore import Qt


class ResBioSVGIcons:
    """Factory class for SVG icons"""

    @staticmethod
    def _svg_to_icon(svg_data, size=24):
        """Convert SVG bytes to QIcon"""
        try:
            renderer = QSvgRenderer(svg_data)
            pixmap = QPixmap(size, size)
            pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pixmap)
            renderer.render(painter)
            painter.end()
            return QIcon(pixmap)
        except Exception as e:
            print(f"Error creating icon: {e}")
            return QIcon()

