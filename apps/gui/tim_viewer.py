#!/usr/bin/env python3
#this belongs in apps/gui/tim_viewer.py - Version: 1
# X-Seti - May22 2026 - ResBio-Evil-Workshop - TIM Texture Viewer
"""
TIM Texture Viewer - Displays PSX TIM texture files.
Supports 4/8/16/24-bit color modes. Pan and zoom.
Embeds into the display stack as page 2.
"""

from typing import Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QComboBox
)
from PyQt6.QtCore import Qt, QPoint, QSize
from PyQt6.QtGui import (
    QPainter, QPixmap, QImage, QColor, QWheelEvent, QMouseEvent, QFont
)

from apps.core.re1_formats import TIMFile, parse_tim

##Methods list -
# load_tim_file
# load_tim_data
# reset_view
# set_zoom

##class TIMCanvas:
##class TIMViewerWidget:

COL_BG = QColor(20, 22, 26)


class TIMCanvas(QWidget): #vers 1
    """Canvas that renders a TIM texture with pan and zoom."""

    def __init__(self, parent=None): #vers 1
        super().__init__(parent)
        self._pixmap: Optional[QPixmap] = None
        self._zoom = 1.0
        self._pan = QPoint(0, 0)
        self._drag_start: Optional[QPoint] = None
        self.setMouseTracking(True)
        self.setMinimumSize(200, 200)
        self.setStyleSheet("background-color: #14161a;")

    def set_pixmap(self, pixmap: QPixmap): #vers 1
        self._pixmap = pixmap
        self.reset_view()

    def reset_view(self): #vers 1
        """Center and fit the image."""
        if not self._pixmap:
            self._zoom = 1.0
            self._pan = QPoint(0, 0)
            self.update()
            return
        zoom_x = self.width()  / max(self._pixmap.width(), 1)
        zoom_y = self.height() / max(self._pixmap.height(), 1)
        self._zoom = min(zoom_x, zoom_y, 4.0)
        self._zoom = max(self._zoom, 0.1)
        iw = int(self._pixmap.width()  * self._zoom)
        ih = int(self._pixmap.height() * self._zoom)
        self._pan = QPoint((self.width() - iw) // 2, (self.height() - ih) // 2)
        self.update()

    def set_zoom(self, zoom: float): #vers 1
        self._zoom = max(0.1, min(zoom, 16.0))
        self.update()

    def paintEvent(self, event): #vers 1
        painter = QPainter(self)
        painter.fillRect(self.rect(), COL_BG)

        if not self._pixmap:
            painter.setPen(QColor(100, 100, 100))
            painter.setFont(QFont("Courier New", 11))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter,
                             "No TIM loaded\nOpen a .tim file or select from RDT")
            return

        if self._pixmap.isNull():
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter,
                             "Failed to load image")
            return
        iw = max(1, int(self._pixmap.width()  * self._zoom))
        ih = max(1, int(self._pixmap.height() * self._zoom))
        scaled = self._pixmap.scaled(iw, ih,
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.FastTransformation)
        painter.drawPixmap(self._pan, scaled)

        # Info overlay
        painter.setPen(QColor(180, 180, 180))
        painter.setFont(QFont("Courier New", 8))
        info = f"{self._pixmap.width()}x{self._pixmap.height()}  {self._zoom*100:.0f}%"
        painter.drawText(6, self.height() - 6, info)

    def mousePressEvent(self, event: QMouseEvent): #vers 1
        if event.button() in (Qt.MouseButton.LeftButton, Qt.MouseButton.MiddleButton):
            self._drag_start = event.pos()

    def mouseMoveEvent(self, event: QMouseEvent): #vers 1
        if self._drag_start and event.buttons():
            delta = event.pos() - self._drag_start
            self._pan += delta
            self._drag_start = event.pos()
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent): #vers 1
        self._drag_start = None

    def wheelEvent(self, event: QWheelEvent): #vers 1
        pos = event.position().toPoint()
        # Compute world coord under cursor before zoom
        wx = (pos.x() - self._pan.x()) / self._zoom
        wy = (pos.y() - self._pan.y()) / self._zoom

        factor = 1.2 if event.angleDelta().y() > 0 else (1.0 / 1.2)
        self._zoom = max(0.1, min(self._zoom * factor, 16.0))

        # Keep point under cursor
        self._pan = QPoint(
            pos.x() - int(wx * self._zoom),
            pos.y() - int(wy * self._zoom)
        )
        self.update()

    def resizeEvent(self, event): #vers 1
        super().resizeEvent(event)
        if self._pixmap:
            self.reset_view()


class TIMViewerWidget(QWidget): #vers 1
    """TIM viewer with toolbar. Embeds as display stack page 2."""

    def __init__(self, parent=None): #vers 1
        super().__init__(parent)
        self._tim: Optional[TIMFile] = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Toolbar
        toolbar = QFrame()
        toolbar.setFrameStyle(QFrame.Shape.StyledPanel)
        toolbar.setMaximumHeight(32)
        tl = QHBoxLayout(toolbar)
        tl.setContentsMargins(4, 2, 4, 2)
        tl.setSpacing(4)

        fit_btn = QPushButton("Fit")
        fit_btn.setMaximumHeight(24)
        fit_btn.clicked.connect(self._on_fit)
        tl.addWidget(fit_btn)

        zoom_in_btn = QPushButton("+")
        zoom_in_btn.setMaximumHeight(24)
        zoom_in_btn.setMaximumWidth(28)
        zoom_in_btn.clicked.connect(lambda: self._zoom_step(1.5))
        tl.addWidget(zoom_in_btn)

        zoom_out_btn = QPushButton("-")
        zoom_out_btn.setMaximumHeight(24)
        zoom_out_btn.setMaximumWidth(28)
        zoom_out_btn.clicked.connect(lambda: self._zoom_step(1.0 / 1.5))
        tl.addWidget(zoom_out_btn)

        tl.addStretch()

        self._info_label = QLabel("No texture")
        self._info_label.setFont(QFont("Courier New", 8))
        tl.addWidget(self._info_label)

        layout.addWidget(toolbar)

        self.canvas = TIMCanvas(self)
        layout.addWidget(self.canvas, stretch=1)

    def load_tim_file(self, file_path: str): #vers 1
        """Parse and display a TIM file from disk."""
        tim = parse_tim(file_path)
        self.load_tim_data(tim)

    def load_tim_data(self, tim: TIMFile): #vers 1
        """Display a pre-parsed TIMFile."""
        self._tim = tim
        if not tim.valid or not tim.rgba_data:
            self._info_label.setText(f"Parse error: {'; '.join(tim.parse_errors)}")
            self.canvas.set_pixmap(QPixmap())
            return

        image = QImage(
            tim.rgba_data,
            tim.width,
            tim.height,
            tim.width * 4,
            QImage.Format.Format_RGBA8888
        )
        if image.isNull():
            self._info_label.setText("Failed to create image")
            return

        pixmap = QPixmap.fromImage(image)
        self.canvas.set_pixmap(pixmap)

        bpp_names = {0: "4bpp", 1: "8bpp", 2: "16bpp", 3: "24bpp"}
        bpp = bpp_names.get(tim.header.bpp if tim.header else 2, "?bpp")
        self._info_label.setText(f"{tim.width}x{tim.height}  {bpp}")

    def reset_view(self): #vers 1
        self.canvas.reset_view()

    def _on_fit(self): #vers 1
        self.canvas.reset_view()

    def _zoom_step(self, factor: float): #vers 1
        self.canvas.set_zoom(self.canvas._zoom * factor)
