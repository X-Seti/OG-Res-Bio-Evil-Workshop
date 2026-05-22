#!/usr/bin/env python3
#this belongs in apps/gui/stage_map_editor.py - Version: 1
# X-Seti - May22 2026 - ResBio-Evil-Workshop - Stage Map Editor
"""
Stage Map Editor - Visual canvas showing all rooms in a stage as boxes
with connection arrows. Click to load a room. Drag to reposition.
Right-click for room actions: open, swap, remove.
"""

import os
from typing import Optional, Dict, Tuple, TYPE_CHECKING
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFrame, QMenu, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, QPoint, QRect, pyqtSignal
from PyQt6.QtGui import (
    QPainter, QPen, QBrush, QColor, QFont,
    QWheelEvent, QMouseEvent, QKeyEvent
)

from apps.core.re1_room_map import StageGraph, RoomNode, scan_stage_folder, swap_rooms, remove_room

if TYPE_CHECKING:
    from apps.components.ResBio_Evil_Workshop.ResBio_Evil_Workshop import ResBioEvilWorkshop

##Methods list -
# _draw_connections
# _draw_room_box
# _find_room_at
# _room_rect
# keyPressEvent
# load_folder
# mouseMoveEvent
# mousePressEvent
# mouseReleaseEvent
# paintEvent
# reset_view
# wheelEvent

##class StageMapCanvas:
##class StageMapToolbar:
##class StageMapWidget:


# Colors
COL_BG          = QColor(18, 20, 24)
COL_ROOM        = QColor(40, 55, 75)
COL_ROOM_BORDER = QColor(80, 130, 200)
COL_ROOM_SEL    = QColor(60, 100, 160)
COL_ROOM_SEL_BORDER = QColor(120, 200, 255)
COL_CONN_LINE   = QColor(100, 180, 100, 180)
COL_CONN_ARR    = QColor(100, 220, 100, 220)
COL_TEXT        = QColor(200, 210, 220)
COL_TEXT_DIM    = QColor(120, 130, 140)
COL_GRID        = QColor(35, 38, 44)

ROOM_W = 110
ROOM_H = 60


class StageMapCanvas(QWidget): #vers 1
    """QPainter canvas drawing a StageGraph as room boxes with arrows."""

    room_clicked    = pyqtSignal(str)   # room_id
    room_activated  = pyqtSignal(str)   # double-click: load the room

    def __init__(self, parent=None): #vers 1
        super().__init__(parent)
        self.graph: Optional[StageGraph] = None
        self._zoom = 1.0
        self._pan = QPoint(40, 40)
        self._drag_start: Optional[QPoint] = None
        self._drag_room: Optional[str] = None
        self._selected_room: Optional[str] = None
        self._panning = False
        self._swap_pending: Optional[str] = None  # first room in swap operation

        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setStyleSheet("background-color: #12141a;")
        self.setMinimumSize(300, 300)

    def load_graph(self, graph: StageGraph): #vers 1
        self.graph = graph
        self._selected_room = None
        self._swap_pending = None
        self.reset_view()
        self.update()

    def reset_view(self): #vers 1
        """Fit all rooms into view."""
        if not self.graph or not self.graph.rooms:
            self._zoom = 1.0
            self._pan = QPoint(40, 40)
            self.update()
            return

        positions = [n.position for n in self.graph.rooms.values()]
        min_x = min(p[0] for p in positions)
        min_y = min(p[1] for p in positions)
        max_x = max(p[0] for p in positions) + ROOM_W
        max_y = max(p[1] for p in positions) + ROOM_H

        w = max_x - min_x + 80
        h = max_y - min_y + 80
        zoom_x = self.width()  / max(w, 1)
        zoom_y = self.height() / max(h, 1)
        self._zoom = max(0.1, min(zoom_x, zoom_y, 2.0))

        cx = (min_x + max_x) / 2
        cy = (min_y + max_y) / 2
        sx = int(cx * self._zoom)
        sy = int(cy * self._zoom)
        self._pan = QPoint(self.width() // 2 - sx, self.height() // 2 - sy)
        self.update()

    # --- Coordinate helpers ---

    def _to_screen(self, wx: int, wy: int) -> Tuple[int, int]: #vers 1
        return int(wx * self._zoom) + self._pan.x(), int(wy * self._zoom) + self._pan.y()

    def _to_world(self, sx: int, sy: int) -> Tuple[int, int]: #vers 1
        return int((sx - self._pan.x()) / self._zoom), int((sy - self._pan.y()) / self._zoom)

    def _room_rect(self, node: RoomNode) -> QRect: #vers 1
        sx, sy = self._to_screen(node.position[0], node.position[1])
        return QRect(sx, sy, int(ROOM_W * self._zoom), int(ROOM_H * self._zoom))

    def _find_room_at(self, pos: QPoint) -> Optional[str]: #vers 1
        if not self.graph:
            return None
        for room_id, node in self.graph.rooms.items():
            if self._room_rect(node).contains(pos):
                return room_id
        return None

    # --- Drawing ---

    def paintEvent(self, event): #vers 1
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), COL_BG)

        self._draw_grid(painter)

        if not self.graph:
            painter.setPen(QColor(80, 80, 80))
            painter.setFont(QFont("Courier New", 11))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter,
                             "No stage loaded\nOpen a folder containing .rdt files")
            return

        self._draw_connections(painter)
        for room_id, node in self.graph.rooms.items():
            self._draw_room_box(painter, room_id, node)

        self._draw_status(painter)

    def _draw_grid(self, painter: QPainter): #vers 1
        painter.setPen(QPen(COL_GRID, 1))
        step = int(80 * self._zoom)
        if step < 8:
            return
        for x in range(0, self.width(), step):
            painter.drawLine(x, 0, x, self.height())
        for y in range(0, self.height(), step):
            painter.drawLine(0, y, self.width(), y)

    def _draw_connections(self, painter: QPainter): #vers 1
        if not self.graph:
            return
        seen = set()
        for conn in self.graph.connections:
            key = tuple(sorted([conn.from_room, conn.to_room]))
            node_a = self.graph.rooms.get(conn.from_room)
            node_b = self.graph.rooms.get(conn.to_room)
            if not node_a or not node_b:
                continue
            ra = self._room_rect(node_a)
            rb = self._room_rect(node_b)
            ax, ay = ra.center().x(), ra.center().y()
            bx, by = rb.center().x(), rb.center().y()

            painter.setPen(QPen(COL_CONN_LINE, 1.5))
            painter.drawLine(ax, ay, bx, by)

            # Arrow head on midpoint if not yet drawn
            if key not in seen:
                mx, my = (ax + bx) // 2, (ay + by) // 2
                painter.setBrush(QBrush(COL_CONN_ARR))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawEllipse(QPoint(mx, my), 4, 4)
                seen.add(key)

    def _draw_room_box(self, painter: QPainter, room_id: str, node: RoomNode): #vers 1
        rect = self._room_rect(node)
        selected = (room_id == self._selected_room)
        swap_first = (room_id == self._swap_pending)

        if swap_first:
            fill = QColor(80, 60, 20)
            border = QColor(255, 200, 50)
        elif selected:
            fill = COL_ROOM_SEL
            border = COL_ROOM_SEL_BORDER
        else:
            fill = COL_ROOM
            border = COL_ROOM_BORDER

        painter.setBrush(QBrush(fill))
        painter.setPen(QPen(border, 2 if selected or swap_first else 1))
        painter.drawRoundedRect(rect, 4, 4)

        # Room ID label
        font = QFont("Courier New", max(7, int(9 * self._zoom)))
        painter.setFont(font)
        painter.setPen(QPen(COL_TEXT))
        painter.drawText(rect.adjusted(3, 3, -3, -3),
                         Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter,
                         node.room_id)

        # Connection count
        painter.setFont(QFont("Courier New", max(6, int(7 * self._zoom))))
        painter.setPen(QPen(COL_TEXT_DIM))
        doors = len(node.connections)
        items = len(node.rdt.items) if node.rdt else 0
        painter.drawText(rect.adjusted(3, -3, -3, -3),
                         Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter,
                         f"doors:{doors}  items:{items}")

    def _draw_status(self, painter: QPainter): #vers 1
        if not self.graph:
            return
        painter.setPen(QColor(140, 140, 140))
        painter.setFont(QFont("Courier New", 8))
        info = (f"Rooms: {self.graph.room_count}  "
                f"Connections: {self.graph.connection_count}  "
                f"Zoom: {self._zoom*100:.0f}%")
        painter.drawText(6, self.height() - 6, info)

        if self._swap_pending:
            painter.setPen(QColor(255, 200, 50))
            painter.setFont(QFont("Courier New", 9))
            painter.drawText(6, 18,
                f"SWAP MODE: click second room to swap with {self._swap_pending}  [Esc to cancel]")

    # --- Mouse events ---

    def mousePressEvent(self, event: QMouseEvent): #vers 1
        pos = event.pos()

        if event.button() == Qt.MouseButton.RightButton:
            room_id = self._find_room_at(pos)
            self._show_context_menu(pos, room_id)
            return

        if event.button() == Qt.MouseButton.LeftButton:
            room_id = self._find_room_at(pos)
            if room_id:
                if self._swap_pending:
                    if room_id != self._swap_pending:
                        self._do_swap(self._swap_pending, room_id)
                    self._swap_pending = None
                else:
                    self._selected_room = room_id
                    self._drag_room = room_id
                    self._drag_start = pos
                    self.room_clicked.emit(room_id)
                self.update()
            else:
                self._panning = True
                self._drag_start = pos
                self._swap_pending = None
                self._selected_room = None
                self.update()

        elif event.button() == Qt.MouseButton.MiddleButton:
            self._panning = True
            self._drag_start = pos

    def mouseMoveEvent(self, event: QMouseEvent): #vers 1
        pos = event.pos()

        if self._panning and self._drag_start:
            self._pan += pos - self._drag_start
            self._drag_start = pos
            self.update()
            return

        if self._drag_room and self._drag_start and self.graph:
            node = self.graph.rooms.get(self._drag_room)
            if node:
                delta = pos - self._drag_start
                wx = int(delta.x() / self._zoom)
                wy = int(delta.y() / self._zoom)
                node.position = (node.position[0] + wx, node.position[1] + wy)
                self._drag_start = pos
                self.update()

    def mouseReleaseEvent(self, event: QMouseEvent): #vers 1
        self._panning = False
        self._drag_room = None
        self._drag_start = None

    def mouseDoubleClickEvent(self, event: QMouseEvent): #vers 1
        room_id = self._find_room_at(event.pos())
        if room_id:
            self.room_activated.emit(room_id)

    def wheelEvent(self, event: QWheelEvent): #vers 1
        pos = event.position().toPoint()
        wx, wy = self._to_world(pos.x(), pos.y())
        factor = 1.15 if event.angleDelta().y() > 0 else (1.0 / 1.15)
        self._zoom = max(0.15, min(self._zoom * factor, 4.0))
        sx, sy = self._to_screen(wx, wy)
        self._pan += QPoint(pos.x() - sx, pos.y() - sy)
        self.update()

    def keyPressEvent(self, event: QKeyEvent): #vers 1
        if event.key() == Qt.Key.Key_Escape:
            self._swap_pending = None
            self.update()
        elif event.key() in (Qt.Key.Key_Home, Qt.Key.Key_F):
            self.reset_view()
        else:
            super().keyPressEvent(event)

    # --- Context menu ---

    def _show_context_menu(self, pos: QPoint, room_id: Optional[str]): #vers 1
        menu = QMenu(self)
        if room_id:
            menu.addAction(f"Load room:  {room_id}",
                           lambda: self.room_activated.emit(room_id))
            menu.addSeparator()
            menu.addAction("Swap with another room...",
                           lambda: self._start_swap(room_id))
            menu.addAction("Remove room from stage",
                           lambda: self._confirm_remove(room_id))
        else:
            menu.addAction("Fit all rooms [F]", self.reset_view)
        menu.exec(self.mapToGlobal(pos))

    def _start_swap(self, room_id: str): #vers 1
        self._swap_pending = room_id
        self.update()

    def _do_swap(self, room_a: str, room_b: str): #vers 1
        if not self.graph:
            return
        try:
            swap_rooms(self.graph, room_a, room_b)
            self.update()
        except Exception as e:
            QMessageBox.warning(self, "Swap Error", str(e))

    def _confirm_remove(self, room_id: str): #vers 1
        reply = QMessageBox.question(self, "Remove Room",
            f"Remove {room_id} from the stage graph?\n"
            "This only removes connections in the editor.\n"
            "The .rdt file is not deleted.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            if not self.graph:
                return
            remove_room(self.graph, room_id)
            if self._selected_room == room_id:
                self._selected_room = None
            self.update()


class StageMapToolbar(QFrame): #vers 1
    """Toolbar for the stage map editor."""

    folder_opened = pyqtSignal(str)

    def __init__(self, canvas: StageMapCanvas, parent=None): #vers 1
        super().__init__(parent)
        self.canvas = canvas
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setMaximumHeight(34)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(4)

        open_btn = QPushButton("Open Stage Folder")
        open_btn.setMaximumHeight(26)
        open_btn.clicked.connect(self._open_folder)
        layout.addWidget(open_btn)

        fit_btn = QPushButton("Fit [F]")
        fit_btn.setMaximumHeight(26)
        fit_btn.clicked.connect(canvas.reset_view)
        layout.addWidget(fit_btn)

        layout.addStretch()

        self._info_label = QLabel("No stage loaded")
        self._info_label.setFont(QFont("Courier New", 8))
        layout.addWidget(self._info_label)

        canvas.room_clicked.connect(self._on_room_clicked)

    def _open_folder(self): #vers 1
        folder = QFileDialog.getExistingDirectory(self, "Open Stage Folder")
        if folder:
            self.folder_opened.emit(folder)

    def set_graph_info(self, graph): #vers 1
        self._info_label.setText(
            f"Stage: {os.path.basename(graph.folder_path)}  "
            f"{graph.room_count} rooms  {graph.connection_count} connections"
        )

    def _on_room_clicked(self, room_id: str): #vers 1
        self._info_label.setText(f"Selected: {room_id}")


class StageMapWidget(QWidget): #vers 1
    """Combined stage map canvas + toolbar for embedding in display stack."""

    room_activated = pyqtSignal(str)  # emits file_path of selected room

    def __init__(self, parent=None): #vers 1
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.canvas = StageMapCanvas(self)
        self.toolbar = StageMapToolbar(self.canvas, self)

        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas, stretch=1)

        self.toolbar.folder_opened.connect(self._load_folder)
        self.canvas.room_activated.connect(self._on_room_activated)

    def load_folder(self, folder_path: str): #vers 1
        self._load_folder(folder_path)

    def _load_folder(self, folder_path: str): #vers 1
        from apps.core.re1_room_map import scan_stage_folder
        graph = scan_stage_folder(folder_path, load_rdts=True)
        self.canvas.load_graph(graph)
        self.toolbar.set_graph_info(graph)
        if graph.parse_errors:
            print(f"Stage map errors: {graph.parse_errors}")

    def _on_room_activated(self, room_id: str): #vers 1
        if not self.canvas.graph:
            return
        node = self.canvas.graph.rooms.get(room_id)
        if node and node.file_path:
            self.room_activated.emit(node.file_path)

    def reset_view(self): #vers 1
        self.canvas.reset_view()
