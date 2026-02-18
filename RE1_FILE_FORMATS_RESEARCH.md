# Resident Evil 1 (PS1/PC) File Formats Research

**Project:** ResBio-Evil-Workshop  
**Research Date:** February 2025  
**Source:** reevengi-tools Wiki, RE Modding Forums, Just Solve Archive  
**Status:** COMPLETED - Ready for Parser Implementation

---

## Overview

Resident Evil 1 (PS1/PC) uses a series of interconnected file formats. The primary file is **RDT** (Room Description Table), which defines a single room and references other file types (models, textures, scripts, collision).

**Key File Types (Priority Order):**
1. **RDT** - Room data (PRIMARY)
2. **EMD** - Enemy/NPC 3D models
3. **TIM** - Texture images
4. **SCA** - Collision boundaries
5. **SCD** - Scripts (initialization/execution)

---

## 1. RDT Format (Room Description Table)

### Purpose
Defines a complete game room: camera positions, background images, 3D objects, collision, items, enemies, scripts.

### File Naming
- `roomSXX0.rdt` or `roomSXX1.rdt`
- S = game stage/scenario
- XX = location number (hex)

### Data Types
All values stored in **Little-Endian** order.

### Header Structure
```
Offset  Size  Type              Field
------  ----  ----------------  ------
0x00    1     unsigned char     unknown0
0x01    1     unsigned char     num_cameras        (count of camera angles)
0x02    1     unsigned char     num_sound_banks
0x03    3     char[3]           unknown1
0x06    6     unsigned short[3] unknown2
0x0C    12    rdt_header_part_t unknown3[3]

typedef struct {
  long unknown_pos_x;
  long unknown_pos_y;
  long unknown_pos_z;
  unsigned long unknown0[2];
} rdt_header_part_t;
```

### Offset Array
Following the header (offset 0x20), there are **19 absolute offsets** to data sections:

```
Offset#  Section                    Purpose
-------  ----------------------     -------
0        Camera switches            Camera angle changes
1        Collision boundaries       SCA collision mesh data
2        Items/obstacles            Item placement, obstacles
3        TMD/TIM pairs              3D model + texture references
4        Unknown                    
5        Unknown                    
6        Initialization script      SCD bytecode (setup)
7        Execution script           SCD bytecode (runtime)
8        Event scripts              EVT bytecode (special events)
9        Skeleton                   Skeletal animation data
10       Skeleton animation steps   Animation frame data
11-12    Unknown                    
13       Animation for room         Room-level animations
14-18    Various (camera, effects)  
```

### Camera Data Structure
Located at offset 0x94 in file. Contains **num_cameras** entries:

```c
typedef struct {
  long masks_offset;           // Offset to mask definition
  long tim_masks_offset;       // Offset to TIM file for masks (0 if none)
  long camera_from_x;          // Camera position (from)
  long camera_from_y;
  long camera_from_z;
  long camera_to_x;            // Camera look-at target
  long camera_to_y;
  long camera_to_z;
  long unknown1[3];
} rdt_camera_t;
```

### Collision Boundaries (SCA)
Header (24 bytes):
```c
typedef struct {
  unsigned short Cx;           // Ceiling X
  unsigned short Cz;           // Ceiling Z
  unsigned long counts[5];     // Number of objects per type
} rdt_sca_header_t;
```

Boundary entries follow header.

### Item Placement Data
Stored in offset 2 section. Contains item type, position, rotation, and flags.

---

## 2. EMD Format (Enemy/NPC 3D Models)

### Purpose
Contains complete 3D model data: vertices, normals, triangles, animations, textures.

### Structure Overview
Directory located at **end of file** (filesize - 16 bytes):
```c
typedef struct {
  unsigned long offset0;  // Section 0
  unsigned long offset1;  // Section 1
  unsigned long offset2;  // Section 2
  unsigned long offset3;  // Section 3
} emd_directory_t;
```

### Section 0: Model Geometry
Contains all 3D mesh data.

**Vertex Structure:**
```c
typedef struct {
  signed short x;          // Coordinates (fixed-point)
  signed short y;
  signed short z;
  signed short zero;       // Padding
} emd_vertex_t;
```

**Normal Structure:** (Same format as vertex)

**Triangle Structure:**
```c
typedef struct {
  unsigned short vertex_indices[3];
  // + normal, texture, color data...
} emd_triangle_t;
```

**Model Entry:**
```c
typedef struct {
  unsigned long vertex_offset;    // Offset to vertex array
  unsigned long vertex_count;
  unsigned long normal_offset;
  unsigned long normal_count;
  unsigned long tri_offset;       // Offset to triangle array
  unsigned long tri_count;
  unsigned long dummy;
} emd_model_triangles_t;
```

### Section 1: Skeleton & Animation
Contains bone data and skeletal animations.

**Animation Header:**
```c
typedef struct {
  short x_offset;
  short y_offset;
  short z_offset;
  short x_speed;
  short y_speed;
  short z_speed;
  short angles[3*15];  // Rotation angles per bone (max 15 bones)
  short unknown;
} emd1_skel_anim_t;
```

### Section 2: Animation Metadata
```c
typedef struct {
  unsigned short count;   // Indices to process
  unsigned short offset;  // Byte offset in Section 1 data
} emd_anim_header_t;
```

### Section 3: Texture (Embedded TIM)
Sony PSX TIM file format (texture image).

---

## 3. TIM Format (Texture Images)

### Purpose
PSX texture format. Contains color palettes and pixel data.

### Header (8 bytes minimum)
```c
typedef struct {
  unsigned long magic;        // 0x10000000 (little-endian)
  unsigned long flags;        // Bits indicate: BPP (bits per pixel), palette, etc.
} tim_header_t;
```

### Color Modes
- **4-bit (16 colors)** - Palletized
- **8-bit (256 colors)** - Palletized
- **16-bit** - Direct color (15-bit RGB + 1-bit transparency)
- **24-bit** - RGB (3 bytes per pixel)

### Structure
```
TIM Header (8 bytes)
  ↓
[Palette Data] (if palletized)
  ↓
Pixel Data
  ↓
[CLUT] (Color Lookup Table, if palletized)
```

---

## 4. SCA Format (Collision Boundaries)

### Purpose
Defines collision mesh for room geometry. Used for player movement and hit detection.

### Structure
**Header (24 bytes):**
```c
typedef struct {
  unsigned short Cx;      // Ceiling X position
  unsigned short Cz;      // Ceiling Z position
  unsigned long counts[5];  // Count of 5 object types
} sca_header_t;
```

**Collision Objects:**
- Walls
- Floors
- Doors
- Obstacles
- Unknown type

Each object type has variable-length entries defining polygons/areas.

---

## 5. SCD Format (Scripts)

### Purpose
Bytecode scripts for room initialization, runtime behavior, and events.

### Structure
**Initialization Script (Offset 6):**
- Single script
- Runs once when room loads
- Format: `unsigned short length` + bytecode

**Execution Script (Offset 7):**
- Continuous execution
- Updates room state each frame
- Same format

**Event Scripts (Offset 8):**
- Triggered by specific events
- Multiple independent scripts

### Bytecode Language
Operates on a stack-based VM:
- Push/pop values
- Function calls
- Conditional branches
- Variable assignments

**Common Operations:**
- Camera control
- NPC spawning
- Door unlock/lock
- Item placement
- Effect triggers

---

## 6. Supporting Formats

### DOR (Door Animation)
Door sprites and animation frames.

### ESP (Effect Sprites)
Visual effects (fire, water, etc.).

### EVT (Event Data)
Complex event definitions (cutscenes, puzzles).

### BSS (PS1 Only)
Background images with embedded masks.

### PAK (PC Only)
Background images (PAK format).

---

## Implementation Priority

### Phase 1: Core RDT Parser (PRIORITY)
- [x] Header parsing
- [x] Offset array reading
- [x] Camera data extraction
- [ ] Collision boundary parsing
- [ ] Item placement loading

### Phase 2: EMD Model Parser
- [ ] Directory reading
- [ ] Vertex/normal/triangle loading
- [ ] Skeletal animation parsing
- [ ] Texture integration

### Phase 3: Texture & Image Support
- [ ] TIM parsing
- [ ] Color mode handling
- [ ] Palette application

### Phase 4: Script Support
- [ ] SCD bytecode interpretation
- [ ] Script execution environment
- [ ] Event triggering

### Phase 5: Visualization
- [ ] 3D viewport rendering
- [ ] Model animation playback
- [ ] Collision visualization

---

## Data Type Reference

### Fixed-Point Numbers
Coordinates in EMD use fixed-point:
- Typically 12.4 or 16.0 format
- Divide by 4096 for world units
- Range: -32768 to 32767 (signed short)

### Angles
- Stored as signed shorts
- 0x0000 = 0°, 0x4000 = 90°
- 0x8000 = 180°, 0xC000 = 270°
- Formula: degrees = (value / 0x10000) * 360

### Colors
- **16-bit mode:** RGBA (5:5:5:1)
- **24-bit mode:** RGB (8:8:8)
- **Palletized:** Index into CLUT

---

## Known Tools Reference

### reevengi-tools
- **GitHub:** pmandin/reevengi-tools
- **RDT Extractor:** Extracts offsets and sections
- **EMD Viewer:** RE1MV (Resident Evil 1 Model Viewer)
- **TIM Tools:** Various converters (TIM↔BMP)

### RDTool
- Extracts RDT contents
- Creates folder structure: CAMERA/, EFFECT/, OBJECT/, SCRIPT_01/, SCRIPT_02/

### RE1MV (RE1 Model Viewer)
- Views EMD files
- Plays animations
- Exports to OBJ format
- Imports modified meshes

---

## PS1 vs PC Differences

### Same
- RDT structure and offsets
- EMD format
- TIM format

### Different (PS1 Only)
- BSS backgrounds (instead of PAK)
- Slightly different file paths
- Optional 16-byte headers on Saturn version

### Different (PC Only)
- PAK backgrounds (instead of BSS)
- No built-in models (some extracted separately)

---

## Example File Locations

**PS1 Game Structure:**
```
BIOHAZARD/ (game root)
├── STAGE/ (rooms)
│   ├── ROOM*.RDT
│   ├── room*.BSS (backgrounds)
│   └── room*.BIN (archives)
├── ENEMY/ (character models)
│   ├── EM*.EMD
│   └── CHAR*.EMD
└── EVENT/ (cutscenes)
    └── various EVT files
```

**PC Game Structure:**
```
BIOHAZARD/ (game root)
├── ROOM*/ (rooms, extracted from BIN)
│   ├── ROOM*.RDT
│   ├── *.PAK (backgrounds)
│   └── various image files
└── EMD/ (models)
    └── EM*.EMD
```

---

## Testing Notes

- **Minimum Viable RDT:** Need num_cameras, offset array
- **First Success:** Parse camera positions from single RDT
- **Validation:** Verify offsets point to valid data (magic headers)
- **Performance:** RDT files typically 50KB-500KB

---

## References

- reevengi-tools Wiki: https://github.com/pmandin/reevengi-tools/wiki
- Just Solve Archive: http://justsolve.archiveteam.org/
- RE Modding Forum: RE 1 2 3 - Modding Forum
- RDT Format Documentation: Comprehensive community research

---

**Next Step:** Implement `re1_formats.py` parser module in `depends/` folder.
