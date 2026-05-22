#!/usr/bin/env python3
#this belongs in apps/gui/floor_plan.py - Version: 1
# X-Seti - May22 2026 - ResBio-Evil-Workshop - Floor Plan Viewer
"""
Floor Plan Viewer - Renders an in-game style top-down floor map.
Green filled rectangles = walkable floor (from SCA collision data).
Black = walls/obstacles. Orange markers = doors. Yellow = items.
Diamond = camera positions. Matches the style of the RE1 in-game map.

Can show a single room or a full stage (all loaded RDTs composited).
Click a room area to load that room. Click an item marker to inspect it.
"""

from typing import Optional, List, Dict, Tuple, TYPE_CHECKING
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFrame, QCheckBox, QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt, QPoint, QRect, QRectF, pyqtSignal
from PyQt6.QtGui import (
    QPainter, QPen, QBrush, QColor, QFont, QFontMetrics,
    QWheelEvent, QMouseEvent, QKeyEvent, QImage, QPixmap
)

from apps.core.re1_formats import RDTFile, RDTCollisionBoundary, RDTItem, get_item_name

if TYPE_CHECKING:
    pass

##Methods list -
# _draw_cameras
# _draw_doors
# _draw_floor_label
# _draw_floors
# _draw_grid
# _draw_items
# _draw_scale_bar
# _draw_stairs
# _find_item_at
# _find_room_at
# _room_to_screen
# _screen_to_room
# _world_bounds
# keyPressEvent
# load_rdt
# load_stage
# mouseMoveEvent
# mousePressEvent
# mouseReleaseEvent
# paintEvent
# reset_view
# wheelEvent

##class BoundaryClass:
##class FloorPlanCanvas:
##class FloorPlanToolbar:
##class FloorPlanWidget:


# --- Boundary classification using SCA counts ---
# SCA counts[5]: floors(0), slopes(1), walls(2), doors(3), other(4)

class BoundaryClass:
    FLOOR  = 0
    SLOPE  = 1
    WALL   = 2
    DOOR   = 3
    OTHER  = 4

def classify_boundaries(boundaries: List[RDTCollisionBoundary],
                         counts: List[int]) -> List[int]: #vers 1
    """Return a list of BoundaryClass int per boundary, using SCA counts."""
    result = []
    if not counts or sum(counts) == 0:
        # No count data - guess from boundary_type low nibble
        for b in boundaries:
            t = b.boundary_type & 0x0F
            if t == 0:
                result.append(BoundaryClass.FLOOR)
            elif t in (1, 2):
                result.append(BoundaryClass.SLOPE)
            elif t == 3:
                result.append(BoundaryClass.DOOR)
            elif t >= 0x08:
                result.append(BoundaryClass.WALL)
            else:
                result.append(BoundaryClass.OTHER)
        return result

    idx = 0
    for cat, count in enumerate(counts[:5]):
        for _ in range(count):
            result.append(cat)
            idx += 1
    # Any overflow
    while len(result) < len(boundaries):
        result.append(BoundaryClass.OTHER)
    return result


# --- Color scheme matching RE1 in-game map ---
COL_BG          = QColor(0,   0,   0)       # black background
COL_FLOOR       = QColor(0,   160, 0)       # green floor
COL_FLOOR_SEL   = QColor(0,   200, 40)      # selected room floor
COL_SLOPE       = QColor(0,   120, 20)      # darker green for stairs
COL_WALL        = QColor(20,  20,  20)      # near-black walls (implied)
COL_DOOR        = QColor(220, 160, 0)       # orange door markers
COL_ITEM        = QColor(255, 220, 50)      # yellow item markers
COL_ITEM_SEL    = QColor(255, 100, 100)     # selected item
COL_CAMERA      = QColor(180, 180, 255)     # pale blue camera diamonds
COL_GRID        = QColor(15,  30,  15)      # very faint green grid
COL_TEXT        = QColor(200, 200, 200)
COL_LABEL       = QColor(160, 200, 160)
COL_FLOOR_LABEL = QColor(200, 200, 200)

DOOR_W   = 6    # door marker width in world units scaled
ITEM_R   = 5    # item dot radius px
CAM_R    = 5    # camera diamond half-size px


class FloorPlanCanvas(QWidget): #vers 1
    """Renders the in-game style floor plan from collision data."""

    item_clicked   = pyqtSignal(int)          # item index in current rdt
    camera_clicked = pyqtSignal(int)          # camera index
    room_clicked   = pyqtSignal(str)          # room_id (stage mode)

    def __init__(self, parent=None): #vers 1
        super().__init__(parent)
        self._rdts: List[Tuple[str, RDTFile]] = []   # (room_id, rdt) pairs
        self._selected_room: Optional[str] = None
        self._selected_item: Optional[int] = None
        self._zoom = 1.0
        self._pan = QPoint(40, 40)
        self._drag_start: Optional[QPoint] = None
        self._panning = False

        # Display toggles
        self.show_floors   = True
        self.show_slopes   = True
        self.show_doors    = True
        self.show_items    = True
        self.show_cameras  = True
        self.show_grid     = False
        self.show_labels   = True

        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setStyleSheet("background-color: #000000;")
        self.setMinimumSize(300, 300)

    def load_rdt(self, rdt: RDTFile, room_id: str = ''): #vers 1
        """Show a single room."""
        rid = room_id or rdt.room_id
        self._rdts = [(rid, rdt)]
        self._selected_room = rid
        self._selected_item = None
        self.reset_view()
        self.update()

    def load_stage(self, rdts: List[Tuple[str, RDTFile]]): #vers 1
        """Show all rooms in a stage composited together."""
        self._rdts = rdts
        self._selected_room = None
        self._selected_item = None
        self.reset_view()
        self.update()

    def reset_view(self): #vers 1
        min_x, max_x, min_z, max_z = self._world_bounds()
        if max_x == min_x:
            self._zoom = 1.0
            self._pan = QPoint(self.width() // 2, self.height() // 2)
            self.update()
            return
        pad = 0.88
        self._zoom = min(
            self.width()  * pad / max(max_x - min_x, 1),
            self.height() * pad / max(max_z - min_z, 1),
        )
        self._zoom = max(0.002, min(self._zoom, 8.0))
        cx = (min_x + max_x) / 2
        cz = (min_z + max_z) / 2
        self._pan = QPoint(
            int(self.width()  / 2 - cx * self._zoom),
            int(self.height() / 2 - cz * self._zoom),
        )
        self.update()

    # --- Coordinates ---

    def _room_to_screen(self, x: float, z: float) -> Tuple[int, int]: #vers 1
        return int(x * self._zoom) + self._pan.x(), int(z * self._zoom) + self._pan.y()

    def _screen_to_room(self, sx: int, sy: int) -> Tuple[float, float]: #vers 1
        return (sx - self._pan.x()) / self._zoom, (sy - self._pan.y()) / self._zoom

    def _world_bounds(self) -> Tuple[float, float, float, float]: #vers 1
        xs, zs = [], []
        for _, rdt in self._rdts:
            for b in rdt.collision:
                xs += [b.x1, b.x2]
                zs += [b.z1, b.z2]
            for item in rdt.items:
                xs.append(item.x); zs.append(item.z)
        if not xs:
            return -2000, 2000, -2000, 2000
        pad = 400
        return min(xs)-pad, max(xs)+pad, min(zs)-pad, max(zs)+pad

    # --- Paint ---

    def paintEvent(self, event): #vers 1
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), COL_BG)

        if not self._rdts:
            painter.setPen(QColor(50, 80, 50))
            painter.setFont(QFont("Courier New", 11))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter,
                             "No room loaded\n\nOpen an RDT file or load a stage folder")
            return

        if self.show_grid:
            self._draw_grid(painter)

        for room_id, rdt in self._rdts:
            selected = (room_id == self._selected_room)
            self._draw_room(painter, room_id, rdt, selected)

        self._draw_scale_bar(painter)

        if self.show_labels and len(self._rdts) > 1:
            for room_id, rdt in self._rdts:
                self._draw_floor_label(painter, room_id, rdt)

    def _draw_grid(self, painter: QPainter): #vers 1
        step = max(1, int(500 * self._zoom))
        if step < 4:
            return
        painter.setPen(QPen(COL_GRID, 1))
        min_x, max_x, min_z, max_z = self._world_bounds()
        x = (int(min_x) // 500) * 500
        while x <= max_x:
            sx, _ = self._room_to_screen(x, 0)
            if 0 <= sx <= self.width():
                painter.drawLine(sx, 0, sx, self.height())
            x += 500
        z = (int(min_z) // 500) * 500
        while z <= max_z:
            _, sz = self._room_to_screen(0, z)
            if 0 <= sz <= self.height():
                painter.drawLine(0, sz, self.width(), sz)
            z += 500

    def _draw_room(self, painter: QPainter, room_id: str,
                   rdt: RDTFile, selected: bool): #vers 1
        classes = classify_boundaries(rdt.collision, rdt.sca_counts)

        # Draw floors first (filled green rects)
        if self.show_floors:
            self._draw_floors(painter, rdt, classes, selected)

        # Stairs/slopes (darker green, hatched)
        if self.show_slopes:
            self._draw_stairs(painter, rdt, classes)

        # Door markers (orange rectangles on room edges)
        if self.show_doors:
            self._draw_doors(painter, rdt, classes)

        # Items
        if self.show_items:
            self._draw_items(painter, rdt)

        # Cameras
        if self.show_cameras:
            self._draw_cameras(painter, rdt)

    def _draw_floors(self, painter: QPainter, rdt: RDTFile,
                     classes: List[int], selected: bool): #vers 1
        fill = COL_FLOOR_SEL if selected else COL_FLOOR
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(fill))

        for b, cls in zip(rdt.collision, classes):
            if cls != BoundaryClass.FLOOR:
                continue
            sx1, sz1 = self._room_to_screen(b.x1, b.z1)
            sx2, sz2 = self._room_to_screen(b.x2, b.z2)
            rect = QRect(min(sx1,sx2), min(sz1,sz2),
                         abs(sx2-sx1), abs(sz2-sz1))
            if rect.width() < 1 or rect.height() < 1:
                continue
            painter.drawRect(rect)

    def _draw_stairs(self, painter: QPainter, rdt: RDTFile,
                     classes: List[int]): #vers 1
        painter.setPen(QPen(COL_SLOPE.darker(120), 1))
        painter.setBrush(QBrush(COL_SLOPE))

        for b, cls in zip(rdt.collision, classes):
            if cls != BoundaryClass.SLOPE:
                continue
            sx1, sz1 = self._room_to_screen(b.x1, b.z1)
            sx2, sz2 = self._room_to_screen(b.x2, b.z2)
            rect = QRect(min(sx1,sx2), min(sz1,sz2),
                         abs(sx2-sx1), abs(sz2-sz1))
            if rect.width() < 1 or rect.height() < 1:
                continue
            painter.drawRect(rect)
            # Draw stair lines inside
            if self._zoom > 0.03:
                painter.setPen(QPen(COL_SLOPE.darker(160), 1))
                step_px = max(3, int(80 * self._zoom))
                y = rect.top() + step_px
                while y < rect.bottom():
                    painter.drawLine(rect.left(), y, rect.right(), y)
                    y += step_px
                painter.setPen(QPen(COL_SLOPE.darker(120), 1))

    def _draw_doors(self, painter: QPainter, rdt: RDTFile,
                    classes: List[int]): #vers 1
        """Draw door markers as small orange rectangles, matching RE1 in-game style."""
        door_size = max(3, int(DOOR_W * self._zoom))

        for b, cls in zip(rdt.collision, classes):
            if cls != BoundaryClass.DOOR:
                continue
            sx1, sz1 = self._room_to_screen(b.x1, b.z1)
            sx2, sz2 = self._room_to_screen(b.x2, b.z2)
            cx = (sx1 + sx2) // 2
            cz = (sz1 + sz2) // 2
            w  = abs(sx2 - sx1)
            h  = abs(sz2 - sz1)

            painter.setBrush(QBrush(COL_DOOR))
            painter.setPen(Qt.PenStyle.NoPen)

            # Door marker: short fat rect on the narrower axis
            if w >= h:
                rect = QRect(cx - door_size*2, cz - door_size,
                             door_size*4, door_size*2)
            else:
                rect = QRect(cx - door_size, cz - door_size*2,
                             door_size*2, door_size*4)
            painter.drawRect(rect)

    def _draw_items(self, painter: QPainter, rdt: RDTFile): #vers 1
        painter.setFont(QFont("Courier New", max(6, int(7 * self._zoom))))
        for i, item in enumerate(rdt.items):
            sx, sz = self._room_to_screen(item.x, item.z)
            selected = (i == self._selected_item)
            color = COL_ITEM_SEL if selected else COL_ITEM
            r = ITEM_R + (2 if selected else 0)
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(color.darker(150), 1))
            painter.drawEllipse(QPoint(sx, sz), r, r)

            if self._zoom >= 0.08 and self.show_labels:
                name = get_item_name(item.item_type)
                short = name[:10] + ".." if len(name) > 10 else name
                painter.setPen(QPen(COL_TEXT))
                painter.drawText(sx + r + 2, sz + 4, short)

    def _draw_cameras(self, painter: QPainter, rdt: RDTFile): #vers 1
        for i, cam in enumerate(rdt.cameras):
            sx, sz = self._room_to_screen(cam.from_x, cam.from_z)
            r = max(3, int(CAM_R * self._zoom))
            painter.setBrush(QBrush(COL_CAMERA))
            painter.setPen(QPen(COL_CAMERA.darker(150), 1))
            # Diamond
            from PyQt6.QtGui import QPolygon
            pts = [QPoint(sx, sz-r), QPoint(sx+r, sz),
                   QPoint(sx, sz+r), QPoint(sx-r, sz)]
            painter.drawPolygon(QPolygon(pts))

            if self._zoom >= 0.1 and self.show_labels:
                painter.setPen(QPen(COL_CAMERA))
                painter.setFont(QFont("Courier New", max(5, int(6*self._zoom))))
                painter.drawText(sx+r+1, sz+3, f"C{i}")

    def _draw_floor_label(self, painter: QPainter,
                          room_id: str, rdt: RDTFile): #vers 1
        """Draw room name label near its centroid."""
        if not rdt.collision:
            return
        xs = [b.x1 for b in rdt.collision] + [b.x2 for b in rdt.collision]
        zs = [b.z1 for b in rdt.collision] + [b.z2 for b in rdt.collision]
        cx = sum(xs) / len(xs)
        cz = sum(zs) / len(zs)
        sx, sz = self._room_to_screen(cx, cz)
        painter.setPen(QPen(COL_LABEL))
        painter.setFont(QFont("Courier New", max(6, int(8 * self._zoom))))
        painter.drawText(sx - 20, sz, room_id)

    def _draw_scale_bar(self, painter: QPainter): #vers 1
        bar_world = 1000
        bar_px = int(bar_world * self._zoom)
        if bar_px < 8:
            return
        x, y = 12, self.height() - 20
        painter.setPen(QPen(QColor(100, 160, 100), 2))
        painter.drawLine(x, y, x + bar_px, y)
        painter.drawLine(x, y-3, x, y+3)
        painter.drawLine(x+bar_px, y-3, x+bar_px, y+3)
        painter.setFont(QFont("Courier New", 8))
        painter.setPen(QPen(COL_TEXT_DIM := QColor(140, 160, 140)))
        painter.drawText(x, y - 4, f"{bar_world} units")

    # --- Hit testing ---

    def _find_item_at(self, sx: int, sy: int) -> Tuple[Optional[int], Optional[str]]: #vers 1
        """Return (item_index, room_id) for item under screen pos."""
        for room_id, rdt in self._rdts:
            for i, item in enumerate(rdt.items):
                ix, iz = self._room_to_screen(item.x, item.z)
                if abs(sx - ix) <= ITEM_R + 4 and abs(sy - iz) <= ITEM_R + 4:
                    return i, room_id
        return None, None

    def _find_room_at(self, sx: int, sy: int) -> Optional[str]: #vers 1
        """Return room_id of room whose floor boundary contains screen pos."""
        for room_id, rdt in self._rdts:
            classes = classify_boundaries(rdt.collision, rdt.sca_counts)
            for b, cls in zip(rdt.collision, classes):
                if cls != BoundaryClass.FLOOR:
                    continue
                bsx1, bsz1 = self._room_to_screen(b.x1, b.z1)
                bsx2, bsz2 = self._room_to_screen(b.x2, b.z2)
                r = QRect(min(bsx1,bsx2), min(bsz1,bsz2),
                          abs(bsx2-bsx1), abs(bsz2-bsz1))
                if r.contains(QPoint(sx, sy)):
                    return room_id
        return None

    # --- Mouse ---

    def mousePressEvent(self, event: QMouseEvent): #vers 1
        pos = event.pos()
        if event.button() == Qt.MouseButton.LeftButton:
            # Item hit test first
            item_idx, room_id = self._find_item_at(pos.x(), pos.y())
            if item_idx is not None:
                self._selected_item = item_idx
                self.item_clicked.emit(item_idx)
                self.update()
                return
            # Room floor hit
            room_id = self._find_room_at(pos.x(), pos.y())
            if room_id and room_id != self._selected_room:
                self._selected_room = room_id
                self._selected_item = None
                self.room_clicked.emit(room_id)
                self.update()
                return
            # Pan
            self._panning = True
            self._drag_start = pos
            self._selected_item = None

        elif event.button() == Qt.MouseButton.MiddleButton:
            self._panning = True
            self._drag_start = pos

    def mouseMoveEvent(self, event: QMouseEvent): #vers 1
        if self._panning and self._drag_start:
            self._pan += event.pos() - self._drag_start
            self._drag_start = event.pos()
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent): #vers 1
        self._panning = False
        self._drag_start = None

    def wheelEvent(self, event: QWheelEvent): #vers 1
        pos = event.position().toPoint()
        wx, wz = self._screen_to_room(pos.x(), pos.y())
        factor = 1.15 if event.angleDelta().y() > 0 else (1.0 / 1.15)
        self._zoom = max(0.002, min(self._zoom * factor, 16.0))
        sx, sz = self._room_to_screen(wx, wz)
        self._pan += QPoint(pos.x() - sx, pos.y() - sz)
        self.update()

    def keyPressEvent(self, event: QKeyEvent): #vers 1
        k = event.key()
        if k in (Qt.Key.Key_Home, Qt.Key.Key_F):
            self.reset_view()
        elif k == Qt.Key.Key_G:
            self.show_grid = not self.show_grid; self.update()
        elif k == Qt.Key.Key_L:
            self.show_labels = not self.show_labels; self.update()
        elif k == Qt.Key.Key_I:
            self.show_items = not self.show_items; self.update()
        elif k == Qt.Key.Key_D:
            self.show_doors = not self.show_doors; self.update()
        elif k == Qt.Key.Key_C:
            self.show_cameras = not self.show_cameras; self.update()
        else:
            super().keyPressEvent(event)


class FloorPlanToolbar(QFrame): #vers 1

    def __init__(self, canvas: FloorPlanCanvas, parent=None): #vers 1
        super().__init__(parent)
        self.canvas = canvas
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setMaximumHeight(34)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(6)

        fit_btn = QPushButton("Fit [F]")
        fit_btn.setMaximumHeight(26)
        fit_btn.clicked.connect(canvas.reset_view)
        layout.addWidget(fit_btn)

        for label, attr, key in [
            ("Floors", "show_floors", ""),
            ("Stairs", "show_slopes", ""),
            ("Doors [D]", "show_doors", ""),
            ("Items [I]", "show_items", ""),
            ("Cams [C]", "show_cameras", ""),
            ("Labels [L]", "show_labels", ""),
            ("Grid [G]", "show_grid", ""),
        ]:
            cb = QCheckBox(label)
            cb.setChecked(getattr(canvas, attr))
            cb.toggled.connect(lambda v, a=attr: (setattr(canvas, a, v), canvas.update()))
            layout.addWidget(cb)

        layout.addStretch()

        self._info = QLabel("")
        self._info.setFont(QFont("Courier New", 8))
        layout.addWidget(self._info)

        canvas.room_clicked.connect(
            lambda rid: self._info.setText(f"Room: {rid}"))
        canvas.item_clicked.connect(
            lambda idx: self._info.setText(f"Item #{idx}"))


class FloorPlanWidget(QWidget): #vers 2
    """Combined floor plan canvas + toolbar. Embeds in display stack."""

    room_clicked = pyqtSignal(str)    # room_id clicked on floor
    item_clicked = pyqtSignal(int)    # item index clicked

    def __init__(self, parent=None): #vers 1
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.canvas = FloorPlanCanvas(self)
        self.toolbar = FloorPlanToolbar(self.canvas, self)

        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas, stretch=1)

        self.canvas.room_clicked.connect(self.room_clicked)
        self.canvas.item_clicked.connect(self.item_clicked)

    def load_rdt(self, rdt: RDTFile, room_id: str = ''): #vers 1
        self.canvas.load_rdt(rdt, room_id)

    def load_stage(self, rdts: List[Tuple[str, RDTFile]]): #vers 1
        self.canvas.load_stage(rdts)

    def reset_view(self): #vers 1
        self.canvas.reset_view()
