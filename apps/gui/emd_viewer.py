#!/usr/bin/env python3
#this belongs in apps/gui/emd_viewer.py - Version: 1
# X-Seti - May22 2026 - ResBio-Evil-Workshop - EMD Wireframe Viewer
"""
EMD Wireframe Viewer - Renders RE1 EMD 3D model as a wireframe
using QPainter with simple perspective projection.
No OpenGL required. Pan, rotate, zoom.
"""

import math
from typing import Optional, List, Tuple

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame
from PyQt6.QtCore import Qt, QPoint, QRect
from PyQt6.QtGui import (
    QPainter, QPen, QBrush, QColor, QFont,
    QWheelEvent, QMouseEvent, QKeyEvent
)

from apps.core.re1_formats import EMDFile, EMDMesh, EMDVertex, parse_emd

##Methods list -
# _project
# _rotate_x
# _rotate_y
# _rotate_z
# _draw_axes
# _draw_mesh
# _draw_status
# keyPressEvent
# load_emd_file
# load_emd
# mouseMoveEvent
# mousePressEvent
# mouseReleaseEvent
# paintEvent
# reset_view
# wheelEvent

##class EMDCanvas:
##class EMDViewerWidget:


COL_BG      = QColor(14,  16,  20)
COL_WIRE    = QColor(60,  180, 60)
COL_WIRE_HI = QColor(120, 255, 120)
COL_AXIS_X  = QColor(220, 60,  60)
COL_AXIS_Y  = QColor(60,  220, 60)
COL_AXIS_Z  = QColor(60,  60,  220)
COL_TEXT    = QColor(180, 180, 180)


def _rotate_y(v: Tuple, angle: float) -> Tuple: #vers 1
    c, s = math.cos(angle), math.sin(angle)
    x, y, z = v
    return (x*c + z*s, y, -x*s + z*c)

def _rotate_x(v: Tuple, angle: float) -> Tuple: #vers 1
    c, s = math.cos(angle), math.sin(angle)
    x, y, z = v
    return (x, y*c - z*s, y*s + z*c)


class EMDCanvas(QWidget): #vers 1

    def __init__(self, parent=None): #vers 1
        super().__init__(parent)
        self._emd: Optional[EMDFile] = None
        self._rot_x = 0.3
        self._rot_y = 0.4
        self._zoom  = 1.0
        self._pan   = QPoint(0, 0)
        self._drag_start: Optional[QPoint] = None
        self._panning = False

        self.show_axes = True
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setStyleSheet("background-color: #0e1014;")
        self.setMinimumSize(200, 200)

    def load_emd_file(self, path: str): #vers 1
        emd = parse_emd(path)
        self.load_emd(emd)

    def load_emd(self, emd: EMDFile): #vers 1
        self._emd = emd
        self.reset_view()
        self.update()

    def reset_view(self): #vers 1
        self._rot_x = 0.3
        self._rot_y = 0.4
        self._zoom  = 1.0
        self._pan   = QPoint(self.width() // 2, self.height() // 2)
        self.update()

    def _project(self, v: Tuple) -> Tuple[int, int]: #vers 1
        """Simple perspective projection."""
        fov = 400 * self._zoom
        z = v[2] + 5.0
        if z <= 0.01:
            z = 0.01
        sx = int(v[0] * fov / z) + self._pan.x()
        sy = int(-v[1] * fov / z) + self._pan.y()
        return sx, sy

    def paintEvent(self, event): #vers 1
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), COL_BG)

        if not self._emd:
            painter.setPen(QColor(60, 70, 80))
            painter.setFont(QFont("Courier New", 10))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter,
                             "No EMD model loaded\nOpen an .emd file")
            return

        if self.show_axes:
            self._draw_axes(painter)

        for mesh in self._emd.meshes:
            self._draw_mesh(painter, mesh)

        self._draw_status(painter)

    def _draw_axes(self, painter: QPainter): #vers 1
        length = 0.5
        axes = [
            (COL_AXIS_X, (0,0,0), (length,0,0), "X"),
            (COL_AXIS_Y, (0,0,0), (0,length,0), "Y"),
            (COL_AXIS_Z, (0,0,0), (0,0,length), "Z"),
        ]
        for color, a, b, label in axes:
            ra = _rotate_x(_rotate_y(a, self._rot_y), self._rot_x)
            rb = _rotate_x(_rotate_y(b, self._rot_y), self._rot_x)
            ax, ay = self._project(ra)
            bx, by = self._project(rb)
            painter.setPen(QPen(color, 1))
            painter.drawLine(ax, ay, bx, by)
            painter.setFont(QFont("Courier New", 7))
            painter.setPen(QPen(color))
            painter.drawText(bx + 2, by + 4, label)

    def _draw_mesh(self, painter: QPainter, mesh: EMDMesh): #vers 1
        if not mesh.vertices:
            return

        # Scale vertices to reasonable display size
        scale = 1.0 / 4096.0

        # Project all vertices
        projected = []
        for v in mesh.vertices:
            rv = _rotate_x(_rotate_y(
                (v.x * scale, v.y * scale, v.z * scale),
                self._rot_y), self._rot_x)
            projected.append(self._project(rv))

        # Draw edges from triangles
        painter.setPen(QPen(COL_WIRE, 1))
        for tri in mesh.triangles:
            if (tri.v0 < len(projected) and
                tri.v1 < len(projected) and
                tri.v2 < len(projected)):
                p0 = projected[tri.v0]
                p1 = projected[tri.v1]
                p2 = projected[tri.v2]
                painter.drawLine(p0[0], p0[1], p1[0], p1[1])
                painter.drawLine(p1[0], p1[1], p2[0], p2[1])
                painter.drawLine(p2[0], p2[1], p0[0], p0[1])

        # Vertex dots
        painter.setBrush(QBrush(COL_WIRE_HI))
        painter.setPen(Qt.PenStyle.NoPen)
        if len(projected) < 500:  # skip dots for dense models
            for px, py in projected:
                painter.drawEllipse(QPoint(px, py), 1, 1)

    def _draw_status(self, painter: QPainter): #vers 1
        if not self._emd:
            return
        verts = sum(len(m.vertices) for m in self._emd.meshes)
        tris  = sum(len(m.triangles) for m in self._emd.meshes)
        painter.setPen(QPen(COL_TEXT))
        painter.setFont(QFont("Courier New", 8))
        painter.drawText(6, self.height() - 6,
            f"Meshes: {len(self._emd.meshes)}  Verts: {verts}  Tris: {tris}  "
            f"[drag=rotate  scroll=zoom  R=reset  A=axes]")

    def mousePressEvent(self, event: QMouseEvent): #vers 1
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start = event.pos()
        elif event.button() == Qt.MouseButton.MiddleButton:
            self._panning = True
            self._drag_start = event.pos()

    def mouseMoveEvent(self, event: QMouseEvent): #vers 1
        if not self._drag_start:
            return
        delta = event.pos() - self._drag_start
        self._drag_start = event.pos()
        if self._panning or event.buttons() & Qt.MouseButton.MiddleButton:
            self._pan += delta
        elif event.buttons() & Qt.MouseButton.LeftButton:
            self._rot_y += delta.x() * 0.01
            self._rot_x += delta.y() * 0.01
        self.update()

    def mouseReleaseEvent(self, event: QMouseEvent): #vers 1
        self._drag_start = None
        self._panning = False

    def wheelEvent(self, event: QWheelEvent): #vers 1
        factor = 1.15 if event.angleDelta().y() > 0 else (1.0 / 1.15)
        self._zoom = max(0.05, min(self._zoom * factor, 20.0))
        self.update()

    def keyPressEvent(self, event: QKeyEvent): #vers 1
        k = event.key()
        if k in (Qt.Key.Key_R, Qt.Key.Key_Home):
            self.reset_view()
        elif k == Qt.Key.Key_A:
            self.show_axes = not self.show_axes
            self.update()
        else:
            super().keyPressEvent(event)


class EMDViewerWidget(QWidget): #vers 1
    """EMD viewer + toolbar for embedding in display stack."""

    def __init__(self, parent=None): #vers 1
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Toolbar
        tb = QFrame()
        tb.setFrameStyle(QFrame.Shape.StyledPanel)
        tb.setMaximumHeight(32)
        tl = QHBoxLayout(tb)
        tl.setContentsMargins(4, 2, 4, 2)
        tl.setSpacing(4)

        reset_btn = QPushButton("Reset [R]")
        reset_btn.setMaximumHeight(24)
        reset_btn.clicked.connect(lambda: self.canvas.reset_view())
        tl.addWidget(reset_btn)

        axes_btn = QPushButton("Axes [A]")
        axes_btn.setMaximumHeight(24)
        axes_btn.setCheckable(True)
        axes_btn.setChecked(True)
        axes_btn.clicked.connect(lambda v: (
            setattr(self.canvas, 'show_axes', v), self.canvas.update()))
        tl.addWidget(axes_btn)

        tl.addStretch()
        self._info = QLabel("No model")
        self._info.setFont(QFont("Courier New", 8))
        tl.addWidget(self._info)

        layout.addWidget(tb)

        self.canvas = EMDCanvas(self)
        layout.addWidget(self.canvas, stretch=1)

    def load_emd_file(self, path: str): #vers 1
        self.canvas.load_emd_file(path)
        from apps.core.re1_formats import parse_emd
        emd = parse_emd(path)
        if emd.valid:
            v = sum(len(m.vertices) for m in emd.meshes)
            t = sum(len(m.triangles) for m in emd.meshes)
            self._info.setText(f"{path.split('/')[-1]}  v:{v} t:{t}")

    def load_emd(self, emd): #vers 1
        self.canvas.load_emd(emd)
