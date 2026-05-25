#!/usr/bin/env python3
#this belongs in apps/gui/room_map_editor.py - Version: 1
# X-Seti - May22 2026 - ResBio-Evil-Workshop - Room Map Editor
"""
Room Map Editor - 2D top-down map editor for RE1 rooms.
Displays collision boundaries, camera positions, and item placements.
Supports pan, zoom, item selection and drag.
Uses QPainter only - no OpenGL dependency.
"""

from typing import Optional, List, Tuple
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame
from PyQt6.QtCore import Qt, QPoint, QRect, QRectF, pyqtSignal
from PyQt6.QtGui import (
    QPainter, QPen, QBrush, QColor, QFont, QTransform,
    QPainterPath, QWheelEvent, QMouseEvent, QKeyEvent
)

from apps.core.re1_formats import RDTFile, RDTItem, RDTCamera, RDTCollisionBoundary, get_item_name

##Methods list -
# _draw_cameras
# _draw_collision
# _draw_grid
# _draw_items
# _draw_scale_bar
# _find_item_at
# _room_to_screen
# _screen_to_room
# _world_bounds
# keyPressEvent
# load_rdt
# mouseMoveEvent
# mousePressEvent
# mouseReleaseEvent
# paintEvent
# reset_view
# wheelEvent

##class RoomMapEditor:
##class RoomMapToolbar:
##class RoomMapWidget:

# --- Color constants ---

COL_GRID          = QColor(60, 60, 60, 120)
COL_BOUNDARY      = QColor(80, 160, 255, 200)
COL_BOUNDARY_FILL = QColor(40, 80, 140, 60)
COL_CAMERA        = QColor(255, 200, 50, 230)
COL_CAMERA_LINE   = QColor(255, 200, 50, 100)
COL_ITEM          = QColor(80, 220, 80, 230)
COL_ITEM_SEL      = QColor(255, 100, 100, 255)
COL_ENEMY         = QColor(220, 60,  60,  230)   # red
COL_ENEMY_SEL     = QColor(255, 150, 50,  255)   # orange
COL_AOT_DOOR      = QColor(220, 140, 40,  180)   # orange
COL_AOT_ITEM      = QColor(200, 220, 40,  180)   # yellow-green
COL_AOT_EVENT     = QColor(80,  140, 220, 180)   # blue
COL_AOT_DEFAULT   = QColor(150, 150, 150, 140)   # grey
COL_CAM_SWITCH    = QColor(40,  200, 180, 140)   # teal
COL_BACKGROUND    = QColor(20, 22, 26)
COL_TEXT          = QColor(200, 200, 200)
COL_AXIS          = QColor(100, 100, 100, 150)

ITEM_RADIUS = 6
CAMERA_RADIUS = 8
GRID_SPACING = 500  # RE1 world units


class RoomMapEditor(QWidget): #vers 1
    """2D top-down map editor for a single RE1 room."""

    item_selected = pyqtSignal(int)       # emits item index
    camera_selected = pyqtSignal(int)     # emits camera index
    item_moved = pyqtSignal(int, int, int)  # emits item_index, new_x, new_z

    def __init__(self, parent=None): #vers 1
        super().__init__(parent)

        self.rdt: Optional[RDTFile] = None

        # View state
        self._zoom = 1.0
        self._pan = QPoint(0, 0)
        self._drag_start: Optional[QPoint] = None
        self._panning = False

        # Selection
        self._selected_item: Optional[int] = None
        self._selected_camera: Optional[int] = None
        self._dragging_item: Optional[int] = None
        self._drag_item_origin: Optional[Tuple[int, int]] = None

        # Display toggles
        self.show_grid = True
        self.show_collision = True
        self.show_cameras = True
        self.show_items = True
        self.show_camera_lines = True

        self.setMinimumSize(300, 300)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setStyleSheet("background-color: #14161a;")

    def load_rdt(self, rdt: RDTFile): #vers 1
        """Load an RDT file and reset the view."""
        self.rdt = rdt
        self._selected_item = None
        self._selected_camera = None
        self.reset_view()
        self.update()

    def reset_view(self): #vers 1
        """Fit the room into the current viewport."""
        if not self.rdt:
            self._zoom = 1.0
            self._pan = QPoint(self.width() // 2, self.height() // 2)
            self.update()
            return

        min_x, max_x, min_z, max_z = self._world_bounds()
        world_w = max(max_x - min_x, 1)
        world_h = max(max_z - min_z, 1)

        pad = 0.85
        zoom_x = (self.width()  * pad) / world_w
        zoom_y = (self.height() * pad) / world_h
        self._zoom = min(zoom_x, zoom_y)
        self._zoom = max(0.001, min(self._zoom, 10.0))

        cx = (min_x + max_x) / 2
        cz = (min_z + max_z) / 2
        sx, sz = self._room_to_screen(cx, cz)
        self._pan += QPoint(self.width() // 2 - sx, self.height() // 2 - sz)
        self.update()

    # --- Coordinate transforms ---

    def _room_to_screen(self, x: float, z: float) -> Tuple[int, int]: #vers 1
        """Convert RE1 world (X, Z) to screen pixel coords."""
        sx = int(x * self._zoom) + self._pan.x()
        sz = int(z * self._zoom) + self._pan.y()
        return sx, sz

    def _screen_to_room(self, sx: int, sy: int) -> Tuple[float, float]: #vers 1
        """Convert screen pixel to RE1 world (X, Z)."""
        x = (sx - self._pan.x()) / self._zoom
        z = (sy - self._pan.y()) / self._zoom
        return x, z

    def _world_bounds(self) -> Tuple[float, float, float, float]: #vers 1
        """Return (min_x, max_x, min_z, max_z) of all data."""
        if not self.rdt:
            return -1000, 1000, -1000, 1000

        xs, zs = [], []

        for b in self.rdt.collision:
            xs += [b.x1, b.x2]
            zs += [b.z1, b.z2]

        for item in self.rdt.items:
            xs.append(item.x)
            zs.append(item.z)

        for cam in self.rdt.cameras:
            xs += [cam.from_x, cam.to_x]
            zs += [cam.from_z, cam.to_z]

        if not xs:
            return -2000, 2000, -2000, 2000

        pad = 500
        return min(xs) - pad, max(xs) + pad, min(zs) - pad, max(zs) + pad

    # --- Drawing ---

    def paintEvent(self, event): #vers 1
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Background
        painter.fillRect(self.rect(), COL_BACKGROUND)

        if self.show_grid:
            self._draw_grid(painter)

        if not self.rdt:
            painter.setPen(QColor(100, 100, 100))
            painter.setFont(QFont("Courier New", 12))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "No RDT loaded\nOpen a .rdt file")
            return

        if self.show_collision:
            self._draw_collision(painter)

        if self.show_camera_lines:
            self._draw_camera_lines(painter)

        if self.show_cameras:
            self._draw_cameras(painter)

        if self.show_items:
            self._draw_items(painter)

        if self.show_aot:
            self._draw_aot(painter)

        if self.show_enemies:
            self._draw_enemies(painter)

        if self.show_cam_switches:
            self._draw_cam_switches(painter)

        self._draw_scale_bar(painter)
        self._draw_room_label(painter)

    def _draw_grid(self, painter: QPainter): #vers 1
        """Draw background grid in world-unit intervals."""
        pen = QPen(COL_GRID, 1, Qt.PenStyle.DotLine)
        painter.setPen(pen)

        min_x, max_x, min_z, max_z = self._world_bounds()
        step = GRID_SPACING

        # Vertical lines (X axis)
        x = (int(min_x) // step) * step
        while x <= max_x + step:
            sx, _ = self._room_to_screen(x, 0)
            if 0 <= sx <= self.width():
                painter.drawLine(sx, 0, sx, self.height())
            x += step

        # Horizontal lines (Z axis)
        z = (int(min_z) // step) * step
        while z <= max_z + step:
            _, sz = self._room_to_screen(0, z)
            if 0 <= sz <= self.height():
                painter.drawLine(0, sz, self.width(), sz)
            z += step

        # Axes
        painter.setPen(QPen(COL_AXIS, 1))
        ox, oz = self._room_to_screen(0, 0)
        painter.drawLine(0, oz, self.width(), oz)
        painter.drawLine(ox, 0, ox, self.height())

    def _draw_collision(self, painter: QPainter): #vers 1
        """Draw collision boundary rectangles."""
        if not self.rdt:
            return

        for boundary in self.rdt.collision:
            sx1, sz1 = self._room_to_screen(boundary.x1, boundary.z1)
            sx2, sz2 = self._room_to_screen(boundary.x2, boundary.z2)

            rect = QRect(min(sx1, sx2), min(sz1, sz2),
                         abs(sx2 - sx1), abs(sz2 - sz1))

            painter.setBrush(QBrush(COL_BOUNDARY_FILL))
            painter.setPen(QPen(COL_BOUNDARY, 1))
            painter.drawRect(rect)

    def _draw_camera_lines(self, painter: QPainter): #vers 1
        """Draw faint lines from camera positions to their targets."""
        if not self.rdt:
            return

        painter.setPen(QPen(COL_CAMERA_LINE, 1, Qt.PenStyle.DashLine))
        for cam in self.rdt.cameras:
            sx1, sz1 = self._room_to_screen(cam.from_x, cam.from_z)
            sx2, sz2 = self._room_to_screen(cam.to_x, cam.to_z)
            painter.drawLine(sx1, sz1, sx2, sz2)

    def _draw_cameras(self, painter: QPainter): #vers 1
        """Draw camera position markers."""
        if not self.rdt:
            return

        font = QFont("Courier New", 8)
        painter.setFont(font)

        for i, cam in enumerate(self.rdt.cameras):
            sx, sz = self._room_to_screen(cam.from_x, cam.from_z)
            selected = (i == self._selected_camera)

            color = QColor(255, 255, 100) if selected else COL_CAMERA
            painter.setPen(QPen(color, 2))
            painter.setBrush(QBrush(color.darker(180)))

            # Diamond shape for camera
            r = CAMERA_RADIUS + (2 if selected else 0)
            pts = [
                QPoint(sx,     sz - r),
                QPoint(sx + r, sz),
                QPoint(sx,     sz + r),
                QPoint(sx - r, sz),
            ]
            from PyQt6.QtGui import QPolygon
            painter.drawPolygon(QPolygon(pts))

            # Label
            painter.setPen(QPen(COL_TEXT))
            painter.drawText(sx + r + 2, sz + 4, f"C{i}")

            # Target dot
            tx, tz = self._room_to_screen(cam.to_x, cam.to_z)
            painter.setPen(QPen(COL_CAMERA_LINE, 1))
            painter.setBrush(QBrush(COL_CAMERA_LINE))
            painter.drawEllipse(QPoint(tx, tz), 3, 3)

    def _draw_items(self, painter: QPainter): #vers 1
        """Draw item placement markers."""
        if not self.rdt:
            return

        font = QFont("Courier New", 7)
        painter.setFont(font)

        for i, item in enumerate(self.rdt.items):
            sx, sz = self._room_to_screen(item.x, item.z)
            selected = (i == self._selected_item)

            color = COL_ITEM_SEL if selected else COL_ITEM
            painter.setPen(QPen(color, 2))
            painter.setBrush(QBrush(color.darker(200)))

            r = ITEM_RADIUS + (2 if selected else 0)
            painter.drawEllipse(QPoint(sx, sz), r, r)

            # Label
            painter.setPen(QPen(COL_TEXT))
            name = get_item_name(item.item_type)
            short = name[:12] + ".." if len(name) > 12 else name
            painter.drawText(sx + r + 2, sz + 4, short)

    def _draw_enemies(self, painter: QPainter): #vers 1
        """Draw enemy positions as red skull markers."""
        if not self.rdt or not self.rdt.enemies:
            return
        from apps.core.re1_formats import get_enemy_name
        from apps.core.re_room_names import get_game_from_room_id
        game = get_game_from_room_id(self.rdt.room_id)

        for i, enemy in enumerate(self.rdt.enemies):
            sx, sz = self._room_to_screen(enemy.x, enemy.z)
            selected = (i == self._selected_enemy)
            color = COL_ENEMY_SEL if selected else COL_ENEMY
            r = 8 + (2 if selected else 0)

            # Draw as X marker
            painter.setPen(QPen(color, 2))
            painter.drawLine(sx-r, sz-r, sx+r, sz+r)
            painter.drawLine(sx+r, sz-r, sx-r, sz+r)

            # Outer circle
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(QPoint(sx, sz), r, r)

            # Label
            if self._zoom >= 0.04:
                name = get_enemy_name(enemy.enemy_type, game)
                short = name[:12] + '..' if len(name) > 12 else name
                painter.setFont(QFont("Courier New", max(6, int(7*self._zoom))))
                painter.setPen(QPen(color))
                painter.drawText(sx + r + 2, sz + 4, short)

    def _draw_aot(self, painter: QPainter): #vers 1
        """Draw AOT trigger zones as dashed rectangles."""
        if not self.rdt or not self.rdt.aot:
            return
        for i, aot in enumerate(self.rdt.aot):
            if aot.aot_type == 0:
                continue
            # Colour by type
            if aot.is_door:
                color = COL_AOT_DOOR
                label = "Door"
            elif aot.is_item:
                color = COL_AOT_ITEM
                label = "Item"
            elif aot.is_event:
                color = COL_AOT_EVENT
                label = "Event"
            else:
                color = COL_AOT_DEFAULT
                label = f"AOT{aot.aot_type}"

            sx1, sz1 = self._room_to_screen(aot.x1, aot.z1)
            sx2, sz2 = self._room_to_screen(aot.x2, aot.z2)
            rect = QRect(min(sx1,sx2), min(sz1,sz2),
                         abs(sx2-sx1), abs(sz2-sz1))
            if rect.width() < 2 or rect.height() < 2:
                continue

            # Dashed outline
            painter.setBrush(QBrush(QColor(color.red(), color.green(),
                                           color.blue(), 40)))
            painter.setPen(QPen(color, 1, Qt.PenStyle.DashLine))
            painter.drawRect(rect)

            # Label in centre
            if self._zoom >= 0.04 and rect.width() > 20:
                painter.setFont(QFont("Courier New", max(6, int(6*self._zoom))))
                painter.setPen(QPen(color))
                painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, label)

    def _draw_cam_switches(self, painter: QPainter): #vers 1
        """Draw camera switch zones as teal dashed rectangles."""
        if not self.rdt or not self.rdt.camera_switches:
            return
        for cs in self.rdt.camera_switches:
            sx1, sz1 = self._room_to_screen(cs.x1, cs.z1)
            sx2, sz2 = self._room_to_screen(cs.x2, cs.z2)
            rect = QRect(min(sx1,sx2), min(sz1,sz2),
                         abs(sx2-sx1), abs(sz2-sz1))
            if rect.width() < 2:
                continue
            painter.setBrush(QBrush(QColor(40, 200, 180, 30)))
            painter.setPen(QPen(COL_CAM_SWITCH, 1, Qt.PenStyle.DotLine))
            painter.drawRect(rect)
            if self._zoom >= 0.04 and rect.width() > 20:
                painter.setFont(QFont("Courier New", max(5, int(6*self._zoom))))
                painter.setPen(QPen(COL_CAM_SWITCH))
                painter.drawText(rect, Qt.AlignmentFlag.AlignCenter,
                                 f"C{cs.from_cam}→C{cs.to_cam}")

    def _draw_scale_bar(self, painter: QPainter): #vers 1
        """Draw a scale bar in the bottom-left corner."""
        bar_world = 1000  # 1000 RE units
        bar_px = int(bar_world * self._zoom)

        if bar_px < 10:
            return

        x, y = 16, self.height() - 24
        painter.setPen(QPen(COL_TEXT, 2))
        painter.drawLine(x, y, x + bar_px, y)
        painter.drawLine(x, y - 4, x, y + 4)
        painter.drawLine(x + bar_px, y - 4, x + bar_px, y + 4)

        painter.setFont(QFont("Courier New", 8))
        painter.drawText(x, y - 6, f"{bar_world} units")

    def _draw_room_label(self, painter: QPainter): #vers 1
        """Draw room ID in top-left corner."""
        if not self.rdt:
            return
        painter.setPen(QPen(COL_TEXT))
        painter.setFont(QFont("Courier New", 9))
        painter.drawText(8, 16, self.rdt.room_id)
        painter.setFont(QFont("Courier New", 8))
        cam_count = len(self.rdt.cameras)
        item_count = len(self.rdt.items)
        col_count = len(self.rdt.collision)
        painter.drawText(8, 30, f"Cams:{cam_count}  Items:{item_count}  Col:{col_count}")

    # --- Selection ---

    def _find_enemy_at(self, sx: int, sy: int) -> Optional[int]: #vers 1
        """Return enemy index under screen position."""
        if not self.rdt:
            return None
        for i, enemy in enumerate(self.rdt.enemies):
            ex, ez = self._room_to_screen(enemy.x, enemy.z)
            if abs(sx - ex) <= 10 and abs(sy - ez) <= 10:
                return i
        return None

    def _find_item_at(self, sx: int, sy: int) -> Optional[int]: #vers 1
        """Return item index under screen position, or None."""
        if not self.rdt:
            return None
        for i, item in enumerate(self.rdt.items):
            ix, iz = self._room_to_screen(item.x, item.z)
            if abs(sx - ix) <= ITEM_RADIUS + 4 and abs(sy - iz) <= ITEM_RADIUS + 4:
                return i
        return None

    def _find_camera_at(self, sx: int, sy: int) -> Optional[int]: #vers 1
        """Return camera index under screen position, or None."""
        if not self.rdt:
            return None
        for i, cam in enumerate(self.rdt.cameras):
            cx, cz = self._room_to_screen(cam.from_x, cam.from_z)
            if abs(sx - cx) <= CAMERA_RADIUS + 4 and abs(sy - cz) <= CAMERA_RADIUS + 4:
                return i
        return None

    # --- Mouse events ---

    def mousePressEvent(self, event: QMouseEvent): #vers 1
        pos = event.pos()

        if event.button() == Qt.MouseButton.LeftButton:
            # Check items first
            item_idx = self._find_item_at(pos.x(), pos.y())
            if item_idx is not None:
                self._selected_item = item_idx
                self._selected_camera = None
                self._dragging_item = item_idx
                self._drag_item_origin = self._screen_to_room(pos.x(), pos.y())
                self.item_selected.emit(item_idx)
                self.update()
                return

            # Check cameras
            cam_idx = self._find_camera_at(pos.x(), pos.y())
            if cam_idx is not None:
                self._selected_camera = cam_idx
                self._selected_item = None
                self.camera_selected.emit(cam_idx)
                self.update()
                return

            # Pan
            self._panning = True
            self._drag_start = pos
            self._selected_item = None
            self._selected_camera = None
            self.update()

        elif event.button() == Qt.MouseButton.MiddleButton:
            self._panning = True
            self._drag_start = pos

    def mouseMoveEvent(self, event: QMouseEvent): #vers 1
        pos = event.pos()

        if self._panning and self._drag_start:
            delta = pos - self._drag_start
            self._pan += delta
            self._drag_start = pos
            self.update()
            return

        if self._dragging_item is not None and self.rdt:
            wx, wz = self._screen_to_room(pos.x(), pos.y())
            item = self.rdt.items[self._dragging_item]
            item.x = int(wx)
            item.z = int(wz)
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent): #vers 1
        if event.button() in (Qt.MouseButton.LeftButton, Qt.MouseButton.MiddleButton):
            if self._dragging_item is not None and self.rdt:
                item = self.rdt.items[self._dragging_item]
                self.item_moved.emit(self._dragging_item, item.x, item.z)
            self._panning = False
            self._drag_start = None
            self._dragging_item = None
            self._drag_item_origin = None

    def wheelEvent(self, event: QWheelEvent): #vers 1
        """Zoom in/out centered on mouse cursor."""
        pos = event.position().toPoint()
        wx, wz = self._screen_to_room(pos.x(), pos.y())

        delta = event.angleDelta().y()
        factor = 1.15 if delta > 0 else (1.0 / 1.15)
        self._zoom = max(0.001, min(self._zoom * factor, 20.0))

        # Keep world point under cursor
        sx, sz = self._room_to_screen(wx, wz)
        self._pan += QPoint(pos.x() - sx, pos.y() - sz)
        self.update()

    def keyPressEvent(self, event: QKeyEvent): #vers 1
        """Keyboard shortcuts for map editor."""
        key = event.key()
        if key == Qt.Key.Key_Home or key == Qt.Key.Key_F:
            self.reset_view()
        elif key == Qt.Key.Key_G:
            self.show_grid = not self.show_grid
            self.update()
        elif key == Qt.Key.Key_C:
            self.show_cameras = not self.show_cameras
            self.show_camera_lines = self.show_cameras
            self.update()
        elif key == Qt.Key.Key_I:
            self.show_items = not self.show_items
            self.update()
        elif key == Qt.Key.Key_B:
            self.show_collision = not self.show_collision
            self.update()
        else:
            super().keyPressEvent(event)


class RoomMapToolbar(QFrame): #vers 1
    """Toolbar strip for the room map editor."""

    def __init__(self, map_editor: RoomMapEditor, parent=None): #vers 1
        super().__init__(parent)
        self.map_editor = map_editor
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setMaximumHeight(36)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(4)

        self._add_btn("Fit [Home]",    self.map_editor.reset_view)
        self._add_toggle("Grid [G]",   lambda: self._toggle('show_grid'))
        self._add_toggle("Col [B]",     lambda: self._toggle('show_collision'))
        self._add_toggle("Cams [C]",    lambda: self._toggle_cameras())
        self._add_toggle("Items [I]",   lambda: self._toggle('show_items'))
        self._add_toggle("Enemies [E]", lambda: self._toggle('show_enemies'))
        self._add_toggle("Triggers [T]",lambda: self._toggle('show_aot'))
        self._add_toggle("CamZones [Z]",lambda: self._toggle('show_cam_switches'))

        layout.addStretch()

        self.coord_label = QLabel("X: 0  Z: 0")
        self.coord_label.setFont(QFont("Courier New", 8))
        layout.addWidget(self.coord_label)

        # Connect mouse move to coord display
        self.map_editor.setMouseTracking(True)
        self.map_editor.mouseMoveEvent = self._wrapped_mouse_move(self.map_editor.mouseMoveEvent)

    def _add_btn(self, text: str, slot): #vers 1
        btn = QPushButton(text)
        btn.setMaximumHeight(24)
        btn.clicked.connect(slot)
        self.layout().addWidget(btn)

    def _add_toggle(self, text: str, slot): #vers 1
        btn = QPushButton(text)
        btn.setMaximumHeight(24)
        btn.setCheckable(True)
        btn.setChecked(True)
        btn.clicked.connect(slot)
        self.layout().addWidget(btn)

    def _toggle(self, attr: str): #vers 1
        val = getattr(self.map_editor, attr, False)
        setattr(self.map_editor, attr, not val)
        self.map_editor.update()

    def _toggle_cameras(self): #vers 1
        self.map_editor.show_cameras = not self.map_editor.show_cameras
        self.map_editor.show_camera_lines = self.map_editor.show_cameras
        self.map_editor.update()

    def _wrapped_mouse_move(self, original_fn): #vers 1
        """Wrap mouse move to also update coordinate label."""
        def wrapper(event: QMouseEvent):
            original_fn(event)
            pos = event.pos()
            wx, wz = self.map_editor._screen_to_room(pos.x(), pos.y())
            self.coord_label.setText(f"X: {int(wx):6d}  Z: {int(wz):6d}")
        return wrapper


class RoomMapWidget(QWidget): #vers 1
    """Combined map editor + toolbar widget for embedding in the main window."""

    item_selected = pyqtSignal(int)
    camera_selected = pyqtSignal(int)
    item_moved = pyqtSignal(int, int, int)

    def __init__(self, parent=None): #vers 1
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.map_editor = RoomMapEditor(self)
        self.toolbar = RoomMapToolbar(self.map_editor, self)

        layout.addWidget(self.toolbar)
        layout.addWidget(self.map_editor, stretch=1)

        self.map_editor.item_selected.connect(self.item_selected)
        self.map_editor.camera_selected.connect(self.camera_selected)
        self.map_editor.item_moved.connect(self.item_moved)

    def load_rdt(self, rdt: RDTFile): #vers 1
        self.map_editor.load_rdt(rdt)

    def reset_view(self): #vers 1
        self.map_editor.reset_view()
