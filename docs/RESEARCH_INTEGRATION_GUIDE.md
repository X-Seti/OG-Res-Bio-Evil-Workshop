# Research Tab Integration Guide

## File Locations

| File | Location | Purpose |
|------|----------|---------|
| `research_db.py` | `apps/core/` | Database manager (core functionality) |
| `research_tab.py` | `apps/components/` | GUI tab widget (UI component) |
| `research_db.json` | `root/` | Research database (persistent storage) |

---

## Installation Steps

### 1. Copy Files to Project
```
research_db.py       → ResBio_Evil_Workshop/apps/core/
research_tab.py      → ResBio_Evil_Workshop/apps/components/
research_db.json     → ResBio_Evil_Workshop/ (root)
```

### 2. Update ResBio_Evil_Workshop.py (Main GUI)

Add import at top:
```python
from apps.components.research_tab import ResearchTab
```

In the tab creation section (where other tabs are added), add:
```python
# === RESEARCH TAB ===
research_tab = ResearchTab()
research_tab.load_database()
tabs.addTab(research_tab, "Research")
```

### 3. Verify Imports in research_tab.py

Check that imports resolve:
```python
from apps.core.research_db import ResearchDB  # Update if needed
```

---

## Features

### Left Panel (Category Tree)
- **Categories:** RE1, RE2, RE3, Tools, General
- **Hierarchical Display:** Category → Entries
- **Action Buttons:** Add, Edit, Delete entry

### Right Panel (Editor & Search)
- **Search Bar:** Full-text search across title + content
- **Tag Filter:** Filter entries by tags
- **Text Editor:** Markdown support for entry content
- **Export Button:** Export all entries to markdown file

### Database Operations
- **Add Entry:** Create new research findings
- **Edit Entry:** Modify existing content
- **Delete Entry:** Remove entries with confirmation
- **Search:** Find entries by keyword
- **Export:** Save all entries to `research_export.md`

---

## JSON Database Structure

```json
{
  "version": "1.0",
  "created": "2025-02-18T...",
  "last_modified": "2025-02-18T...",
  "entries": [
    {
      "id": 1,
      "title": "Entry Title",
      "category": "RE1",
      "content": "Markdown content here...",
      "tags": ["RDT", "Format", "RE1"],
      "created": "2025-02-18T...",
      "modified": "2025-02-18T..."
    }
  ]
}
```

---

## Adding New Research

### Via GUI
1. Click **"Add Entry"** button
2. Enter title
3. Select category (RE1/RE2/RE3/Tools/General)
4. Enter content (Markdown supported)
5. Select/create tags

### Manually (JSON)
Edit `research_db.json` directly and increment entry IDs.

---

## Supported Tags (Default)

- **Format:** RDT, EMD, TIM, SCA, SCD, MD1, PLD
- **Game:** RE1, RE2, RE3, PS1, PC
- **Topic:** Parser, Bug, Format, 3D Model, Texture, Collision, Script
- **Tools:** reevengi, RDTool

Add custom tags by entering them when creating entries.

---

## Example: Adding an RDT Finding

```
Title: "RDT Camera Switch Bug"
Category: RE1
Content: 
  # Camera Switch Issues
  
  When parsing RDT camera switch offset (Offset 0), the 'from' 
  field may contain invalid values if num_cameras is incorrect.
  
  **Fix:** Validate num_cameras in header before reading switches.
  
Tags: RDT, RE1, Bug, Parser
```

---

## Exporting Research

Click **"Export All to Markdown"** to create `research_export.md`:
- Organized by category
- Includes all tags and timestamps
- Ready for sharing or documentation

---

## Development Notes

- Database persists automatically on every change
- Search is case-insensitive
- Tags are user-creatable (no fixed list)
- Markdown formatting supported in content
- Thread-safe JSON reads/writes

---

## Future Enhancements

- [ ] Import research from external markdown
- [ ] Sync research database across team
- [ ] Attach binary files to entries
- [ ] Cross-reference entries by ID
- [ ] Version history for entries

---

## Troubleshooting

**Database won't load:**
- Check `research_db.json` is in project root
- Verify JSON is valid (use online validator)
- Delete and let app recreate with defaults

**Tags not showing:**
- Tags are auto-populated from entries
- Create entries with tags first
- Clear filter combo and reload

**Export fails:**
- Check write permissions in project root
- Ensure `research_export.md` is not open elsewhere

---

**Status:** Ready for integration  
**Last Updated:** 2025-02-18
