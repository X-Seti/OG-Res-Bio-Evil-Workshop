# Resident Evil 1 (PS1/PC) File Format Research

**Date:** February 18, 2026  
**Project:** ResBio-Evil-Workshop  
**Status:** Initial Research Phase

---

## Overview

Resident Evil 1 uses various file formats for game data. This doc tracks formats needed for room loading, item placement, and room editing.

**Source:** https://github.com/pmandin/reevengi-tools/wiki/Resident-Evil-1-file-formats

---

## Critical File Formats for Workshop

### 1. **RDT - Room Description** ⭐ PRIMARY
- **Purpose:** Room layout, geometry, collision data
- **Status:** PRIORITY - needed for room loading
- **Notes:** Different specs for PS1 vs PC versions
- **TODO:** Parse RDT structure, extract room data

### 2. **EMD - Enemy/Player 3D Model**
- **Purpose:** 3D model data for objects in rooms
- **Status:** SECONDARY - for item/object placement
- **Notes:** Contains vertex, face, animation data
- **TODO:** Parse EMD, understand item placement references

### 3. **TIM - Texture Image**
- **Purpose:** Texture data for rooms and models
- **Status:** SECONDARY - for visual reference
- **Notes:** PlayStation native texture format
- **TODO:** Parse TIM, display in preview

### 4. **TMD - 3D Model** (Alternative to EMD)
- **Purpose:** Generic 3D model format
- **Status:** SECONDARY - verify if used in RE1
- **TODO:** Determine if needed for RE1

### 5. **BSS - Background & Masks (PS1)**
- **Purpose:** Room background images and transparency masks
- **Status:** SECONDARY - for room visualization
- **TODO:** Parse BSS format

### 6. **PAK - Background Images (PC)**
- **Purpose:** PC version background image format
- **Status:** PC-specific, lower priority
- **TODO:** Research PAK structure

### 7. **DOR - Door Animation**
- **Purpose:** Door open/close animation data
- **Status:** TERTIARY - environment interaction
- **TODO:** Parse DOR if needed for editing

---

## File Format Details (Known)

| Format | Type | Version | Priority |
|--------|------|---------|----------|
| .RDT | Room Data | PS1/PC | ⭐⭐⭐ |
| .EMD | 3D Model | PS1/PC | ⭐⭐ |
| .TIM | Texture | PS1/PC | ⭐⭐ |
| .TMD | 3D Model | PS1/PC | ⭐⭐ |
| .BSS | Backgrounds | PS1 | ⭐⭐ |
| .PAK | Backgrounds | PC | ⭐ |
| .DOR | Door Anim | PS1/PC | ⭐ |

---

## Research Tasks

### Phase 1: RDT Format Parsing
- [ ] Find RDT format specification
- [ ] Identify room structure layout
- [ ] Extract collision data
- [ ] Map room geometry
- [ ] Parse item placement entries
- [ ] Create RDT parser module

### Phase 2: Item/Object Data
- [ ] Find item placement format within RDT
- [ ] Identify item type IDs
- [ ] Map item coordinates in room
- [ ] Understand item properties
- [ ] Create item placement editor

### Phase 3: Room Replacement
- [ ] Understand room linking/dependencies
- [ ] Plan room insertion logic
- [ ] Plan room deletion logic
- [ ] Identify breaking points (door connections, etc)
- [ ] Create room swap mechanism

### Phase 4: Visualization
- [ ] Parse TIM texture format
- [ ] Parse BSS backgrounds
- [ ] Render room layouts in preview
- [ ] Display item positions
- [ ] Create 3D viewport (optional)

---

## Known Issues & Limitations

1. **PS1 vs PC differences** - Some formats differ between versions
2. **Saturn version** - Extra 16-byte header on some files (skip for now)
3. **Compression** - Unknown if any formats are compressed
4. **File dependencies** - Rooms link to other files (need to track)

---

## Tools & Resources

- **reevengi-tools** - Reference implementation (C code)
  - GitHub: https://github.com/pmandin/reevengi-tools
  - Has working RDT, EMD, TIM parsers

- **Evil Resource Wiki** - RE1 file database
  - https://www.evilresource.com/resident-evil/files

- **TCRF (The Cutting Room Floor)** - Game internals
  - https://tcrf.net/Resident_Evil_(PlayStation)

---

## Next Steps

1. ✓ Create this research document
2. Study reevengi-tools source code for RDT parsing
3. Begin RDT parser implementation in `depends/re1_formats.py`
4. Create RDT test with sample room file
5. Build room loader in main app

---

## Notes

- Focus on PS1 version first (PC follows same format mostly)
- RDT is the critical blocker - everything depends on parsing it correctly
- Item placement data likely embedded in RDT, not separate file
- Door connections need special handling when replacing rooms
