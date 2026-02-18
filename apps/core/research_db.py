#this belongs in apps/core/research_db.py - Version: 1
# X-Seti - February18 2025 - ResBio-Evil-Workshop 1.0 - Research Database Manager
"""
Research Database Manager - Manages RE file format research and findings.
Stores entries in JSON format with categories, tags, and markdown content.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

##Methods list -
# __init__
# _load_database
# _save_database
# add_entry
# edit_entry
# delete_entry
# get_entry
# get_all_entries
# get_entries_by_category
# get_entries_by_tag
# search_entries
# export_to_markdown
# get_categories
# get_all_tags

##class ResearchDB: -

class ResearchDB: #vers 1
    """JSON-based research database for RE file format findings"""
    
    CATEGORIES = ["RE1", "RE2", "RE3", "Tools", "General"]
    DEFAULT_TAGS = ["RDT", "EMD", "TIM", "SCA", "SCD", "PS1", "PC", "Format", "Parser", "Bug"]
    
    def __init__(self, db_path: str = "research_db.json"): #vers 1
        """Initialize database"""
        self.db_path = Path(db_path)
        self.data = self._load_database()
    
    def _load_database(self) -> Dict: #vers 1
        """Load database from JSON file"""
        if self.db_path.exists():
            try:
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading database: {e}")
                return self._get_default_structure()
        return self._get_default_structure()
    
    def _get_default_structure(self) -> Dict: #vers 1
        """Get default empty database structure"""
        return {
            "version": "1.0",
            "created": datetime.now().isoformat(),
            "last_modified": datetime.now().isoformat(),
            "entries": []
        }
    
    def _save_database(self) -> bool: #vers 1
        """Save database to JSON file"""
        try:
            self.data["last_modified"] = datetime.now().isoformat()
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving database: {e}")
            return False
    
    def add_entry(self, title: str, category: str, content: str, tags: List[str] = None) -> bool: #vers 1
        """Add new research entry"""
        if not title or not category:
            return False
        
        if category not in self.CATEGORIES:
            return False
        
        entry_id = len(self.data["entries"]) + 1
        
        entry = {
            "id": entry_id,
            "title": title,
            "category": category,
            "content": content,
            "tags": tags if tags else [],
            "created": datetime.now().isoformat(),
            "modified": datetime.now().isoformat()
        }
        
        self.data["entries"].append(entry)
        return self._save_database()
    
    def edit_entry(self, entry_id: int, title: str = None, content: str = None, tags: List[str] = None) -> bool: #vers 1
        """Edit existing entry"""
        for entry in self.data["entries"]:
            if entry["id"] == entry_id:
                if title:
                    entry["title"] = title
                if content:
                    entry["content"] = content
                if tags is not None:
                    entry["tags"] = tags
                entry["modified"] = datetime.now().isoformat()
                return self._save_database()
        return False
    
    def delete_entry(self, entry_id: int) -> bool: #vers 1
        """Delete entry by ID"""
        original_count = len(self.data["entries"])
        self.data["entries"] = [e for e in self.data["entries"] if e["id"] != entry_id]
        
        if len(self.data["entries"]) < original_count:
            return self._save_database()
        return False
    
    def get_entry(self, entry_id: int) -> Optional[Dict]: #vers 1
        """Get single entry by ID"""
        for entry in self.data["entries"]:
            if entry["id"] == entry_id:
                return entry
        return None
    
    def get_all_entries(self) -> List[Dict]: #vers 1
        """Get all entries"""
        return self.data["entries"]
    
    def get_entries_by_category(self, category: str) -> List[Dict]: #vers 1
        """Get entries by category"""
        return [e for e in self.data["entries"] if e["category"] == category]
    
    def get_entries_by_tag(self, tag: str) -> List[Dict]: #vers 1
        """Get entries containing specific tag"""
        return [e for e in self.data["entries"] if tag in e.get("tags", [])]
    
    def search_entries(self, query: str) -> List[Dict]: #vers 1
        """Search entries by title and content"""
        query_lower = query.lower()
        results = []
        
        for entry in self.data["entries"]:
            if (query_lower in entry["title"].lower() or 
                query_lower in entry["content"].lower()):
                results.append(entry)
        
        return results
    
    def get_categories(self) -> List[str]: #vers 1
        """Get list of categories"""
        return self.CATEGORIES
    
    def get_all_tags(self) -> List[str]: #vers 1
        """Get all unique tags from entries"""
        tags = set()
        for entry in self.data["entries"]:
            tags.update(entry.get("tags", []))
        return sorted(list(tags))
    
    def export_to_markdown(self, output_path: str = "research_export.md") -> bool: #vers 1
        """Export all entries to markdown file"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("# ResBio-Evil-Workshop Research Database\n\n")
                f.write(f"**Exported:** {datetime.now().isoformat()}\n\n")
                
                # Group by category
                for category in self.CATEGORIES:
                    entries = self.get_entries_by_category(category)
                    if entries:
                        f.write(f"## {category}\n\n")
                        for entry in entries:
                            f.write(f"### {entry['title']}\n\n")
                            f.write(f"**Tags:** {', '.join(entry.get('tags', []))}\n\n")
                            f.write(f"**Created:** {entry['created']}\n\n")
                            f.write(f"{entry['content']}\n\n")
                            f.write("---\n\n")
            
            return True
        except Exception as e:
            print(f"Error exporting to markdown: {e}")
            return False
