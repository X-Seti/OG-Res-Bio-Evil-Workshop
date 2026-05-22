#!/usr/bin/env python3
#this belongs in apps/core/re1_room_map.py - Version: 1
# X-Seti - May22 2026 - ResBio-Evil-Workshop - RE1 Room Connection Map
"""
RE1 Room Connection Map - Scans a folder of RDT files and builds a
graph of room connections from camera switch (door transition) data.
RDT offset[0] = camera switch table with destination room IDs.
"""

import os
import struct
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from apps.core.re1_formats import parse_rdt, RDTFile

##Methods list -
# scan_stage_folder
# parse_camera_switches
# build_stage_graph
# get_room_id_from_filename
# swap_rooms
# remove_room
# get_connected_rooms

##class RoomConnection:
##class RoomNode:
##class StageGraph:


@dataclass
class RoomConnection: #vers 1
    """A directional link from one room to another via a door."""
    from_room: str
    to_room: str
    switch_index: int       # index in camera switch table
    switch_offset: int      # byte offset in RDT file
    dest_room_id: int       # raw destination room ID byte from switch entry
    flags: int = 0
    cut: int = 0            # camera cut number

    @property
    def label(self) -> str:
        return f"{self.from_room} -> {self.to_room} (switch {self.switch_index})"


@dataclass
class RoomNode: #vers 1
    """A room in the stage graph."""
    room_id: str            # e.g. "ROOM000"
    file_path: str
    rdt: Optional[RDTFile] = None
    connections: List[RoomConnection] = field(default_factory=list)
    position: Tuple[int, int] = (0, 0)   # display position in stage map
    stage: int = 0
    index: int = 0

    @property
    def display_name(self) -> str:
        return f"{self.room_id}\n{len(self.connections)} doors"


@dataclass
class StageGraph: #vers 1
    """All rooms in a stage folder and their connections."""
    folder_path: str
    rooms: Dict[str, RoomNode] = field(default_factory=dict)
    connections: List[RoomConnection] = field(default_factory=list)
    parse_errors: List[str] = field(default_factory=list)

    @property
    def room_count(self) -> int:
        return len(self.rooms)

    @property
    def connection_count(self) -> int:
        return len(self.connections)


# Camera switch entry sizes in RE1 RDT
# Structure (approximated from reevengi-tools):
# cut(1) cam(1) dest_room(1) dest_cut(1) x(2) z(2) w(2) h(2) = 12 bytes
_SWITCH_ENTRY_SIZE = 12
_SWITCH_TERM = 0xFF  # terminator byte


def get_room_id_from_filename(filename: str) -> str: #vers 1
    """Extract room ID string from filename. E.g. ROOM000.RDT -> ROOM000"""
    name = os.path.splitext(os.path.basename(filename))[0].upper()
    return name


def scan_stage_folder(folder_path: str, load_rdts: bool = True) -> StageGraph: #vers 1
    """Scan a folder for .rdt files and build a StageGraph."""
    graph = StageGraph(folder_path=folder_path)

    if not os.path.isdir(folder_path):
        graph.parse_errors.append(f"Not a directory: {folder_path}")
        return graph

    rdt_files = sorted([
        os.path.join(folder_path, f)
        for f in os.listdir(folder_path)
        if f.upper().endswith('.RDT')
    ])

    for file_path in rdt_files:
        room_id = get_room_id_from_filename(file_path)
        node = RoomNode(room_id=room_id, file_path=file_path)
        node.stage, node.index = _parse_room_id_numbers(room_id)

        if load_rdts:
            try:
                node.rdt = parse_rdt(file_path)
                if not node.rdt.valid:
                    graph.parse_errors.append(
                        f"{room_id}: {'; '.join(node.rdt.parse_errors)}")
            except Exception as e:
                graph.parse_errors.append(f"{room_id}: {e}")

        graph.rooms[room_id] = node

    if load_rdts:
        build_stage_graph(graph)

    _assign_layout_positions(graph)
    return graph


def build_stage_graph(graph: StageGraph): #vers 1
    """Parse camera switch tables and populate room connections."""
    graph.connections.clear()
    for room_id, node in graph.rooms.items():
        if not node.rdt or not node.rdt.valid:
            continue
        conns = parse_camera_switches(node.rdt, room_id, graph)
        node.connections = conns
        graph.connections.extend(conns)


def parse_camera_switches(rdt: RDTFile, room_id: str, graph: StageGraph) -> List[RoomConnection]: #vers 1
    """Parse camera switch table from RDT offset[0] to find door connections."""
    connections = []
    if not rdt.header or not rdt.header.offsets:
        return connections

    switch_offset = rdt.header.offsets[0]
    if switch_offset == 0 or switch_offset >= len(rdt.raw_data):
        return connections

    data = rdt.raw_data
    off = switch_offset
    idx = 0
    max_entries = 64

    while idx < max_entries:
        if off + _SWITCH_ENTRY_SIZE > len(data):
            break

        # Read switch entry
        try:
            cut, cam, dest_room, dest_cut = struct.unpack_from('<BBBB', data, off)
        except struct.error:
            break

        if cut == _SWITCH_TERM:
            break

        # dest_room encodes stage + room: high nibble = stage, low nibble = room
        dest_stage = (dest_room >> 4) & 0x0F
        dest_idx   = dest_room & 0x0F

        # Build destination room_id string to match filenames
        dest_room_id = _build_room_id(dest_stage, dest_idx, graph)

        conn = RoomConnection(
            from_room=room_id,
            to_room=dest_room_id,
            switch_index=idx,
            switch_offset=off,
            dest_room_id=dest_room,
            flags=cam,
            cut=cut,
        )
        connections.append(conn)
        off += _SWITCH_ENTRY_SIZE
        idx += 1

    return connections


def get_connected_rooms(graph: StageGraph, room_id: str) -> List[str]: #vers 1
    """Return list of room IDs directly connected to room_id."""
    node = graph.rooms.get(room_id)
    if not node:
        return []
    return list(set(c.to_room for c in node.connections if c.to_room in graph.rooms))


def swap_rooms(graph: StageGraph, room_a: str, room_b: str): #vers 1
    """Swap two rooms in the graph. Updates connection destination IDs.
    Warning: Only swaps references in the graph data structure.
    Call write_rdt on each modified room to persist to disk.
    """
    if room_a not in graph.rooms or room_b not in graph.rooms:
        raise ValueError(f"Both rooms must exist in graph: {room_a}, {room_b}")

    node_a = graph.rooms[room_a]
    node_b = graph.rooms[room_b]

    # Swap room IDs and indexes
    node_a.room_id, node_b.room_id = room_b, room_a
    node_a.stage, node_b.stage = node_b.stage, node_a.stage
    node_a.index, node_b.index = node_b.index, node_a.index

    # Re-key in dict
    graph.rooms[room_b] = node_a
    graph.rooms[room_a] = node_b

    # Update all connection from/to references
    for conn in graph.connections:
        if conn.from_room == room_a:
            conn.from_room = room_b
        elif conn.from_room == room_b:
            conn.from_room = room_a
        if conn.to_room == room_a:
            conn.to_room = room_b
        elif conn.to_room == room_b:
            conn.to_room = room_a

    # Patch raw bytes in each node's rdt.raw_data
    _patch_switch_dest(node_a, node_b.stage, node_b.index)
    _patch_switch_dest(node_b, node_a.stage, node_a.index)


def remove_room(graph: StageGraph, room_id: str): #vers 1
    """Remove a room from the graph and orphan its incoming connections."""
    if room_id not in graph.rooms:
        return
    del graph.rooms[room_id]
    # Remove connections to/from the room
    graph.connections = [
        c for c in graph.connections
        if c.from_room != room_id and c.to_room != room_id
    ]
    # Also clear from remaining nodes
    for node in graph.rooms.values():
        node.connections = [c for c in node.connections
                           if c.from_room != room_id and c.to_room != room_id]


# --- Internal helpers ---

def _parse_room_id_numbers(room_id: str) -> Tuple[int, int]: #vers 1
    """Extract (stage, index) from room ID string like ROOM000 or ROOM1A0."""
    name = room_id.upper().replace('ROOM', '').replace('.RDT', '')
    try:
        if len(name) >= 3:
            stage = int(name[0], 16)
            index = int(name[1:3], 16)
            return stage, index
    except ValueError:
        pass
    return 0, 0


def _build_room_id(stage: int, index: int, graph: StageGraph) -> str: #vers 1
    """Build a room_id string matching the graph's naming convention."""
    # Try to find matching room in graph by stage/index
    for room_id, node in graph.rooms.items():
        if node.stage == stage and node.index == index:
            return room_id
    # Fallback: construct canonical name
    return f"ROOM{stage:01X}{index:02X}"


def _patch_switch_dest(node: RoomNode, new_stage: int, new_index: int): #vers 1
    """Patch destination room bytes in a node's raw_data camera switch table."""
    if not node.rdt or not node.rdt.raw_data or not node.rdt.header:
        return
    switch_offset = node.rdt.header.offsets[0]
    if not switch_offset:
        return

    data = bytearray(node.rdt.raw_data)
    new_dest_byte = ((new_stage & 0x0F) << 4) | (new_index & 0x0F)

    off = switch_offset
    max_entries = 64
    for _ in range(max_entries):
        if off + _SWITCH_ENTRY_SIZE > len(data):
            break
        cut = data[off]
        if cut == _SWITCH_TERM:
            break
        # dest_room is at byte offset 2 within the entry
        data[off + 2] = new_dest_byte
        off += _SWITCH_ENTRY_SIZE

    node.rdt.raw_data = bytes(data)


def _assign_layout_positions(graph: StageGraph): #vers 2
    """Assign topology-aware positions using BFS from the lowest-index room.
    Rooms are spread out by connection depth so the map resembles the
    actual layout rather than a dump grid.
    """
    if not graph.rooms:
        return

    rooms = list(graph.rooms.values())

    # Build adjacency: room_id -> set of connected room_ids
    adj: Dict[str, set] = {r: set() for r in graph.rooms}
    for conn in graph.connections:
        if conn.from_room in adj and conn.to_room in adj:
            adj[conn.from_room].add(conn.to_room)
            adj[conn.to_room].add(conn.from_room)

    # BFS to assign levels (depth from start room)
    start = sorted(graph.rooms.keys())[0]
    visited = {}
    queue = [(start, 0, 0)]  # (room_id, depth, branch)
    depth_slots: Dict[int, List[str]] = {}

    while queue:
        room_id, depth, branch = queue.pop(0)
        if room_id in visited:
            continue
        visited[room_id] = depth
        if depth not in depth_slots:
            depth_slots[depth] = []
        depth_slots[depth].append(room_id)
        neighbors = sorted(adj.get(room_id, set()) - set(visited.keys()))
        for i, nb in enumerate(neighbors):
            queue.append((nb, depth + 1, i))

    # Handle disconnected rooms
    for room_id in graph.rooms:
        if room_id not in visited:
            max_depth = max(depth_slots.keys()) + 1 if depth_slots else 0
            visited[room_id] = max_depth
            if max_depth not in depth_slots:
                depth_slots[max_depth] = []
            depth_slots[max_depth].append(room_id)

    # Assign positions: depth = column, slot within depth = row
    COL_STEP = 180
    ROW_STEP = 110

    for depth, room_ids in depth_slots.items():
        for slot, room_id in enumerate(room_ids):
            node = graph.rooms[room_id]
            node.position = (depth * COL_STEP, slot * ROW_STEP)
