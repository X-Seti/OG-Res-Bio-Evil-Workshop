# ResBio-Evil-Workshop ChangeLog

## December 14, 2025

### Research Phase 1: File Format Documentation
- **Status:** COMPLETED
- **Work:**
  - Researched Resident Evil 1 (PS1/PC) file formats
  - Created RE1_FILE_FORMATS_RESEARCH.md with format specifications
  - Identified critical formats: RDT (rooms), EMD (models), TIM (textures)
  - Found reference implementation: reevengi-tools (GitHub)
  
- **Key Findings:**
  - RDT format is PRIMARY priority for room loading/editing
  - Item placement data embedded in RDT files
  - PS1/PC versions mostly compatible
  - Format specs available in reevengi-tools wiki
  
- **Next Phase:** RDT parser implementation

### Launcher & Main App Fixes
- **Status:** COMPLETED
- **Work:**
  - Fixed launcher.py import paths (ResBio_Evil_Workshop)
  - Renamed class GUIWorkshop → ResBioEvilWorkshop
  - Fixed header paths in ResBio_Evil_Workshop.py
  - Fixed line ending issues (CRLF → LF)
  - Added proper sys.path handling for depends/ folder
  
- **Outstanding:**
  - Folder rename from hyphenated to underscore (ResBio-Evil-Workshop → ResBio_Evil_Workshop)
  - Launcher v5 ready, tested (loads UI)

### UI Status
- **Status:** SKELETON ONLY
- **Contains:** Placeholder widgets, no actual functionality
- **Ready for:** Phase 2 - file loading implementation

---

## TODO - High Priority

- [ ] Implement RDT parser module (re1_formats.py)
- [ ] Parse room geometry from RDT
- [ ] Parse item placement from RDT
- [ ] Create room loader UI integration
- [ ] Add file browser for game files (ISO/CD)

---

## Files Modified

| File | Version | Status |
|------|---------|--------|
| launcher.py | 5 | Ready |
| ResBio_Evil_Workshop.py | 2 | Ready |
| RE1_FILE_FORMATS_RESEARCH.md | 1 | NEW |
| ChangeLog | 1 | NEW |

---

## Session Notes

First time exploring RE1 file formats. reevengi-tools provides excellent reference. Focus on RDT parsing before anything else since room loading is blocked on it.

---

## May 22 2026

### Phase 2: Core Parser Implementation + Room Map Editor

#### New Files
- **apps/core/re1_formats.py** v1 - Binary parsers for RDT, TIM, EMD, SCA formats
  - RDTFile, RDTHeader, RDTCamera, RDTItem, RDTCollisionBoundary dataclasses
  - TIMFile with 4/8/16/24-bit color decoding to RGBA
  - EMDFile with vertex/normal/triangle parsing
  - RE1_ITEM_NAMES lookup table (70+ items)
  - parse_rdt(), parse_tim(), parse_emd(), parse_sca_header()

- **apps/methods/rdt_loader.py** v1 - RDT loader for GUI integration
  - load_rdt_file() - loads RDT and updates main window
  - populate_room_table() - section overview in middle panel
  - populate_items_table() - item placement list
  - populate_cameras_table() - camera data list
  - get_room_summary_text() - text panel summary

- **apps/gui/room_map_editor.py** v1 - 2D top-down room map editor
  - RoomMapEditor - QPainter-based, no OpenGL dependency
  - Draws collision boundaries, camera positions, items
  - Pan (LMB drag), zoom (wheel), item drag, camera select
  - Keyboard: F=fit, G=grid, C=cameras, I=items, B=collision
  - RoomMapToolbar - toggle buttons + live coordinate display
  - RoomMapWidget - combined toolbar+editor for embedding

#### Modified Files
- **ResBio_Evil_Workshop.py** - 843 lines of duplicates removed
  - Removed: 2x _apply_button_mode, 2x _apply_fonts_to_widgets
  - Removed: 3x _show_workshop_settings, 2x _get_icon_color, 3x keyPressEvent
  - _open_file: now opens .rdt files (was .col)
  - _load_rdt(): new method, calls rdt_loader
  - Display stack page 1: RoomMapWidget (was placeholder label)
  - Display mode combo: "Room Map" (was "3D Model")
  - Added: _on_map_item_selected, _on_map_camera_selected, _on_map_item_moved
  - Added: _on_col_selected, _enable_name_edit, _create_merged_icons_line stubs
  - Added: current_rdt, current_file_path, icon_display_mode init in __init__

### TODO - Next
- [ ] Test with real RDT files
- [ ] _save_file: implement RDT write-back
- [ ] Texture viewer (TIM display in display stack page 2)
- [ ] EMD model viewer

### May 22 2026 - Session continued

#### New Files
- **apps/gui/tim_viewer.py** v1 - PSX TIM texture viewer
  - TIMCanvas: pan/zoom QPainter widget
  - TIMViewerWidget: canvas + toolbar (Fit, +/- zoom)
  - load_tim_file(path) and load_tim_data(TIMFile)
  - Wired into display stack page 2 ("Texture")

#### Modified Files
- **ResBio_Evil_Workshop.py**
  - Display stack page 2: TIMViewerWidget (was placeholder)
  - show_texture(): uses real TIMViewerWidget
  - show_tim_file(): new method, load TIM by path

#### Verified
- RDT parser: cameras, items (terminator), collision all parse correctly
- All 5 modules import cleanly
- All syntax checks pass

#### TODO
- [ ] Test with real .rdt and .tim files from RE1 game
- [ ] _save_file: RDT write-back (modify items, export)
- [ ] Middle panel: tab-switch between overview/items/cameras views
- [ ] EMD model viewer (display stack page - future)

---

## May 22 2026 - Session 3 (5:30am wrap-up)

### Bug Fixes
- **ResBio_Evil_Workshop.py** - Fixed `No module named 'depends'` by inserting `sys.path` patch before bare `depends.*` imports
- **resbio_svg_icons.py** - Was empty stub (27 lines). Replaced with full factory: 50+ icon methods. All toolbar icons now functional.
- **ResBio_Evil_Workshop.py** - Fixed `apps.debug.debug_functions` import in docked mode block (changed to `depends.img_debug_functions`)
- **ResBio_Evil_Workshop.py** - Fixed research tab import: `apps.components.research_tab` -> `apps.methods.research_tab`
- **resbio_svg_icons.py** - Added `research_icon()` (book with lines SVG)
- **ResBio_Evil_Workshop.py** - Research button now shows icon

### Readme
- **Readme.md** - Written from scratch: purpose, file formats table, run instructions, game file locations, project layout

---

## TODO - Next session priority order

### Immediate (app must-haves)
- [ ] Middle panel tab bar: Overview / Items / Cameras / Collision (switch table content without mode combo)
- [ ] _save_file: write modified item positions back to RDT binary
- [ ] Open TIM file directly from toolbar (alongside RDT)

### Room connection map (the big one)
The room IDs encode stage and room number: `roomSXX` where S=stage, XX=room hex.
RDT offset[0] = camera switch table, which contains door/transition data linking rooms.
Plan:
- **apps/core/re1_room_map.py** - parse room connections from camera switch tables across all RDTs in a folder
- **apps/gui/stage_map_editor.py** - canvas showing all rooms as boxes with connection lines
  - Click a room box to load it in the room map editor
  - Drag to rearrange room order (cosmetic for now)
  - Right-click: add room, remove room, swap two rooms
- Room swap: re-index the RDT offset that references the target room ID in the camera switch table
- Room removal: zero out or redirect the camera switch entry pointing to removed room
- Room addition: duplicate an existing RDT, assign new room ID, add a connection from existing room

### Item editing
- [ ] Double-click item in map editor -> dialog: change type, amount, flags
- [ ] Item type combo box wired to RE1_ITEM_NAMES
- [ ] Write changes back to RDT binary on Save

### Texture / model viewers
- [ ] Wire TIM viewer: when RDT loaded, check offset[3] (TMD/TIM pairs) and offer to view embedded textures
- [ ] EMD viewer: basic vertex/face wireframe using QPainter (no OpenGL required for RE1 scale)

### File browser
- [ ] Left panel: folder browser for game directory, lists all .rdt files by stage
- [ ] Shows room IDs, file sizes, item counts at a glance

---

## May 22 2026 - Session 4 (all TODOs completed)

### New Files

- **apps/core/re1_room_map.py** v1
  - `scan_stage_folder()` - scans folder for .rdt files, builds StageGraph
  - `build_stage_graph()` - parses camera switch tables for door connections
  - `parse_camera_switches()` - reads RDT offset[0] switch entries
  - `swap_rooms()` - swaps two rooms, patches raw binary switch bytes
  - `remove_room()` - removes room and orphans its connections
  - `get_connected_rooms()` - returns list of directly connected rooms
  - Dataclasses: RoomConnection, RoomNode, StageGraph

- **apps/gui/stage_map_editor.py** v1
  - StageMapCanvas: QPainter room boxes with connection arrows, pan/zoom/drag
  - Right-click menu: load room, swap with another, remove from stage
  - Drag rooms to reposition. Double-click to load in room map editor.
  - StageMapToolbar: open folder button, status bar
  - StageMapWidget: combined, room_activated signal -> _load_rdt

- **apps/gui/item_edit_dialog.py** v1
  - Edit item type (combo with all 70+ RE1 items), amount, flags, X/Y/Z, rotation
  - Opens via double-click on Items tab row
  - Writes changes directly to RDTItem object

- **apps/methods/rdt_writer.py** v1
  - `write_rdt()` - patches items and collision sections in raw bytes
  - `_backup_file()` - auto-creates .bak before first overwrite
  - Only rewrites changed sections, all other bytes preserved verbatim

### Modified Files

- **ResBio_Evil_Workshop.py**
  - Middle panel: QTabWidget with Overview/Items/Cameras/Collision tabs
  - `_on_middle_tab_changed()`: repopulate table per tab
  - `_populate_collision_table()`: new
  - `_on_middle_list_double_clicked()`: opens item edit dialog on Items tab
  - `_save_file/_save_file_as`: rewritten for RDT (were referencing COL/OBJ)
  - `_open_tim_file()`: opens TIM texture directly; TIM button added to toolbar
  - Display stack page 3: StageMapWidget (replaced collision placeholder)
  - Display combo: "Stage Map" replaces "Collision"
  - `_create_left_panel()` v6: full file browser, folder open button, RDT list
  - `_browse_stage_folder()`, `_load_stage_folder()`: scan and populate
  - `_on_left_file_activated()`: double-click loads RDT

### TODO - Next session
- [ ] Test with real RE1 game files
- [ ] Wire TIM from embedded RDT offset[3] (view textures from inside RDT)
- [ ] EMD wireframe viewer (vertex/face, QPainter, page 5)
- [ ] SCD script hex browser
- [ ] Export room data to JSON for external editing
