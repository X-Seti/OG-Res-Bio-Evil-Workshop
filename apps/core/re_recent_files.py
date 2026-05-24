#!/usr/bin/env python3
#this belongs in apps/core/re_recent_files.py - Version: 2
# X-Seti - May22 2026 - ResBio-Evil-Workshop - Recent Files & Game Paths
"""
Manages recently opened files, disc paths, and game installation paths.
Persists via AppSettings JSON and own fallback file.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

MAX_RECENT = 10

_FALLBACK_FILE = Path.home() / '.config' / 'resbio-evil-workshop' / 'recent.json'

##Methods list -
# load
# save
# add_recent_file
# get_recent_files
# clear_recent_files
# add_recent_disc
# get_recent_discs
# add_game_path
# remove_game_path
# get_game_paths
# suggest_game_label

##class RecentFilesManager:


class RecentFilesManager: #vers 2

    def __init__(self, app_settings=None): #vers 2
        self._settings = app_settings
        self._recent: List[Dict] = []
        self._recent_discs: List[str] = []
        self._game_paths: Dict[str, str] = {}
        self.load()

    def load(self): #vers 2
        """Load from app_settings first, then fallback JSON."""
        if self._settings and hasattr(self._settings, 'current_settings'):
            s = self._settings.current_settings
            self._recent       = list(s.get('recent_files', []))
            self._game_paths   = dict(s.get('game_paths', {}))
            self._recent_discs = list(s.get('recent_discs', []))
            if self._recent or self._game_paths or self._recent_discs:
                return
        # Fallback: own JSON
        try:
            if _FALLBACK_FILE.exists():
                with open(_FALLBACK_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self._recent       = list(data.get('recent_files', []))
                self._game_paths   = dict(data.get('game_paths', {}))
                self._recent_discs = list(data.get('recent_discs', []))
        except Exception as e:
            print(f"RecentFiles: load error: {e}")

    def save(self): #vers 2
        """Save to app_settings AND own JSON file."""
        data = {
            'recent_files':  self._recent[:MAX_RECENT],
            'game_paths':    self._game_paths,
            'recent_discs':  self._recent_discs[:MAX_RECENT],
        }
        if self._settings and hasattr(self._settings, 'current_settings'):
            self._settings.current_settings.update(data)
            try:
                self._settings.save_settings()
            except Exception as e:
                print(f"RecentFiles: settings save error: {e}")
        # Always write fallback
        try:
            _FALLBACK_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(_FALLBACK_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"RecentFiles: fallback save error: {e}")

    # --- RDT recent files ---

    def add_recent_file(self, path: str, room_id: str = '',
                        game: str = '') -> None: #vers 1
        if not path or not os.path.exists(path):
            return
        self._recent = [r for r in self._recent if r.get('path') != path]
        self._recent.insert(0, {
            'path':      path,
            'room_id':   room_id or os.path.splitext(os.path.basename(path))[0].upper(),
            'game':      game,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
        })
        self._recent = self._recent[:MAX_RECENT]
        self.save()

    def get_recent_files(self) -> List[Dict]: #vers 1
        return [r for r in self._recent if os.path.exists(r.get('path', ''))]

    def clear_recent_files(self): #vers 1
        self._recent = []
        self.save()

    # --- Disc recent files ---

    def add_recent_disc(self, path: str): #vers 1
        """Add a disc image path to recent discs."""
        if not path or not os.path.exists(path):
            return
        self._recent_discs = [p for p in self._recent_discs if p != path]
        self._recent_discs.insert(0, path)
        self._recent_discs = self._recent_discs[:MAX_RECENT]
        self.save()

    def get_recent_discs(self) -> List[str]: #vers 1
        return [p for p in self._recent_discs if os.path.exists(p)]

    # --- Game paths ---

    def add_game_path(self, label: str, path: str): #vers 1
        if label and path and os.path.isdir(path):
            self._game_paths[label] = path
            self.save()

    def remove_game_path(self, label: str): #vers 1
        self._game_paths.pop(label, None)
        self.save()

    def get_game_paths(self) -> Dict[str, str]: #vers 1
        return {k: v for k, v in self._game_paths.items() if os.path.isdir(v)}

    def suggest_game_label(self, folder_path: str) -> str: #vers 1
        from apps.core.re_unpacker import detect_game_version, GameVersion
        try:
            ver = detect_game_version(folder_path)
            if ver != GameVersion.UNKNOWN:
                return ver.value
        except Exception:
            pass
        return os.path.basename(folder_path)
