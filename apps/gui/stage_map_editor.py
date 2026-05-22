#!/usr/bin/env python3
#this belongs in apps/gui/stage_map_editor.py - Version: 2
# X-Seti - May22 2026 - ResBio-Evil-Workshop - Stage Map Editor
"""
Stage Map Editor - Visual map of rooms in a stage with named boxes,
directional connection arrows, and thumbnail placeholders.
Layout matches room topology, not a dumb grid.
Click = load room + show cameras. Drag rooms to reposition.
"""

import os
from typing import Optional, Dict, Tuple, List, TYPE_CHECKING
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFrame, QMenu, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, QPoint, QRect, QPointF, pyqtSignal
from PyQt6.QtGui import (
    QPainter, QPen, QBrush, QColor, QFont, QPolygon,
    QWheelEvent, QMouseEvent, QKeyEvent, QFontMetrics
)

from PyQt6.QtGui import QImage
from apps.core.re1_room_map import (
    StageGraph, RoomNode, scan_stage_folder, swap_rooms, remove_room
)

##Methods list -
# _arrow_between_rects
# _draw_connections
# _draw_room_box
# _draw_status
# _draw_grid
# _find_room_at
# _room_rect
# _show_context_menu
# _start_swap
# _do_swap
# _confirm_remove
# keyPressEvent
# load_graph
# mouseDoubleClickEvent
# mouseMoveEvent
# mousePressEvent
# mouseReleaseEvent
# paintEvent
# reset_view
# wheelEvent

##class StageMapCanvas:
##class StageMapToolbar:
##class StageMapWidget:


# Room names loaded from central database
try:
    from apps.core.re_room_names import get_room_name_or_id as _get_room_name_or_id
except ImportError:
    def _get_room_name_or_id(room_id: str) -> str:
        return room_id

# Colors
COL_BG          = QColor(14, 16, 20)
COL_ROOM        = QColor(28, 38, 54)
COL_ROOM_BORDER = QColor(60, 110, 180)
COL_ROOM_HOVER  = QColor(38, 52, 72)
COL_ROOM_SEL    = QColor(45, 75, 130)
COL_ROOM_SEL_BORDER = QColor(100, 180, 255)
COL_ROOM_SWAP   = QColor(70, 50, 15)
COL_ROOM_SWAP_BORDER = QColor(255, 190, 40)
COL_THUMB_BG    = QColor(20, 28, 40)
COL_CONN        = QColor(80, 160, 80, 200)
COL_CONN_DARK   = QColor(60, 120, 60, 140)
COL_ARROW       = QColor(100, 200, 100, 230)
COL_TEXT        = QColor(200, 215, 230)
COL_TEXT_ID     = QColor(100, 140, 180)
COL_TEXT_DIM    = QColor(100, 115, 130)
COL_GRID        = QColor(22, 25, 30)

ROOM_W      = 130
ROOM_H      = 72
THUMB_H     = 36   # height of thumbnail area inside box
ARROW_SIZE  = 8


def _get_room_name(room_id: str) -> str: #vers 2
    """Return human-readable name for a room ID, or the raw ID."""
    return _get_room_name_or_id(room_id)


class StageMapCanvas(QWidget): #vers 1
    """QPainter canvas drawing rooms as named boxes with directional arrows."""

    room_clicked   = pyqtSignal(str)   # single click: room_id
    room_activated = pyqtSignal(str)   # double-click: load room

    def __init__(self, parent=None): #vers 1
        super().__init__(parent)
        self.graph: Optional[StageGraph] = None
        self._zoom = 1.0
        self._pan = QPoint(40, 40)
        self._drag_start: Optional[QPoint] = None
        self._drag_room: Optional[str] = None
        self._selected_room: Optional[str] = None
        self._hovered_room: Optional[str] = None
        self._panning = False
        self._swap_pending: Optional[str] = None

        self._thumb_cache: Dict[str, Optional[object]] = {}  # room_id -> QPixmap or None
        self._thumb_loading: set = set()   # room_ids currently loading

        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setStyleSheet("background-color: #0e1014;")
        self.setMinimumSize(300, 300)

    def load_graph(self, graph: StageGraph): #vers 1
        self.graph = graph
        self._selected_room = None
        self._swap_pending = None
        self._hovered_room = None
        self._thumb_cache.clear()
        self._thumb_loading.clear()
        self.reset_view()
        self.update()

    def reset_view(self): #vers 1
        if not self.graph or not self.graph.rooms:
            self._zoom = 1.0
            self._pan = QPoint(40, 40)
            self.update()
            return

        positions = [n.position for n in self.graph.rooms.values()]
        min_x = min(p[0] for p in positions) - 20
        min_y = min(p[1] for p in positions) - 20
        max_x = max(p[0] for p in positions) + ROOM_W + 20
        max_y = max(p[1] for p in positions) + ROOM_H + 20

        w = max(max_x - min_x, 1)
        h = max(max_y - min_y, 1)
        zoom_x = self.width()  * 0.9 / w
        zoom_y = self.height() * 0.9 / h
        self._zoom = max(0.1, min(zoom_x, zoom_y, 2.0))

        cx = (min_x + max_x) / 2
        cy = (min_y + max_y) / 2
        self._pan = QPoint(
            int(self.width()  / 2 - cx * self._zoom),
            int(self.height() / 2 - cy * self._zoom)
        )
        self.update()

    # --- Coordinates ---

    def _to_screen(self, wx, wy) -> Tuple[int, int]: #vers 1
        return int(wx * self._zoom) + self._pan.x(), int(wy * self._zoom) + self._pan.y()

    def _to_world(self, sx, sy) -> Tuple[int, int]: #vers 1
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
            painter.setPen(QColor(70, 75, 85))
            painter.setFont(QFont("Courier New", 11))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter,
                             "No stage loaded\n\nOpen a stage folder containing .rdt files\nor use File > Open Stage Folder")
            return

        self._draw_connections(painter)
        for room_id, node in self.graph.rooms.items():
            self._draw_room_box(painter, room_id, node)
        self._draw_status(painter)

    def _draw_grid(self, painter: QPainter): #vers 1
        step = int(60 * self._zoom)
        if step < 6:
            return
        painter.setPen(QPen(COL_GRID, 1))
        for x in range(self._pan.x() % step, self.width(), step):
            painter.drawLine(x, 0, x, self.height())
        for y in range(self._pan.y() % step, self.height(), step):
            painter.drawLine(0, y, self.width(), y)

    def _draw_connections(self, painter: QPainter): #vers 1
        if not self.graph:
            return

        drawn_bidirectional = set()

        for conn in self.graph.connections:
            node_a = self.graph.rooms.get(conn.from_room)
            node_b = self.graph.rooms.get(conn.to_room)
            if not node_a or not node_b:
                continue

            key = tuple(sorted([conn.from_room, conn.to_room]))
            bidirectional = any(
                c.from_room == conn.to_room and c.to_room == conn.from_room
                for c in self.graph.connections
            )

            ra = self._room_rect(node_a)
            rb = self._room_rect(node_b)

            # Find best edge-to-edge connection points
            ax, ay, bx, by = self._arrow_between_rects(ra, rb)

            is_selected = (conn.from_room == self._selected_room or
                           conn.to_room == self._selected_room)
            line_color = COL_CONN if is_selected else COL_CONN_DARK
            painter.setPen(QPen(line_color, 1.5 if is_selected else 1.0))
            painter.drawLine(ax, ay, bx, by)

            # Draw directional arrowhead at destination end
            self._draw_arrowhead(painter, ax, ay, bx, by, COL_ARROW if is_selected else COL_CONN)

            # If bidirectional and not yet drawn the reverse arrow
            if bidirectional and key not in drawn_bidirectional:
                self._draw_arrowhead(painter, bx, by, ax, ay, COL_CONN_DARK)
                drawn_bidirectional.add(key)

    def _arrow_between_rects(self, ra: QRect, rb: QRect): #vers 1
        """Return (ax, ay, bx, by) connecting nearest edges of two rects."""
        ax, ay = ra.center().x(), ra.center().y()
        bx, by = rb.center().x(), rb.center().y()

        dx = bx - ax
        dy = by - ay

        # Clamp exit point to edge of ra
        if abs(dx) > abs(dy):
            ax = ra.right() if dx > 0 else ra.left()
            ay = ra.center().y()
        else:
            ax = ra.center().x()
            ay = ra.bottom() if dy > 0 else ra.top()

        # Clamp entry point to edge of rb
        if abs(dx) > abs(dy):
            bx = rb.left() if dx > 0 else rb.right()
            by = rb.center().y()
        else:
            bx = rb.center().x()
            by = rb.top() if dy > 0 else rb.bottom()

        return ax, ay, bx, by

    def _draw_arrowhead(self, painter: QPainter, ax, ay, bx, by, color: QColor): #vers 1
        """Draw filled triangle arrowhead at (bx, by) pointing from (ax,ay)."""
        import math
        dx, dy = bx - ax, by - ay
        length = math.sqrt(dx*dx + dy*dy)
        if length < 1:
            return
        ux, uy = dx / length, dy / length
        px, py = -uy, ux  # perpendicular

        sz = max(5, int(ARROW_SIZE * self._zoom))
        p1 = QPoint(int(bx), int(by))
        p2 = QPoint(int(bx - ux * sz + px * sz * 0.4),
                    int(by - uy * sz + py * sz * 0.4))
        p3 = QPoint(int(bx - ux * sz - px * sz * 0.4),
                    int(by - uy * sz - py * sz * 0.4))

        painter.setBrush(QBrush(color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPolygon(QPolygon([p1, p2, p3]))

    def _draw_room_box(self, painter: QPainter, room_id: str, node: RoomNode): #vers 1
        rect = self._room_rect(node)
        selected  = (room_id == self._selected_room)
        hovered   = (room_id == self._hovered_room)
        swap_mode = (room_id == self._swap_pending)

        # Choose colors
        if swap_mode:
            fill, border, bw = COL_ROOM_SWAP, COL_ROOM_SWAP_BORDER, 2
        elif selected:
            fill, border, bw = COL_ROOM_SEL, COL_ROOM_SEL_BORDER, 2
        elif hovered:
            fill, border, bw = COL_ROOM_HOVER, COL_ROOM_BORDER, 1
        else:
            fill, border, bw = COL_ROOM, COL_ROOM_BORDER, 1

        # Main box
        painter.setBrush(QBrush(fill))
        painter.setPen(QPen(border, bw))
        painter.drawRoundedRect(rect, 5, 5)

        th = int(THUMB_H * self._zoom)

        # Thumbnail strip at top
        thumb_rect = QRect(rect.left() + 1, rect.top() + 1, rect.width() - 2, th)

        # Try to paint cached thumbnail
        pixmap = self._thumb_cache.get(room_id)
        if pixmap is not None and not isinstance(pixmap, bool):
            # Draw the pixmap scaled to thumb_rect
            painter.drawPixmap(thumb_rect, pixmap)
        else:
            painter.setBrush(QBrush(COL_THUMB_BG))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(thumb_rect)
            if self._zoom >= 0.4:
                painter.setPen(QPen(QColor(50, 65, 85)))
                painter.setFont(QFont("Courier New", max(5, int(6 * self._zoom))))
                msg = "loading..." if room_id in self._thumb_loading else "[no bg]"
                painter.drawText(thumb_rect, Qt.AlignmentFlag.AlignCenter, msg)
            # Trigger async load if not already attempted
            if pixmap is None and room_id not in self._thumb_loading:
                self._request_thumbnail(room_id, node)

        # Divider line between thumb and text area
        painter.setPen(QPen(border.darker(150), 1))
        painter.drawLine(rect.left(), rect.top() + th + 1,
                         rect.right(), rect.top() + th + 1)

        # Text area
        text_rect = rect.adjusted(4, th + 4, -4, -3)

        # Human-readable name (larger, top of text area)
        name = _get_room_name(room_id)
        name_font_size = max(6, int(8 * self._zoom))
        painter.setFont(QFont("Courier New", name_font_size, QFont.Weight.Bold))
        painter.setPen(QPen(COL_TEXT))
        # Clip name to fit
        fm = QFontMetrics(painter.font())
        clipped_name = fm.elidedText(name, Qt.TextElideMode.ElideRight, text_rect.width())
        name_rect = QRect(text_rect.left(), text_rect.top(),
                          text_rect.width(), text_rect.height() // 2 + 2)
        painter.drawText(name_rect,
                         Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft,
                         clipped_name)

        # Room ID + stats (smaller, bottom of text area)
        if self._zoom >= 0.5:
            painter.setFont(QFont("Courier New", max(5, int(6 * self._zoom))))
            painter.setPen(QPen(COL_TEXT_ID))
            doors = len(node.connections)
            items = len(node.rdt.items) if node.rdt else 0
            cams  = len(node.rdt.cameras) if node.rdt else 0
            stats = f"{room_id}  d:{doors} i:{items} c:{cams}"
            stats_rect = QRect(text_rect.left(), text_rect.top() + text_rect.height() // 2,
                               text_rect.width(), text_rect.height() // 2)
            painter.drawText(stats_rect,
                             Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft,
                             stats)

    def _request_thumbnail(self, room_id: str, node): #vers 1
        """Request thumbnail load for a room node. Runs in a thread."""
        from PyQt6.QtCore import QThread, QObject, pyqtSignal as _sig

        if not node or not node.file_path:
            self._thumb_cache[room_id] = False  # mark as attempted/failed
            return

        self._thumb_loading.add(room_id)

        class ThumbWorker(QObject):
            done = _sig(str, object)  # room_id, QPixmap or None
            def __init__(self, rid, path):
                super().__init__()
                self._rid = rid
                self._path = path
            def run(self):
                try:
                    from apps.core.re_backgrounds import find_backgrounds_for_rdt, load_background
                    from PyQt6.QtGui import QImage, QPixmap
                    paths = find_backgrounds_for_rdt(self._path)
                    if not paths:
                        self.done.emit(self._rid, None)
                        return
                    bg = load_background(paths[0])
                    if not bg.valid or not bg.rgba_data:
                        self.done.emit(self._rid, None)
                        return
                    img = QImage(bg.rgba_data, bg.width, bg.height,
                                 bg.width * 4, QImage.Format.Format_RGBA8888)
                    self.done.emit(self._rid, QPixmap.fromImage(img))
                except Exception as e:
                    self.done.emit(self._rid, None)

        worker = ThumbWorker(room_id, node.file_path)
        thread = QThread()
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.done.connect(lambda rid, px: self._on_thumbnail_loaded(rid, px, thread))
        worker.done.connect(thread.quit)

        # Keep references alive
        if not hasattr(self, '_thumb_threads'):
            self._thumb_threads = []
        self._thumb_threads.append((thread, worker))
        thread.start()

    def _on_thumbnail_loaded(self, room_id: str, pixmap, thread): #vers 1
        """Called when thumbnail load finishes."""
        self._thumb_loading.discard(room_id)
        self._thumb_cache[room_id] = pixmap if pixmap is not None else False
        # Clean up dead threads
        if hasattr(self, '_thumb_threads'):
            self._thumb_threads = [(t, w) for t, w in self._thumb_threads
                                   if t.isRunning()]
        self.update()

    def _draw_status(self, painter: QPainter): #vers 1
        if not self.graph:
            return
        painter.setPen(QColor(90, 100, 115))
        painter.setFont(QFont("Courier New", 8))
        info = (f"Rooms: {self.graph.room_count}  "
                f"Connections: {self.graph.connection_count}  "
                f"Zoom: {self._zoom*100:.0f}%  "
                f"[double-click to load  |  drag to reposition  |  right-click for options]")
        painter.drawText(6, self.height() - 6, info)

        if self._swap_pending:
            painter.setPen(QColor(255, 190, 40))
            painter.setFont(QFont("Courier New", 9, QFont.Weight.Bold))
            name = _get_room_name(self._swap_pending)
            painter.drawText(6, 20,
                f"SWAP MODE: click room to swap with [{name}]  [Esc = cancel]")

    # --- Mouse ---

    def mousePressEvent(self, event: QMouseEvent): #vers 1
        pos = event.pos()
        if event.button() == Qt.MouseButton.RightButton:
            self._show_context_menu(pos, self._find_room_at(pos))
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
                self._selected_room = None
                self._swap_pending = None
                self.update()

        elif event.button() == Qt.MouseButton.MiddleButton:
            self._panning = True
            self._drag_start = pos

    def mouseMoveEvent(self, event: QMouseEvent): #vers 1
        pos = event.pos()
        # Update hover
        hovered = self._find_room_at(pos)
        if hovered != self._hovered_room:
            self._hovered_room = hovered
            self.update()

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
            self._selected_room = room_id
            self.room_activated.emit(room_id)
            self.update()

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
            name = _get_room_name(room_id)
            menu.addAction(f"Load:  {name}",
                           lambda: (setattr(self, '_selected_room', room_id),
                                    self.room_activated.emit(room_id),
                                    self.update()))
            menu.addSeparator()
            menu.addAction("Swap with another room...",
                           lambda: self._start_swap(room_id))
            menu.addAction("Remove from stage",
                           lambda: self._confirm_remove(room_id))
        else:
            menu.addAction("Fit all rooms  [F]", self.reset_view)
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
        name = _get_room_name(room_id)
        reply = QMessageBox.question(self, "Remove Room",
            f"Remove [{name}] from the stage graph?\n"
            "The .rdt file is NOT deleted — only the map entry is removed.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes and self.graph:
            remove_room(self.graph, room_id)
            if self._selected_room == room_id:
                self._selected_room = None
            self.update()


class StageMapToolbar(QFrame): #vers 2
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
        name = _get_room_name(room_id)
        self._info_label.setText(f"  {room_id}  {name}")


class StageMapWidget(QWidget): #vers 2
    """Combined stage map canvas + toolbar. room_activated -> load RDT."""

    room_activated = pyqtSignal(str)   # emits file_path

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
        graph = scan_stage_folder(folder_path, load_rdts=True)
        self.canvas.load_graph(graph)
        self.toolbar.set_graph_info(graph)
        if graph.parse_errors:
            print(f"Stage map load errors:\n" + "\n".join(graph.parse_errors))

    def _on_room_activated(self, room_id: str): #vers 1
        if not self.canvas.graph:
            return
        node = self.canvas.graph.rooms.get(room_id)
        if node and node.file_path:
            self.room_activated.emit(node.file_path)

    def reset_view(self): #vers 1
        self.canvas.reset_view()
