# Resident Evil 1/2/3 File Format Reference
# X-Seti - May26 2026 - ResBio-Evil-Workshop

This document maps every file extension you'll encounter across RE1, RE2, RE3
(PS1/Saturn/GameCube/PC) to what it contains and how it relates to the others.

---

## The core idea

RE1/2/3 use **pre-rendered backgrounds** (a fixed camera photo of a 3D scene)
with **real-time 3D sprites** drawn on top (enemies, player, items, doors).
There is no single "scene file" — a room is assembled from many files:

```
One room  =  RDT  +  BSS/PAK/ADT  +  EMD files  +  TIM files  +  VAG audio
             │          │                │               │             │
           room       background      3D models       textures      sound
           logic
```

---

## Room data — the hub file

### `.RDT`  (Room DaTa)
The most important file. One per room (RE1) or two per room (RE2/RE3, one
per scenario). Contains **no raw assets** — only offsets pointing at them.

**What's inside:**
- Camera positions (eye + target vectors for each fixed camera angle)
- Collision geometry (floor rectangles, walls, slopes)
- Enemy placement (type, x/y/z, rotation, spawn conditions)
- Item placement (type, position, amount, flags)
- Area-Of-Trigger (AOT) rectangles (doors, item pickups, events)
- Camera switch zones (step into here → camera cuts)
- SCD scripts (the room's logic — locks, cutscenes, item checks)
- Pointers to audio (VAG/VB file indices)
- Pointer to TIM texture for this room

**Naming:**
```
RE1:  ROOMsrr.RDT        s=stage(1-7), rr=room hex  e.g. ROOM100.RDT
RE2:  ROOMsrrY.RDT       Y=0(Leon) or 1(Claire)     e.g. ROOM10A0.RDT
RE3:  ROOM0rrY.RDT       single scenario             e.g. ROOM0000.RDT
RE1 PC: ROOMNxxx.RDT     decimal stage prefix        e.g. ROOM1020.RDT
```

### `.ARD`  (Archive Room Data — RE1.5 prototype only)
Same role as RDT but from the unfinished 1996 Biohazard 2 prototype.
Lives in `/CD_DATA/STAGE1-7/` on the RE1.5 disc.

---

## Background images — the painted backdrop

### `.BSS`  (Background Screen Sequence — PS1)
One per room (not per camera). Contains a single MDEC-compressed video frame
— essentially a JPEG-like compressed image using the PS1 hardware video chip.
Decoded to 320×240 RGB at 16bpp.

```
BSS = PS1 MDEC bitstream → adt_decode() → 320×240 RGB555 pixels
```

**Naming:** `ROOM11C.BSS` is the background for `ROOM11C0.RDT` AND `ROOM11C1.RDT`
(both scenarios share one background per room).

### `.ADT`  (Adaptive Delta Transform — RE2 PC)
RE2 PC equivalent of BSS. Huffman+LZ77 compressed, different algorithm.
Decompresses to the same 320×240 layout as BSS.
Lives alongside the RDT files in `DATA/`.

### `.PAK`  (Packed background — RE1 PC)
RE1 PC background format. LZW-compressed image data, one `.PAK` per camera
angle (unlike BSS which is one per room). Stored in the `STAGE` folder.

---

## 3D models — the moving parts

All RE1/2/3 3D models use a **PS1 coordinate system**: Y-up, 1 unit = ~1mm,
coordinates typically in range ±30000. Models are segmented into body parts
linked by a skeleton.

### `.EMD`  (Enemy MoDel)
Main enemy model format. Contains:
- TMD geometry (vertices, normals, primitives)
- Skeleton hierarchy (bone transforms)
- Animation data (keyframe sequences)

One `.EMD` per enemy type. Named by enemy ID: `EM10.EMD` = enemy type 0x10.

### `.PLD`  (PLaYer moDel)
Player character model. Same structure as EMD but larger (player has more
detail). `PL00.PLD` = Leon, `PL01.PLD` = Claire, `PL10.PLD` = Jill etc.

### `.PLW`  (PLaYer Walk — RE1.5)
Player walk/movement data for the RE1.5 prototype.

### `.IVM`  (Item ViewModel — RE2 PS1)
Item 3D models (the spinning item you see before picking it up).
In `/PSX/ITEM_M2/`. TMD-based, one per item type.

### `.DOR`  (DOoR model — RE2 PS1)
Door and obstacle models. In `/PSX/ITEM_M1/`. Each stage has its own doors.

### `.EMW`  (Enemy Model Weapon)
Weapon attachment models for enemies and players.

### `.TMD`  (Triangular Mesh Data — PS1 raw format)
The lowest-level PS1 3D format. EMD/PLD files contain TMD data internally.
Sometimes used standalone for simple objects.

---

## Textures

### `.TIM`  (Texture IMage — PS1)
Standard PS1 texture format. Header: magic=0x10, flags=bpp+CLUT flag.

**BPP modes:**
```
0 = 4bpp  (16 colours, needs CLUT)
1 = 8bpp  (256 colours, needs CLUT)
2 = 16bpp (RGB555, no CLUT needed) ← most room/enemy textures
3 = 24bpp (RGB888, rare)
```

**CLUT** = Colour LookUp Table (the palette). Stored before the pixel data
if `flags & 0x08`. CLUT is 16 or 256 entries of RGB555 values.

Key TIM files:
```
STATUS.TIM    inventory/item icons (RE2 PS1 sprite sheet)
ITEMALL.PIX   all item icons (RE1 PS1)
TYPE00.TIM    room texture atlas (RE1 PS1, 153KB)
```

### `.PIX`  (raw PIXel data)
Raw VRAM dump, no TIM header. 16bpp RGB555. Must know dimensions externally.
`ITEM_ALL.PIX` = 240×180, contains all RE1 item icons in a 10-wide grid.

### `.RGB`  (Raw RGB)
Raw 24bpp or 16bpp image data used for subtitle/overlay graphics.

---

## Audio

RE's audio system is layered: background music (streamed XA/BGM), room sound
effects (VAG samples loaded per-stage), and voice (pre-compressed VB banks).

### `.VAG`  (Voice Audio Group — PS1 standard)
Single PS1 ADPCM audio sample with a `VAGp` header.
4-byte magic `VAGp`, then ADPCM data at 28 bytes per block.
Each block: 2 header bytes + 28 sample bytes = 28 decoded 16-bit samples.
Sample rate stored in header (usually 22050Hz).

### `.VB`  (Voice Bank — raw ADPCM)
Like VAG but without the per-sample `VAGp` headers. Raw ADPCM stream
for multiple samples packed together. Paired with a `.VH` or `.HED` header
file that gives offsets to each sample within the bank.

### `.VH` / `.HED`  (Voice Header / Header EDit)
Index file for VB data. Contains uint32 offsets to each sample.
`.VH` = standard (RE1), `.HED` = RE2 variant naming.

### `.HSB`  (Heuristic Sound Bank — Biohazard specific)
Biohazard/RE2 sound bank format. Can contain VAGp-headered samples or
raw ADPCM. Scan for `VAGp` magic to find samples, fall back to offset 0x20.

### `.XAS`  (XA audio Stream)
CD-ROM XA format background music. Interleaved on the disc between data
sectors. Not stored as a file — read directly from the disc by the CD
audio hardware. Cannot be extracted as a standalone file from most disc images.

### `.WAV`  (PC audio)
Standard PCM WAV files used in RE1/RE2/RE3 PC versions.

### `.SND`  (SouND container)
Sound container that may wrap VAG samples. Scan for `VAGp` magic inside.

---

## Scripts

### `.SCD`  (Script Code Data)
RE's custom bytecode scripting language. Two script functions per room:
- **Init script** (SCD0): runs once when the room loads (place items, set flags)
- **Run script** (SCD1): runs every frame (check triggers, move enemies)

SCD opcodes are 1-2 bytes. Notable ones:
```
0x00 NOP         0x01 EVT_END      0x06 SLEEP
0x08 GOSUB       0x18 ITEM_SET     0x22 DOOR_SET
0x2B AOT_SET     0x4E ENEMY_SET    0x67 IF / ELSE / ENDIF
```
SCD is stored **inside the RDT** at offsets pScrl (init) and pScdx (run).

---

## Disc-level formats

### `.BIN` / `.ISO` / `.CCD+IMG+SUB` / `.CUE+BIN`
Disc image formats. The actual game data is in `Mode 2 Form 1` sectors
(2336 bytes raw per sector, 2048 bytes payload). The PS1 BIOS reads the
ISO9660 filesystem from these.

### `SYSTEM.CNF`
PS1 disc boot file. Contains the disc ID (e.g. `SLUS_009.23`) used to
identify the game version and region.

---

## PC-specific

### `ROFS*.DAT`  (RE3 PC)
RE3 PC stores all game data in compressed archive files (`ROFS00.DAT` through
`ROFS09.DAT`). Must be unpacked before individual files are accessible.
Our unpacker handles these.

### `BIO.EXE` / `BIO2.EXE` / `BIO3.EXE`
The game executables for RE1/RE2/RE3 PC. Contain compiled game logic,
string tables, and some hardcoded room/item data. Require Wine on Linux.

---

## Quick reference table

| Extension | Game   | Platform | Category    | Contains                          |
|-----------|--------|----------|-------------|-----------------------------------|
| .RDT      | 1/2/3  | All      | Room        | Logic, cameras, collision, items  |
| .ARD      | 1.5    | PS1      | Room        | RE1.5 prototype room data         |
| .BSS      | 1/2/3  | PS1      | Background  | MDEC compressed 320×240 image     |
| .ADT      | 2      | PC       | Background  | Huffman+LZ compressed background  |
| .PAK      | 1      | PC       | Background  | LZW background (one per camera)   |
| .TIM      | 1/2/3  | PS1      | Texture     | PS1 standard texture (4/8/16bpp)  |
| .PIX      | 1      | PS1      | Texture     | Raw VRAM pixels (no header)       |
| .EMD      | 1/2/3  | PS1      | Model       | Enemy model + skeleton + anims    |
| .PLD      | 1/2/3  | PS1      | Model       | Player model + skeleton + anims   |
| .IVM      | 2      | PS1      | Model       | Item pickup 3D model              |
| .DOR      | 2      | PS1      | Model       | Door/obstacle model               |
| .TMD      | 1/2/3  | PS1      | Model       | Raw PS1 triangle mesh             |
| .VAG      | 1/2/3  | PS1      | Audio       | Single ADPCM sample (VAGp header) |
| .VB       | 1/2/3  | PS1      | Audio       | Raw ADPCM sample bank             |
| .VH/.HED  | 1/2/3  | PS1      | Audio       | Index/offsets for VB bank         |
| .HSB      | 2      | PS1      | Audio       | Biohazard sound bank              |
| .XAS      | 1/2/3  | PS1      | Audio       | XA background music stream        |
| .WAV      | 1/2/3  | PC       | Audio       | PCM audio (PC versions)           |
| .SCD      | 1/2/3  | All      | Script      | Room bytecode (embedded in RDT)   |
| .PLW      | 1.5    | PS1      | Data        | Player walk data (prototype)      |
| .DOx      | 1.5    | PS1      | Model       | Door models per stage (prototype) |

---

## RE2 PSX disc structure

RE2 PSX splits room data across two areas of the disc:

```
PL0/                          Leon A scenario
  RDT/ROOMxxxx.RDT            Leon rooms: items, enemies, scripts, cameras, collision
  PLD/PL00.PLD                Leon player model
  VOICE/VOICE00.XAS           Leon voice lines

PL1/                          Claire B scenario  
  RDT/ROOMxxxx.RDT            Claire rooms (different items/enemies, same geometry)

CD_DATA/                      Shared by both scenarios
  STAGE1/                     Police Station
    R10A.ARD  R10A.BSS        Room 0A: cameras+collision + background frames
    R10B.ARD  R10B.BSS        Room 0B
    ...
  STAGE2/                     Sewers
    R20A.ARD  R20A.BSS
    R218.ARD  R218.BSS        Room 18 (sewer corridor, 16 cameras)
  STAGE3/                     Laboratory
  STAGE4-7/                   Other stages
  SOUND/                      BGM, SFX banks
  DOOR/                       Door models
  DATA/                       Shared textures, item icons
```

**ARD vs RDT — same binary format, different content:**

| File | Path | Contains |
|------|------|----------|
| Rxxx.ARD | CD_DATA/STAGE*/ | Cameras + collision only (shared, no items/enemies) |
| ROOMxxxx.RDT | PL0/RDT/ or PL1/RDT/ | Full room: cameras + collision + items + enemies + scripts |

The ARD files are the geometry-only shared version. Both Leon and Claire see the
same room layout and camera angles (defined in ARD), but different item placements
and enemy counts (defined in scenario RDT).

**ARD naming convention:**
```
R[stage][room_hex]  →  e.g. R218 = stage 2, room 0x18
Corresponds to:         ROOM218x.RDT in PL0/PL1 (x = scenario 0 or 1)
```

**BSS naming:**
```
R10A.BSS = backgrounds for room 0A in stage 1
Contains multiple camera angle frames (16 × 0x10000 bytes each)
One BSS file serves both scenarios (shared background)
```

## How a room loads (runtime sequence)

```
1. Game reads SYSTEM.CNF → knows disc region/version
2. Loads RDT for current room number
3. RDT header gives offset to SCA → load collision geometry
4. RDT gives camera positions → set up camera frustums
5. SCD init script runs:
   - AOT_SET opcodes place trigger rectangles
   - ITEM_SET opcodes place item models (IVM) at world positions
   - ENEMY_SET opcodes spawn enemy data
6. Game loads BSS/PAK/ADT background for current camera angle
   → decompresses → uploads to VRAM as background
7. Loads TIM texture for this room (room-specific palette)
8. Enemy EMD models loaded, TIM textures applied
9. Player PLD model loaded
10. Per-frame: render background, then 3D models on top
    → fixed camera = pre-rendered world, sprite characters
```

---

## Why RE is different from GTA (DFF/TXD)

GTA uses a real-time 3D engine — every asset is a mesh with a texture.
RE1/2/3 uses a **hybrid engine**:

- The **world** is a pre-rendered image (BSS/ADT/PAK) — not a 3D model at all
- The **collision** is a separate mathematical description (SCA floor rects)
- Only the **characters** are real-time 3D (EMD/PLD)
- The **camera** is completely fixed per-room

This is why:
- Rooms look photorealistic despite running on PS1 hardware
- You can't change camera angles freely
- Enemy/player movement is restricted to collision floor rectangles
- The same room can look different in different games just by swapping the BSS

---

*Sources: re1.h / re1_formats.py (RE1-Mod-SDK, Gemini-Loboto3),
Room.h (RE2-Mod-tools, Gemini-Loboto3), reevengi-tools (Patrice Mandin),
RE modding community research*
