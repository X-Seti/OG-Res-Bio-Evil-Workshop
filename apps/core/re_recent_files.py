#!/usr/bin/env python3
#this belongs in apps/core/re_recent_files.py - Version: 1
# X-Seti - May22 2026 - ResBio-Evil-Workshop - Recent Files & Game Paths
"""
Manages recently opened files and registered game installation paths.
Persists via AppSettings current_settings JSON.

recent_files: list of up to MAX_RECENT dicts {path, room_id, game, timestamp}
game_paths:   dict of {label: path} for known game installations
              e.g. {"RE1 PS1": "/mnt/games/re1", "RE2 PC": "/home/x2/re2pc"}
"""

import os
from datetime import datetime
from typing import List, Dict, Optional, TYPE_CHECKING

MAX_RECENT = 10

##Methods list -
# add_recent_file
# get_recent_files
# clear_recent_files
# add_game_path
# remove_game_path
# get_game_paths
# save
# load

##class RecentFilesManager:


class RecentFilesManager: #vers 1

    def __init__(self, app_settings=None): #vers 1
        self._settings = app_settings
        self._recent: List[Dict] = []
        self._game_paths: Dict[str, str] = {}
        self.load()

    def load(self): #vers 1
        """Load from app_settings current_settings."""
        if not self._settings or not hasattr(self._settings, 'current_settings'):
            return
        s = self._settings.current_settings
        self._recent = list(s.get('recent_files', []))
        self._game_paths = dict(s.get('game_paths', {}))

    def save(self): #vers 1
        """Persist to app_settings and write settings file."""
        if not self._settings or not hasattr(self._settings, 'current_settings'):
            return
        self._settings.current_settings['recent_files'] = self._recent[:MAX_RECENT]
        self._settings.current_settings['game_paths']   = self._game_paths
        try:
            self._settings.save_settings()
        except Exception as e:
            print(f"RecentFiles: save error: {e}")

    def add_recent_file(self, path: str, room_id: str = '',
                        game: str = '') -> None: #vers 1
        """Add a file to the recent list. Moves to top if already present."""
        if not path or not os.path.exists(path):
            return
        # Remove existing entry for same path
        self._recent = [r for r in self._recent if r.get('path') != path]
        # Insert at top
        self._recent.insert(0, {
            'path':      path,
            'room_id':   room_id or os.path.splitext(os.path.basename(path))[0].upper(),
            'game':      game,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M'),
        })
        self._recent = self._recent[:MAX_RECENT]
        self.save()

    def get_recent_files(self) -> List[Dict]: #vers 1
        """Return list of recent file dicts, skipping missing files."""
        return [r for r in self._recent if os.path.exists(r.get('path', ''))]

    def clear_recent_files(self): #vers 1
        self._recent = []
        self.save()

    def add_game_path(self, label: str, path: str): #vers 1
        """Register a game installation path."""
        if label and path and os.path.isdir(path):
            self._game_paths[label] = path
            self.save()

    def remove_game_path(self, label: str): #vers 1
        self._game_paths.pop(label, None)
        self.save()

    def get_game_paths(self) -> Dict[str, str]: #vers 1
        """Return dict of registered game paths (label -> path)."""
        return {k: v for k, v in self._game_paths.items() if os.path.isdir(v)}

    def suggest_game_label(self, folder_path: str) -> str: #vers 1
        """Guess a label for a game folder from its contents."""
        from apps.core.re_unpacker import detect_game_version, GameVersion
        try:
            ver = detect_game_version(folder_path)
            if ver != GameVersion.UNKNOWN:
                return ver.value
        except Exception:
            pass
        return os.path.basename(folder_path)
