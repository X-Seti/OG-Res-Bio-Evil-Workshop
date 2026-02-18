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
