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
