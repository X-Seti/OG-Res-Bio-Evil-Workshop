#!/usr/bin/env python3
#this belongs in apps/core/re_asset_loader.py - Version: 1
# X-Seti - May22 2026 - ResBio-Evil-Workshop - Stage Asset Loader
"""
Stage Asset Loader - Loads all assets for a stage folder in game order.
Priority: RDTs first, then backgrounds, then models.
Uses a thread pool so the UI stays responsive.

The game loads assets in this order:
1. Room RDT (collision, items, cameras, scripts)
2. Background images (one per camera angle)
3. Enemy/character models (EMD)
4. Effect sprites (ESP)
5. Sound banks

We follow the same order so the most important data is available first.
"""

import os
from typing import Dict, List, Optional, Callable, Tuple
from dataclasses import dataclass, field
from PyQt6.QtCore import QThread, QObject, pyqtSignal

from apps.core.re1_formats import parse_rdt, RDTFile
from apps.core.re_backgrounds import find_backgrounds_for_rdt, load_background, BackgroundImage
from apps.core.re_room_names import get_room_name_or_id

##Methods list -
# load_stage_assets
# cancel

##class StageAsset:
##class StageAssets:
##class StageAssetLoader:


@dataclass
class StageAsset: #vers 1
    """A single loaded asset (RDT, background, model)."""
    room_id: str
    asset_type: str       # "rdt", "background", "model"
    path: str
    camera_index: int = 0
    rdt: Optional[RDTFile] = None
    background: Optional[BackgroundImage] = None
    loaded: bool = False
    error: str = ""


@dataclass
class StageAssets: #vers 1
    """All assets for a stage, indexed by room_id."""
    folder_path: str
    rdts: Dict[str, RDTFile] = field(default_factory=dict)
    backgrounds: Dict[str, List[BackgroundImage]] = field(default_factory=dict)
    room_order: List[str] = field(default_factory=list)   # load order
    errors: List[str] = field(default_factory=list)

    @property
    def room_count(self) -> int:
        return len(self.rdts)

    def get_background(self, room_id: str, camera: int = 0) -> Optional[BackgroundImage]:
        bgs = self.backgrounds.get(room_id, [])
        if camera < len(bgs):
            return bgs[camera]
        return bgs[0] if bgs else None

    def room_name(self, room_id: str) -> str:
        return get_room_name_or_id(room_id)


class StageAssetLoader(QObject): #vers 1
    """Loads all stage assets in a background thread."""

    progress    = pyqtSignal(str, int, int)   # message, done, total
    rdt_loaded  = pyqtSignal(str, object)     # room_id, RDTFile
    bg_loaded   = pyqtSignal(str, int, object) # room_id, cam_idx, BackgroundImage
    finished    = pyqtSignal(object)          # StageAssets
    error       = pyqtSignal(str)

    def __init__(self, folder_path: str,
                 load_backgrounds: bool = True,
                 max_cameras: int = 3): #vers 1
        super().__init__()
        self.folder_path    = folder_path
        self.load_backgrounds = load_backgrounds
        self.max_cameras    = max_cameras
        self._cancelled     = False
        self._assets        = StageAssets(folder_path=folder_path)

    def cancel(self): #vers 1
        self._cancelled = True

    def run(self): #vers 1
        """Main loader - call via QThread.started signal."""
        try:
            self._load_all()
        except Exception as e:
            self.error.emit(str(e))

    def _load_all(self): #vers 1
        folder = self.folder_path
        if not os.path.isdir(folder):
            self.error.emit(f"Not a directory: {folder}")
            return

        # Collect RDT files
        rdt_files = sorted([
            f for f in os.listdir(folder) if f.upper().endswith('.RDT')
        ])

        total_steps = len(rdt_files)
        if self.load_backgrounds:
            total_steps += len(rdt_files) * self.max_cameras

        done = 0

        # Step 1: Load all RDTs
        for filename in rdt_files:
            if self._cancelled:
                break
            full_path = os.path.join(folder, filename)
            room_id = os.path.splitext(filename)[0].upper()
            self.progress.emit(f"Loading RDT: {filename}", done, total_steps)
            try:
                rdt = parse_rdt(full_path)
                self._assets.rdts[room_id] = rdt
                self._assets.room_order.append(room_id)
                self.rdt_loaded.emit(room_id, rdt)
                if not rdt.valid:
                    self._assets.errors.append(f"{room_id}: {'; '.join(rdt.parse_errors)}")
            except Exception as e:
                self._assets.errors.append(f"{room_id}: {e}")
            done += 1

        # Step 2: Load backgrounds for each room
        if self.load_backgrounds and not self._cancelled:
            for room_id in list(self._assets.room_order):
                if self._cancelled:
                    break
                rdt = self._assets.rdts.get(room_id)
                if not rdt:
                    continue
                bg_paths = find_backgrounds_for_rdt(rdt.file_path)
                room_bgs = []
                for cam_idx, bg_path in enumerate(bg_paths[:self.max_cameras]):
                    if self._cancelled:
                        break
                    self.progress.emit(
                        f"Loading background: {os.path.basename(bg_path)}",
                        done, total_steps
                    )
                    try:
                        bg = load_background(bg_path, cam_idx)
                        room_bgs.append(bg)
                        self.bg_loaded.emit(room_id, cam_idx, bg)
                    except Exception as e:
                        room_bgs.append(BackgroundImage(
                            path=bg_path, camera_index=cam_idx,
                            width=0, height=0, rgba_data=b'', error=str(e)
                        ))
                    done += 1
                if room_bgs:
                    self._assets.backgrounds[room_id] = room_bgs

        self.progress.emit("Done", total_steps, total_steps)
        self.finished.emit(self._assets)


def load_stage_assets(folder_path: str,
                      on_progress: Optional[Callable] = None,
                      on_rdt: Optional[Callable] = None,
                      on_bg: Optional[Callable] = None,
                      on_done: Optional[Callable] = None,
                      load_backgrounds: bool = True) -> Tuple[QThread, StageAssetLoader]: #vers 1
    """Convenience wrapper: create loader + thread, connect callbacks, start.
    Returns (thread, loader) so caller can hold references.
    """
    loader = StageAssetLoader(folder_path, load_backgrounds=load_backgrounds)
    thread = QThread()
    loader.moveToThread(thread)

    thread.started.connect(loader.run)
    loader.finished.connect(thread.quit)

    if on_progress:
        loader.progress.connect(on_progress)
    if on_rdt:
        loader.rdt_loaded.connect(on_rdt)
    if on_bg:
        loader.bg_loaded.connect(on_bg)
    if on_done:
        loader.finished.connect(on_done)

    thread.start()
    return thread, loader
