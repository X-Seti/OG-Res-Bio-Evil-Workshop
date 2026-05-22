#!/usr/bin/env python3
#this belongs in apps/methods/resbio_svg_icons.py - Version: 2
# X-Seti - May22 2026 - ResBio-Evil-Workshop - SVG Icons Factory

from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtGui import QPixmap, QPainter, QIcon, QColor
from PyQt6.QtCore import Qt, QByteArray

##Methods list -
# _svg_to_icon
# _make
# add_icon
# analyze_icon
# arrow_down_icon
# arrow_left_icon
# arrow_right_icon
# arrow_up_icon
# box_icon
# build_icon
# check_icon
# chip_icon
# close_icon
# color_picker_icon
# compress_icon
# controller_icon
# convert_icon
# copy_icon
# create_icon
# delete_icon
# duplicate_icon
# export_icon
# fit_icon
# flip_horz_icon
# flip_vert_icon
# folder_icon
# import_icon
# info_icon
# launch_icon
# manage_icon
# maximize_icon
# mesh_icon
# minimize_icon
# open_icon
# package_icon
# paint_icon
# paste_icon
# properties_icon
# record_icon
# reset_icon
# rotate_ccw_icon
# rotate_cw_icon
# save_icon
# saveas_icon
# screenshot_icon
# settings_icon
# sphere_icon
# stop_icon
# uncompress_icon
# undo_icon
# view_icon
# volume_down_icon
# volume_up_icon
# zoom_in_icon
# zoom_out_icon


class ResBioSVGIcons:
    """SVG icon factory for ResBio-Evil-Workshop."""

    @staticmethod
    def _svg_to_icon(svg_data: str, size: int = 24, color: str = None) -> QIcon: #vers 1
        """Render SVG string to QIcon, optionally colorizing strokes/fills."""
        try:
            if color:
                svg_data = svg_data.replace('currentColor', color)
            data = QByteArray(svg_data.encode('utf-8'))
            renderer = QSvgRenderer(data)
            pixmap = QPixmap(size, size)
            pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pixmap)
            renderer.render(painter)
            painter.end()
            return QIcon(pixmap)
        except Exception as e:
            print(f"SVG icon error: {e}")
            return QIcon()

    @staticmethod
    def _make(svg: str, size: int = 20, color: str = '#cccccc') -> QIcon: #vers 1
        """Shorthand for _svg_to_icon."""
        return ResBioSVGIcons._svg_to_icon(svg, size, color)

    # --- Window controls ---

    @staticmethod
    def minimize_icon(size=20, color='#cccccc') -> QIcon: #vers 1
        return ResBioSVGIcons._make(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
            '<line x1="4" y1="12" x2="20" y2="12" stroke="currentColor" stroke-width="2.5"/>'
            '</svg>', size, color)

    @staticmethod
    def maximize_icon(size=20, color='#cccccc') -> QIcon: #vers 1
        return ResBioSVGIcons._make(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
            '<rect x="4" y="4" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"/>'
            '</svg>', size, color)

    @staticmethod
    def close_icon(size=20, color='#cccccc') -> QIcon: #vers 1
        return ResBioSVGIcons._make(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
            '<line x1="5" y1="5" x2="19" y2="19" stroke="currentColor" stroke-width="2.5"/>'
            '<line x1="19" y1="5" x2="5" y2="19" stroke="currentColor" stroke-width="2.5"/>'
            '</svg>', size, color)

    # --- File operations ---

    @staticmethod
    def open_icon(size=20, color='#cccccc') -> QIcon: #vers 1
        return ResBioSVGIcons._make(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
            '<path d="M3 7h6l2 2h10v12H3z" fill="none" stroke="currentColor" stroke-width="1.8"/>'
            '</svg>', size, color)

    @staticmethod
    def save_icon(size=20, color='#cccccc') -> QIcon: #vers 1
        return ResBioSVGIcons._make(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
            '<path d="M5 3h11l3 3v15H5z" fill="none" stroke="currentColor" stroke-width="1.8"/>'
            '<rect x="8" y="3" width="8" height="5" fill="none" stroke="currentColor" stroke-width="1.5"/>'
            '<rect x="7" y="13" width="10" height="7" fill="none" stroke="currentColor" stroke-width="1.5"/>'
            '</svg>', size, color)

    @staticmethod
    def saveas_icon(size=20, color='#cccccc') -> QIcon: #vers 1
        return ResBioSVGIcons._make(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
            '<path d="M5 3h11l3 3v15H5z" fill="none" stroke="currentColor" stroke-width="1.8"/>'
            '<rect x="8" y="3" width="8" height="5" fill="none" stroke="currentColor" stroke-width="1.5"/>'
            '<line x1="14" y1="18" x2="20" y2="18" stroke="currentColor" stroke-width="2"/>'
            '<line x1="17" y1="15" x2="17" y2="21" stroke="currentColor" stroke-width="2"/>'
            '</svg>', size, color)

    @staticmethod
    def folder_icon(size=20, color='#cccccc') -> QIcon: #vers 1
        return ResBioSVGIcons._make(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
            '<path d="M2 6h8l2 2h10v12H2z" fill="none" stroke="currentColor" stroke-width="1.8"/>'
            '</svg>', size, color)

    @staticmethod
    def export_icon(size=20, color='#cccccc') -> QIcon: #vers 1
        return ResBioSVGIcons._make(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
            '<path d="M12 3v12m0-12l-4 4m4-4l4 4" stroke="currentColor" stroke-width="2" fill="none"/>'
            '<path d="M4 17v3h16v-3" stroke="currentColor" stroke-width="2" fill="none"/>'
            '</svg>', size, color)

    @staticmethod
    def import_icon(size=20, color='#cccccc') -> QIcon: #vers 1
        return ResBioSVGIcons._make(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
            '<path d="M12 21V9m0 12l-4-4m4 4l4-4" stroke="currentColor" stroke-width="2" fill="none"/>'
            '<path d="M4 7V4h16v3" stroke="currentColor" stroke-width="2" fill="none"/>'
            '</svg>', size, color)

    @staticmethod
    def package_icon(size=20, color='#cccccc') -> QIcon: #vers 1
        return ResBioSVGIcons._make(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
            '<polygon points="12,2 22,7 22,17 12,22 2,17 2,7" fill="none" stroke="currentColor" stroke-width="1.8"/>'
            '<line x1="2" y1="7" x2="12" y2="12" stroke="currentColor" stroke-width="1.5"/>'
            '<line x1="22" y1="7" x2="12" y2="12" stroke="currentColor" stroke-width="1.5"/>'
            '<line x1="12" y1="12" x2="12" y2="22" stroke="currentColor" stroke-width="1.5"/>'
            '</svg>', size, color)

    # --- Edit operations ---

    @staticmethod
    def undo_icon(size=20, color='#cccccc') -> QIcon: #vers 1
        return ResBioSVGIcons._make(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
            '<path d="M4 8h10a6 6 0 0 1 0 12H8" fill="none" stroke="currentColor" stroke-width="2"/>'
            '<polyline points="4,4 4,8 8,8" fill="none" stroke="currentColor" stroke-width="2"/>'
            '</svg>', size, color)

    @staticmethod
    def copy_icon(size=20, color='#cccccc') -> QIcon: #vers 1
        return ResBioSVGIcons._make(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
            '<rect x="8" y="8" width="13" height="13" rx="1" fill="none" stroke="currentColor" stroke-width="1.8"/>'
            '<path d="M5 16H4a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h11a1 1 0 0 1 1 1v1" fill="none" stroke="currentColor" stroke-width="1.8"/>'
            '</svg>', size, color)

    @staticmethod
    def paste_icon(size=20, color='#cccccc') -> QIcon: #vers 1
        return ResBioSVGIcons._make(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
            '<rect x="8" y="4" width="13" height="17" rx="1" fill="none" stroke="currentColor" stroke-width="1.8"/>'
            '<path d="M8 8H5a1 1 0 0 0-1 1v12a1 1 0 0 0 1 1h10a1 1 0 0 0 1-1v-3" fill="none" stroke="currentColor" stroke-width="1.8"/>'
            '<rect x="10" y="2" width="7" height="4" rx="1" fill="none" stroke="currentColor" stroke-width="1.5"/>'
            '</svg>', size, color)

    @staticmethod
    def delete_icon(size=20, color='#cccccc') -> QIcon: #vers 1
        return ResBioSVGIcons._make(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
            '<polyline points="3,6 5,6 21,6" stroke="currentColor" stroke-width="2" fill="none"/>'
            '<path d="M19 6l-1 14H6L5 6" fill="none" stroke="currentColor" stroke-width="1.8"/>'
            '<path d="M9 6V4h6v2" fill="none" stroke="currentColor" stroke-width="1.8"/>'
            '</svg>', size, color)

    @staticmethod
    def create_icon(size=20, color='#cccccc') -> QIcon: #vers 1
        return ResBioSVGIcons._make(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
            '<rect x="4" y="4" width="16" height="16" rx="1" fill="none" stroke="currentColor" stroke-width="1.8"/>'
            '<line x1="12" y1="8" x2="12" y2="16" stroke="currentColor" stroke-width="2"/>'
            '<line x1="8" y1="12" x2="16" y2="12" stroke="currentColor" stroke-width="2"/>'
            '</svg>', size, color)

    @staticmethod
    def add_icon(size=20, color='#cccccc') -> QIcon: #vers 1
        return ResBioSVGIcons._make(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
            '<circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="1.8"/>'
            '<line x1="12" y1="8" x2="12" y2="16" stroke="currentColor" stroke-width="2"/>'
            '<line x1="8" y1="12" x2="16" y2="12" stroke="currentColor" stroke-width="2"/>'
            '</svg>', size, color)

    @staticmethod
    def duplicate_icon(size=20, color='#cccccc') -> QIcon: #vers 1
        return ResBioSVGIcons._make(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
            '<rect x="9" y="9" width="12" height="12" rx="1" fill="none" stroke="currentColor" stroke-width="1.8"/>'
            '<path d="M5 15H4a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h10a1 1 0 0 1 1 1v1" fill="none" stroke="currentColor" stroke-width="1.8"/>'
            '</svg>', size, color)

    # --- Transform ---

    @staticmethod
    def flip_vert_icon(size=20, color='#cccccc') -> QIcon: #vers 1
        return ResBioSVGIcons._make(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
            '<line x1="4" y1="12" x2="20" y2="12" stroke="currentColor" stroke-width="2" stroke-dasharray="3,2"/>'
            '<polyline points="7,7 12,2 17,7" fill="none" stroke="currentColor" stroke-width="2"/>'
            '<polyline points="7,17 12,22 17,17" fill="none" stroke="currentColor" stroke-width="2"/>'
            '</svg>', size, color)

    @staticmethod
    def flip_horz_icon(size=20, color='#cccccc') -> QIcon: #vers 1
        return ResBioSVGIcons._make(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
            '<line x1="12" y1="4" x2="12" y2="20" stroke="currentColor" stroke-width="2" stroke-dasharray="3,2"/>'
            '<polyline points="7,7 2,12 7,17" fill="none" stroke="currentColor" stroke-width="2"/>'
            '<polyline points="17,7 22,12 17,17" fill="none" stroke="currentColor" stroke-width="2"/>'
            '</svg>', size, color)

    @staticmethod
    def rotate_cw_icon(size=20, color='#cccccc') -> QIcon: #vers 1
        return ResBioSVGIcons._make(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
            '<path d="M20 8a9 9 0 1 0 1 5" fill="none" stroke="currentColor" stroke-width="2"/>'
            '<polyline points="20,2 20,8 14,8" fill="none" stroke="currentColor" stroke-width="2"/>'
            '</svg>', size, color)

    @staticmethod
    def rotate_ccw_icon(size=20, color='#cccccc') -> QIcon: #vers 1
        return ResBioSVGIcons._make(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
            '<path d="M4 8a9 9 0 1 1-1 5" fill="none" stroke="currentColor" stroke-width="2"/>'
            '<polyline points="4,2 4,8 10,8" fill="none" stroke="currentColor" stroke-width="2"/>'
            '</svg>', size, color)

    # --- View ---

    @staticmethod
    def zoom_in_icon(size=20, color='#cccccc') -> QIcon: #vers 1
        return ResBioSVGIcons._make(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
            '<circle cx="11" cy="11" r="7" fill="none" stroke="currentColor" stroke-width="1.8"/>'
            '<line x1="16" y1="16" x2="21" y2="21" stroke="currentColor" stroke-width="2"/>'
            '<line x1="8" y1="11" x2="14" y2="11" stroke="currentColor" stroke-width="2"/>'
            '<line x1="11" y1="8" x2="11" y2="14" stroke="currentColor" stroke-width="2"/>'
            '</svg>', size, color)

    @staticmethod
    def zoom_out_icon(size=20, color='#cccccc') -> QIcon: #vers 1
        return ResBioSVGIcons._make(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
            '<circle cx="11" cy="11" r="7" fill="none" stroke="currentColor" stroke-width="1.8"/>'
            '<line x1="16" y1="16" x2="21" y2="21" stroke="currentColor" stroke-width="2"/>'
            '<line x1="8" y1="11" x2="14" y2="11" stroke="currentColor" stroke-width="2"/>'
            '</svg>', size, color)

    @staticmethod
    def fit_icon(size=20, color='#cccccc') -> QIcon: #vers 1
        return ResBioSVGIcons._make(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
            '<polyline points="4,9 4,4 9,4" fill="none" stroke="currentColor" stroke-width="2"/>'
            '<polyline points="15,4 20,4 20,9" fill="none" stroke="currentColor" stroke-width="2"/>'
            '<polyline points="20,15 20,20 15,20" fill="none" stroke="currentColor" stroke-width="2"/>'
            '<polyline points="9,20 4,20 4,15" fill="none" stroke="currentColor" stroke-width="2"/>'
            '</svg>', size, color)

    @staticmethod
    def view_icon(size=20, color='#cccccc') -> QIcon: #vers 1
        return ResBioSVGIcons._make(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
            '<path d="M1 12S5 4 12 4s11 8 11 8-4 8-11 8S1 12 1 12z" fill="none" stroke="currentColor" stroke-width="1.8"/>'
            '<circle cx="12" cy="12" r="3" fill="none" stroke="currentColor" stroke-width="1.8"/>'
            '</svg>', size, color)

    @staticmethod
    def reset_icon(size=20, color='#cccccc') -> QIcon: #vers 1
        return ResBioSVGIcons._make(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
            '<path d="M3 12a9 9 0 1 1 2 5.5" fill="none" stroke="currentColor" stroke-width="2"/>'
            '<polyline points="3,7 3,12 8,12" fill="none" stroke="currentColor" stroke-width="2"/>'
            '</svg>', size, color)

    # --- Arrows ---

    @staticmethod
    def arrow_up_icon(size=20, color='#cccccc') -> QIcon: #vers 1
        return ResBioSVGIcons._make(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
            '<polyline points="5,15 12,8 19,15" fill="none" stroke="currentColor" stroke-width="2.5"/>'
            '</svg>', size, color)

    @staticmethod
    def arrow_down_icon(size=20, color='#cccccc') -> QIcon: #vers 1
        return ResBioSVGIcons._make(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
            '<polyline points="5,9 12,16 19,9" fill="none" stroke="currentColor" stroke-width="2.5"/>'
            '</svg>', size, color)

    @staticmethod
    def arrow_left_icon(size=20, color='#cccccc') -> QIcon: #vers 1
        return ResBioSVGIcons._make(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
            '<polyline points="15,5 8,12 15,19" fill="none" stroke="currentColor" stroke-width="2.5"/>'
            '</svg>', size, color)

    @staticmethod
    def arrow_right_icon(size=20, color='#cccccc') -> QIcon: #vers 1
        return ResBioSVGIcons._make(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
            '<polyline points="9,5 16,12 9,19" fill="none" stroke="currentColor" stroke-width="2.5"/>'
            '</svg>', size, color)

    # --- Tools / actions ---

    @staticmethod
    def settings_icon(size=20, color='#cccccc') -> QIcon: #vers 1
        return ResBioSVGIcons._make(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
            '<circle cx="12" cy="12" r="3" fill="none" stroke="currentColor" stroke-width="1.8"/>'
            '<path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" fill="none" stroke="currentColor" stroke-width="1.5"/>'
            '</svg>', size, color)

    @staticmethod
    def info_icon(size=20, color='#cccccc') -> QIcon: #vers 1
        return ResBioSVGIcons._make(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
            '<circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="1.8"/>'
            '<line x1="12" y1="8" x2="12" y2="8" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>'
            '<line x1="12" y1="11" x2="12" y2="16" stroke="currentColor" stroke-width="2"/>'
            '</svg>', size, color)

    @staticmethod
    def properties_icon(size=20, color='#cccccc') -> QIcon: #vers 1
        return ResBioSVGIcons._make(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
            '<line x1="8" y1="6" x2="21" y2="6" stroke="currentColor" stroke-width="2"/>'
            '<line x1="8" y1="12" x2="21" y2="12" stroke="currentColor" stroke-width="2"/>'
            '<line x1="8" y1="18" x2="21" y2="18" stroke="currentColor" stroke-width="2"/>'
            '<circle cx="4" cy="6" r="1.5" stroke="currentColor" stroke-width="1.5" fill="none"/>'
            '<circle cx="4" cy="12" r="1.5" stroke="currentColor" stroke-width="1.5" fill="none"/>'
            '<circle cx="4" cy="18" r="1.5" stroke="currentColor" stroke-width="1.5" fill="none"/>'
            '</svg>', size, color)

    @staticmethod
    def analyze_icon(size=20, color='#cccccc') -> QIcon: #vers 1
        return ResBioSVGIcons._make(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
            '<polyline points="22,12 18,12 15,21 9,3 6,12 2,12" fill="none" stroke="currentColor" stroke-width="2"/>'
            '</svg>', size, color)

    @staticmethod
    def check_icon(size=20, color='#cccccc') -> QIcon: #vers 1
        return ResBioSVGIcons._make(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
            '<polyline points="20,6 9,17 4,12" fill="none" stroke="currentColor" stroke-width="2.5"/>'
            '</svg>', size, color)

    @staticmethod
    def convert_icon(size=20, color='#cccccc') -> QIcon: #vers 1
        return ResBioSVGIcons._make(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
            '<polyline points="17,1 21,5 17,9" fill="none" stroke="currentColor" stroke-width="2"/>'
            '<path d="M3 11V9a4 4 0 0 1 4-4h14" fill="none" stroke="currentColor" stroke-width="2"/>'
            '<polyline points="7,23 3,19 7,15" fill="none" stroke="currentColor" stroke-width="2"/>'
            '<path d="M21 13v2a4 4 0 0 1-4 4H3" fill="none" stroke="currentColor" stroke-width="2"/>'
            '</svg>', size, color)

    @staticmethod
    def compress_icon(size=20, color='#cccccc') -> QIcon: #vers 1
        return ResBioSVGIcons._make(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
            '<polyline points="4,14 4,20 10,20" fill="none" stroke="currentColor" stroke-width="2"/>'
            '<polyline points="20,10 20,4 14,4" fill="none" stroke="currentColor" stroke-width="2"/>'
            '<line x1="14" y1="10" x2="20" y2="4" stroke="currentColor" stroke-width="2"/>'
            '<line x1="4" y1="20" x2="10" y2="14" stroke="currentColor" stroke-width="2"/>'
            '</svg>', size, color)

    @staticmethod
    def uncompress_icon(size=20, color='#cccccc') -> QIcon: #vers 1
        return ResBioSVGIcons._make(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
            '<polyline points="14,20 20,20 20,14" fill="none" stroke="currentColor" stroke-width="2"/>'
            '<polyline points="10,4 4,4 4,10" fill="none" stroke="currentColor" stroke-width="2"/>'
            '<line x1="20" y1="20" x2="14" y2="14" stroke="currentColor" stroke-width="2"/>'
            '<line x1="4" y1="4" x2="10" y2="10" stroke="currentColor" stroke-width="2"/>'
            '</svg>', size, color)

    @staticmethod
    def build_icon(size=20, color='#cccccc') -> QIcon: #vers 1
        return ResBioSVGIcons._make(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
            '<path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z" fill="none" stroke="currentColor" stroke-width="1.8"/>'
            '</svg>', size, color)

    @staticmethod
    def paint_icon(size=20, color='#cccccc') -> QIcon: #vers 1
        return ResBioSVGIcons._make(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
            '<path d="M19 3H5a2 2 0 0 0-2 2v4a2 2 0 0 0 2 2h3v9a1 1 0 0 0 2 0v-4h4a6 6 0 0 0 0-12z" fill="none" stroke="currentColor" stroke-width="1.8"/>'
            '</svg>', size, color)

    @staticmethod
    def color_picker_icon(size=20, color='#cccccc') -> QIcon: #vers 1
        return ResBioSVGIcons._make(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
            '<path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10c.926 0 1.648-.746 1.648-1.688 0-.437-.18-.835-.437-1.125-.29-.289-.438-.652-.438-1.125a1.64 1.64 0 0 1 1.668-1.668h1.996c3.051 0 5.555-2.503 5.555-5.554C21.965 6.012 17.461 2 12 2z" fill="none" stroke="currentColor" stroke-width="1.8"/>'
            '<circle cx="8.5" cy="14.5" r="1.5" fill="currentColor"/>'
            '<circle cx="6" cy="10" r="1.5" fill="currentColor"/>'
            '<circle cx="10" cy="6.5" r="1.5" fill="currentColor"/>'
            '</svg>', size, color)

    @staticmethod
    def manage_icon(size=20, color='#cccccc') -> QIcon: #vers 1
        return ResBioSVGIcons._make(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
            '<rect x="3" y="3" width="7" height="7" fill="none" stroke="currentColor" stroke-width="1.8"/>'
            '<rect x="14" y="3" width="7" height="7" fill="none" stroke="currentColor" stroke-width="1.8"/>'
            '<rect x="3" y="14" width="7" height="7" fill="none" stroke="currentColor" stroke-width="1.8"/>'
            '<rect x="14" y="14" width="7" height="7" fill="none" stroke="currentColor" stroke-width="1.8"/>'
            '</svg>', size, color)

    # --- 3D/mesh shapes ---

    @staticmethod
    def sphere_icon(size=20, color='#cccccc') -> QIcon: #vers 1
        return ResBioSVGIcons._make(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
            '<circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="1.8"/>'
            '<ellipse cx="12" cy="12" rx="4" ry="9" fill="none" stroke="currentColor" stroke-width="1.2"/>'
            '<line x1="3" y1="12" x2="21" y2="12" stroke="currentColor" stroke-width="1.2"/>'
            '</svg>', size, color)

    @staticmethod
    def box_icon(size=20, color='#cccccc') -> QIcon: #vers 1
        return ResBioSVGIcons._make(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
            '<polygon points="12,2 22,7 22,17 12,22 2,17 2,7" fill="none" stroke="currentColor" stroke-width="1.8"/>'
            '<line x1="12" y1="22" x2="12" y2="12" stroke="currentColor" stroke-width="1.5"/>'
            '<line x1="2" y1="7" x2="12" y2="12" stroke="currentColor" stroke-width="1.5"/>'
            '<line x1="22" y1="7" x2="12" y2="12" stroke="currentColor" stroke-width="1.5"/>'
            '</svg>', size, color)

    @staticmethod
    def mesh_icon(size=20, color='#cccccc') -> QIcon: #vers 1
        return ResBioSVGIcons._make(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
            '<polygon points="12,3 20,8 20,16 12,21 4,16 4,8" fill="none" stroke="currentColor" stroke-width="1.5"/>'
            '<line x1="12" y1="3" x2="12" y2="21" stroke="currentColor" stroke-width="1"/>'
            '<line x1="4" y1="8" x2="20" y2="8" stroke="currentColor" stroke-width="1"/>'
            '<line x1="4" y1="16" x2="20" y2="16" stroke="currentColor" stroke-width="1"/>'
            '</svg>', size, color)

    # --- Hardware/RE specific ---

    @staticmethod
    def chip_icon(size=20, color='#cccccc') -> QIcon: #vers 1
        return ResBioSVGIcons._make(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
            '<rect x="7" y="7" width="10" height="10" rx="1" fill="none" stroke="currentColor" stroke-width="1.8"/>'
            '<line x1="9" y1="3" x2="9" y2="7" stroke="currentColor" stroke-width="2"/>'
            '<line x1="12" y1="3" x2="12" y2="7" stroke="currentColor" stroke-width="2"/>'
            '<line x1="15" y1="3" x2="15" y2="7" stroke="currentColor" stroke-width="2"/>'
            '<line x1="9" y1="17" x2="9" y2="21" stroke="currentColor" stroke-width="2"/>'
            '<line x1="12" y1="17" x2="12" y2="21" stroke="currentColor" stroke-width="2"/>'
            '<line x1="15" y1="17" x2="15" y2="21" stroke="currentColor" stroke-width="2"/>'
            '<line x1="3" y1="9" x2="7" y2="9" stroke="currentColor" stroke-width="2"/>'
            '<line x1="3" y1="12" x2="7" y2="12" stroke="currentColor" stroke-width="2"/>'
            '<line x1="3" y1="15" x2="7" y2="15" stroke="currentColor" stroke-width="2"/>'
            '<line x1="17" y1="9" x2="21" y2="9" stroke="currentColor" stroke-width="2"/>'
            '<line x1="17" y1="12" x2="21" y2="12" stroke="currentColor" stroke-width="2"/>'
            '<line x1="17" y1="15" x2="21" y2="15" stroke="currentColor" stroke-width="2"/>'
            '</svg>', size, color)

    @staticmethod
    def controller_icon(size=20, color='#cccccc') -> QIcon: #vers 1
        return ResBioSVGIcons._make(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
            '<path d="M6 12H4a2 2 0 0 0-2 2l1 5a2 2 0 0 0 2 1h2a2 2 0 0 0 2-1l1-3h4l1 3a2 2 0 0 0 2 1h2a2 2 0 0 0 2-1l1-5a2 2 0 0 0-2-2h-2L14 8H10L6 12z" fill="none" stroke="currentColor" stroke-width="1.8"/>'
            '<line x1="9" y1="12" x2="9" y2="16" stroke="currentColor" stroke-width="1.5"/>'
            '<line x1="7" y1="14" x2="11" y2="14" stroke="currentColor" stroke-width="1.5"/>'
            '<circle cx="16" cy="13" r="1" fill="currentColor"/>'
            '</svg>', size, color)

    # --- Media controls ---

    @staticmethod
    def launch_icon(size=20, color='#cccccc') -> QIcon: #vers 1
        return ResBioSVGIcons._make(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
            '<polygon points="5,3 19,12 5,21" fill="none" stroke="currentColor" stroke-width="2"/>'
            '</svg>', size, color)

    @staticmethod
    def stop_icon(size=20, color='#cccccc') -> QIcon: #vers 1
        return ResBioSVGIcons._make(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
            '<rect x="4" y="4" width="16" height="16" rx="2" fill="none" stroke="currentColor" stroke-width="2"/>'
            '</svg>', size, color)

    @staticmethod
    def record_icon(size=20, color='#ff4444') -> QIcon: #vers 1
        return ResBioSVGIcons._make(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
            '<circle cx="12" cy="12" r="8" fill="none" stroke="currentColor" stroke-width="2"/>'
            '<circle cx="12" cy="12" r="4" fill="currentColor"/>'
            '</svg>', size, color)

    @staticmethod
    def screenshot_icon(size=20, color='#cccccc') -> QIcon: #vers 1
        return ResBioSVGIcons._make(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
            '<path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z" fill="none" stroke="currentColor" stroke-width="1.8"/>'
            '<circle cx="12" cy="13" r="4" fill="none" stroke="currentColor" stroke-width="1.8"/>'
            '</svg>', size, color)

    @staticmethod
    def volume_up_icon(size=20, color='#cccccc') -> QIcon: #vers 1
        return ResBioSVGIcons._make(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
            '<polygon points="11,5 6,9 2,9 2,15 6,15 11,19" fill="none" stroke="currentColor" stroke-width="1.8"/>'
            '<path d="M15.54 8.46a5 5 0 0 1 0 7.07" fill="none" stroke="currentColor" stroke-width="2"/>'
            '<path d="M19.07 4.93a10 10 0 0 1 0 14.14" fill="none" stroke="currentColor" stroke-width="2"/>'
            '</svg>', size, color)

    @staticmethod
    def volume_down_icon(size=20, color='#cccccc') -> QIcon: #vers 1
        return ResBioSVGIcons._make(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
            '<polygon points="11,5 6,9 2,9 2,15 6,15 11,19" fill="none" stroke="currentColor" stroke-width="1.8"/>'
            '<path d="M15.54 8.46a5 5 0 0 1 0 7.07" fill="none" stroke="currentColor" stroke-width="2"/>'
            '</svg>', size, color)
