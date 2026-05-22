# ResBio-Evil-Workshop

A PyQt6-based editor and room viewer for Resident Evil 1, 2, and 3 (PS1 and PC versions).

**Author:** X-Seti  
**Status:** Active development - Phase 2 (parsers and room editor)  
**GitHub:** https://github.com/X-Seti/OG-Res-Bio-Evil-Workshop

---

## What it does

ResBio-Evil-Workshop lets you open, inspect, and edit the binary game files that make up Resident Evil rooms:

- Load `.rdt` room files and see all embedded data (cameras, items, collision boundaries)
- View rooms as a 2D top-down map - collision geometry, camera positions, item placements
- Drag items to new positions in the map editor
- View PSX TIM textures embedded in or alongside room files
- Research database for documenting file format findings

Planned features (in order):
- Room connection map - see how rooms link together and reorder them
- Add, remove, and swap rooms in a stage
- Edit item types, positions, amounts
- Export/import room data
- EMD model viewer
- SCD script browser

---

## File formats supported

| Format | Purpose | Status |
|--------|---------|--------|
| RDT | Room Description Table - complete room data | Parser done |
| TIM | PSX texture image | Parser done |
| EMD | 3D models (RE1) | Parser stub |
| SCA | Collision boundaries | Parsed inside RDT |
| SCD | Room scripts | Offset table only |
| BSS | PS1 backgrounds | Planned |
| PAK | PC backgrounds | Planned |

---

## Running

Requirements: Python 3.10+, PyQt6

```
pip install PyQt6
python3 launcher.py
```

Then click **Open** and select a `.rdt` file from your RE1/RE2/RE3 game files.

---

## Game file locations

**PS1 (BIOHAZARD / Resident Evil disc):**
```
STAGE/   - room*.RDT files
ENEMY/   - EM*.EMD character models
```

**PC (extracted from CD or installed):**
```
ROOM*/   - ROOM*.RDT + *.PAK backgrounds
EMD/     - EM*.EMD models
```

---

## Project layout

```
launcher.py                          - entry point
apps/
  core/
    re1_formats.py                   - RDT/TIM/EMD/SCA binary parsers
    research_db.py                   - research notes database
  components/
    ResBio_Evil_Workshop/
      ResBio_Evil_Workshop.py        - main GUI window
      depends/
        svg_icon_factory.py
        img_debug_functions.py
  gui/
    room_map_editor.py               - 2D top-down room map widget
    tim_viewer.py                    - PSX TIM texture viewer
  methods/
    rdt_loader.py                    - loads RDT into GUI panels
    research_tab.py                  - research database GUI
    resbio_svg_icons.py              - SVG icon factory
  themes/                            - JSON theme files
  utils/
    app_settings_system.py           - theme and settings manager
reevengi-tools/                      - reference C tools (pmandin)
RE1_FILE_FORMATS_RESEARCH.md         - format documentation
ChangeLog.md
```

---

## Reference

- [reevengi-tools](https://github.com/pmandin/reevengi-tools) - open source RE file tools, format specs
- RE modding community wikis and forums
