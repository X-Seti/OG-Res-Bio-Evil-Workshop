#!/usr/bin/env python3
#this belongs in apps/core/re_launchers.py - Version: 1
# X-Seti - May22 2026 - ResBio-Evil-Workshop - RE Game Launchers
"""
RE Game Launcher - Detect installed emulators and launch RE games
across all supported platforms:
  PS1     - DuckStation, RetroArch (Beetle PSX), PCSXR, PCSX-Redux
  Saturn  - Mednafen, Yabause, Kronos, RetroArch (Mednafen Saturn)
  GameCube - Dolphin
  PC Win98 - Wine (with optional dgVoodoo2 ddraw wrapper)
  PC Modern - Native (GOG/patched versions)

Disc ID detection from .ccd/.img/.cue filenames and system area.
"""

import os
import subprocess
import shutil
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Tuple
from enum import Enum

##Methods list -
# detect_emulators
# detect_wine
# identify_disc
# identify_folder
# launch_disc
# launch_pc_folder
# open_in_filemanager
# get_launch_options

##class Platform:
##class GameVersion:
##class EmulatorInfo:
##class LaunchConfig:


class Platform(Enum): #vers 1
    PS1       = "PlayStation 1"
    SATURN    = "Sega Saturn"
    GAMECUBE  = "Nintendo GameCube"
    PC_WIN98  = "PC (Win98 era)"
    PC_MODERN = "PC (Modern/GOG)"
    UNKNOWN   = "Unknown"


class GameVersion(Enum): #vers 1
    RE1_JP    = "Biohazard (Japan)"
    RE1_US    = "Resident Evil (USA)"
    RE1_EU    = "Resident Evil (Europe)"
    RE2_JP    = "Biohazard 2 (Japan)"
    RE2_US    = "Resident Evil 2 (USA)"
    RE2_EU    = "Resident Evil 2 (Europe)"
    RE3_JP    = "Biohazard 3 Last Escape (Japan)"
    RE3_US    = "Resident Evil 3 Nemesis (USA)"
    RE3_EU    = "Resident Evil 3 Nemesis (Europe)"
    RE15_JP   = "Biohazard 1.5 (Prototype)"
    UNKNOWN   = "Unknown"


# Disc ID -> (GameVersion, Platform)
DISC_ID_MAP: Dict[str, Tuple[GameVersion, Platform]] = {
    # RE1 PS1
    "SLPS_00222": (GameVersion.RE1_JP, Platform.PS1),
    "SLPS_00223": (GameVersion.RE1_JP, Platform.PS1),
    "SLUS_00184": (GameVersion.RE1_US, Platform.PS1),
    "SLES_00969": (GameVersion.RE1_EU, Platform.PS1),
    # RE1 Saturn
    "GS-9184":    (GameVersion.RE1_JP, Platform.SATURN),
    "MK81068":    (GameVersion.RE1_US, Platform.SATURN),
    # RE1 GameCube
    "GEZE08":     (GameVersion.RE1_US, Platform.GAMECUBE),
    "GEZP08":     (GameVersion.RE1_EU, Platform.GAMECUBE),
    "GEZJ08":     (GameVersion.RE1_JP, Platform.GAMECUBE),
    # RE2 PS1
    "SLPS_01222": (GameVersion.RE2_JP, Platform.PS1),
    "SLPS_01223": (GameVersion.RE2_JP, Platform.PS1),
    "SLUS_00421": (GameVersion.RE2_US, Platform.PS1),
    "SLUS_00592": (GameVersion.RE2_US, Platform.PS1),
    "SLES_00972": (GameVersion.RE2_EU, Platform.PS1),
    "SLES_10972": (GameVersion.RE2_EU, Platform.PS1),
    # RE2 GameCube
    "GHAE08":     (GameVersion.RE2_US, Platform.GAMECUBE),
    "GHAP08":     (GameVersion.RE2_EU, Platform.GAMECUBE),
    "GHAJ08":     (GameVersion.RE2_JP, Platform.GAMECUBE),
    # RE3 PS1
    "SLPS_02119": (GameVersion.RE3_JP, Platform.PS1),
    "SLUS_00923": (GameVersion.RE3_US, Platform.PS1),
    "SLES_02642": (GameVersion.RE3_EU, Platform.PS1),
    # RE3 GameCube
    "GHZE08":     (GameVersion.RE3_US, Platform.GAMECUBE),
    "GVPE08":     (GameVersion.RE3_EU, Platform.GAMECUBE),
}

# PC executable names -> (GameVersion, Platform)
PC_EXE_MAP: Dict[str, Tuple[GameVersion, Platform]] = {
    "bio.exe":          (GameVersion.RE1_JP, Platform.PC_WIN98),
    "re.exe":           (GameVersion.RE1_US, Platform.PC_WIN98),
    "resi.exe":         (GameVersion.RE1_US, Platform.PC_WIN98),
    "bio2.exe":         (GameVersion.RE2_JP, Platform.PC_WIN98),
    "re2.exe":          (GameVersion.RE2_US, Platform.PC_WIN98),
    "biohazard2.exe":   (GameVersion.RE2_JP, Platform.PC_WIN98),
    "bio3.exe":         (GameVersion.RE3_JP, Platform.PC_WIN98),
    "re3.exe":          (GameVersion.RE3_US, Platform.PC_WIN98),
    "biohazard3.exe":   (GameVersion.RE3_JP, Platform.PC_WIN98),
    "slusman.exe":      (GameVersion.RE3_US, Platform.PC_WIN98),
}

# GameCube disc image extensions
GC_EXTENSIONS = {'.GCZ', '.ISO', '.RVZ', '.WIA', '.GVM', '.GVZ'}


@dataclass
class EmulatorInfo: #vers 1
    name: str
    path: str
    platform: Platform
    launch_args: List[str] = field(default_factory=list)
    notes: str = ""

    @property
    def available(self) -> bool:
        return bool(self.path)


@dataclass
class LaunchConfig: #vers 1
    """Configuration for launching a game."""
    disc_path: str = ""
    exe_path: str = ""
    platform: Platform = Platform.UNKNOWN
    game_version: GameVersion = GameVersion.UNKNOWN
    emulator: Optional[EmulatorInfo] = None
    wine_path: str = ""
    extra_args: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    @property
    def can_launch(self) -> bool:
        if self.platform == Platform.PC_MODERN:
            return bool(self.exe_path)
        if self.platform == Platform.PC_WIN98:
            return bool(self.exe_path and self.wine_path)
        return bool(self.emulator and self.emulator.available and
                    (self.disc_path or self.exe_path))


def detect_emulators() -> Dict[Platform, List[EmulatorInfo]]: #vers 1
    """Scan system for installed emulators. Returns dict by platform."""
    result: Dict[Platform, List[EmulatorInfo]] = {
        Platform.PS1:      [],
        Platform.SATURN:   [],
        Platform.GAMECUBE: [],
        Platform.PC_WIN98: [],
    }

    # PS1 emulators
    for name, binary, args, notes in [
        ("DuckStation",    "duckstation-qt",   [],          "Best PS1 accuracy"),
        ("DuckStation",    "duckstation",       [],          "Best PS1 accuracy"),
        ("PCSX-Redux",     "pcsx-redux",        [],          ""),
        ("PCSXR",          "pcsxr",             [],          ""),
        ("RetroArch",      "retroarch",
         ["-L", _find_retroarch_core("beetle_psx_hw")],     "Beetle PSX HW core"),
    ]:
        path = shutil.which(binary)
        if not path:
            path = _find_flatpak(binary)
        if path:
            result[Platform.PS1].append(
                EmulatorInfo(name, path, Platform.PS1, args, notes))

    # Saturn emulators
    for name, binary, args, notes in [
        ("Mednafen",    "mednafen",   ["-psx.disable 1"],  "Best Saturn accuracy"),
        ("Yabause",     "yabause",    [],                   ""),
        ("Kronos",      "kronos",     [],                   ""),
        ("RetroArch",   "retroarch",
         ["-L", _find_retroarch_core("mednafen_saturn")],   "Mednafen Saturn core"),
    ]:
        path = shutil.which(binary)
        if not path:
            path = _find_flatpak(binary)
        if path:
            result[Platform.SATURN].append(
                EmulatorInfo(name, path, Platform.SATURN, args, notes))

    # GameCube emulators
    for name, binary, args, notes in [
        ("Dolphin",  "dolphin-emu",  [],  "Best GameCube support"),
        ("Dolphin",  "dolphin",      [],  ""),
        ("RetroArch","retroarch",
         ["-L", _find_retroarch_core("dolphin")], "Dolphin core"),
    ]:
        path = shutil.which(binary)
        if not path:
            path = _find_flatpak(binary)
        if path:
            result[Platform.GAMECUBE].append(
                EmulatorInfo(name, path, Platform.GAMECUBE, args, notes))

    # Wine for PC Win98
    wine = detect_wine()
    if wine:
        result[Platform.PC_WIN98].append(
            EmulatorInfo("Wine", wine, Platform.PC_WIN98, [],
                         "May need dgVoodoo2 for DirectX"))

    return result


def _find_retroarch_core(core_name: str) -> str: #vers 1
    """Find a RetroArch core .so file."""
    search_dirs = [
        os.path.expanduser("~/.config/retroarch/cores"),
        os.path.expanduser("~/.local/share/retroarch/cores"),
        "/usr/lib/libretro",
        "/usr/local/lib/libretro",
    ]
    for d in search_dirs:
        if not os.path.isdir(d):
            continue
        for f in os.listdir(d):
            if core_name in f.lower() and f.endswith(".so"):
                return os.path.join(d, f)
    return ""


def _find_flatpak(binary: str) -> str: #vers 1
    """Check if binary is available as a Flatpak."""
    flatpak_ids = {
        "duckstation-qt": "org.duckstation.DuckStation",
        "dolphin-emu":    "org.DolphinEmu.dolphin-emu",
        "retroarch":      "org.libretro.RetroArch",
        "mednafen":       "com.gitlab.b_lindeijer.Mednafen",
    }
    fid = flatpak_ids.get(binary)
    if not fid:
        return ""
    result = subprocess.run(
        ["flatpak", "info", fid],
        capture_output=True, text=True)
    if result.returncode == 0:
        return f"flatpak run {fid}"
    return ""


def detect_wine() -> str: #vers 1
    """Return path to Wine executable, or empty string."""
    for binary in ["wine", "wine64", "wine-stable"]:
        path = shutil.which(binary)
        if path:
            return path
    # Check Proton via Steam
    steam_compat = os.path.expanduser("~/.steam/root/steamapps/common")
    if os.path.isdir(steam_compat):
        for entry in sorted(os.listdir(steam_compat), reverse=True):
            if "proton" in entry.lower():
                proton = os.path.join(steam_compat, entry, "proton")
                if os.path.exists(proton):
                    return proton
    return ""


def identify_disc(disc_path: str) -> Tuple[GameVersion, Platform]: #vers 1
    """Identify game version and platform from disc image path/filename."""
    name = os.path.basename(disc_path).upper()
    stem = os.path.splitext(name)[0]
    ext  = os.path.splitext(name)[1]

    # Check by stem (SLUS_00923, SLES_00969, etc.)
    stem_clean = stem.replace('-', '_').replace('.', '_')
    for disc_id, (ver, plat) in DISC_ID_MAP.items():
        if disc_id.replace('-', '_').replace('.', '_') in stem_clean:
            return ver, plat

    # GameCube by extension
    if ext in GC_EXTENSIONS:
        return GameVersion.UNKNOWN, Platform.GAMECUBE

    # Saturn: Mednafen uses .cue/.bin, SSF uses .cue
    # PS1: same formats but smaller file sizes typically
    return GameVersion.UNKNOWN, Platform.PS1


def identify_folder(folder_path: str) -> Tuple[GameVersion, Platform]: #vers 1
    """Identify game version from an extracted folder."""
    for root, dirs, files in os.walk(folder_path):
        for fname in files:
            lower = fname.lower()
            for exe, (ver, plat) in PC_EXE_MAP.items():
                if lower == exe:
                    return ver, plat
        # Check for SYSTEM.CNF (PS1 disc ID)
        if "SYSTEM.CNF" in files or "system.cnf" in files:
            cnf_path = os.path.join(root, "SYSTEM.CNF")
            if not os.path.exists(cnf_path):
                cnf_path = os.path.join(root, "system.cnf")
            try:
                cnf = open(cnf_path, 'r', errors='replace').read()
                for disc_id, (ver, plat) in DISC_ID_MAP.items():
                    if disc_id in cnf:
                        return ver, plat
            except OSError:
                pass
        break  # only check top level + one subdir

    return GameVersion.UNKNOWN, Platform.UNKNOWN


def find_pc_executable(folder_path: str) -> Optional[str]: #vers 1
    """Find the RE executable in a folder tree."""
    for root, dirs, files in os.walk(folder_path):
        for fname in files:
            if fname.lower() in PC_EXE_MAP:
                return os.path.join(root, fname)
    return None


def get_launch_options(disc_path: str = '',
                       folder_path: str = '') -> LaunchConfig: #vers 1
    """Build a LaunchConfig for the best available launch method."""
    config = LaunchConfig()
    emulators = detect_emulators()

    if disc_path:
        config.disc_path = disc_path
        ver, plat = identify_disc(disc_path)
        config.game_version = ver
        config.platform = plat

    if folder_path:
        exe = find_pc_executable(folder_path)
        if exe:
            config.exe_path = exe
            ver, plat = identify_folder(folder_path)
            config.game_version = ver
            config.platform = plat

    # Find best emulator
    avail = emulators.get(config.platform, [])
    if avail:
        config.emulator = avail[0]

    if config.platform == Platform.PC_WIN98:
        config.wine_path = detect_wine()
        if not config.wine_path:
            config.notes.append(
                "Wine not found. Install wine or wine64 to run Win98 PC versions.")
        else:
            config.notes.append(
                "RE1/RE2/RE3 PC may need dgVoodoo2 ddraw.dll for DirectX compatibility.")

    if config.platform == Platform.SATURN and not avail:
        config.notes.append(
            "No Saturn emulator found. Install Mednafen for best compatibility.")

    return config


def launch_disc(disc_path: str,
                emulator: Optional[EmulatorInfo] = None) -> Tuple[bool, str]: #vers 1
    """Launch a disc image in the specified (or auto-detected) emulator.
    Returns (success, message).
    """
    if not os.path.exists(disc_path):
        return False, f"Disc image not found: {disc_path}"

    if emulator is None:
        ver, plat = identify_disc(disc_path)
        avail = detect_emulators().get(plat, [])
        if not avail:
            return False, f"No emulator found for {plat.value}"
        emulator = avail[0]

    # Handle flatpak run prefix
    if emulator.path.startswith("flatpak run"):
        cmd = emulator.path.split() + emulator.launch_args + [disc_path]
    else:
        cmd = [emulator.path] + emulator.launch_args + [disc_path]

    try:
        subprocess.Popen(cmd)
        return True, f"Launched {emulator.name}: {os.path.basename(disc_path)}"
    except Exception as e:
        return False, f"Launch error: {e}"


def launch_pc_folder(folder_path: str,
                     wine_path: str = '') -> Tuple[bool, str]: #vers 1
    """Launch RE PC version from a folder. Uses Wine for Win98 era versions."""
    exe = find_pc_executable(folder_path)
    if not exe:
        return False, "No RE executable found in folder"

    ver, plat = identify_folder(folder_path)
    work_dir = os.path.dirname(exe)

    if plat == Platform.PC_MODERN:
        # Run natively
        try:
            subprocess.Popen([exe], cwd=work_dir)
            return True, f"Launched: {os.path.basename(exe)}"
        except Exception as e:
            return False, f"Launch error: {e}"

    # Win98 era - needs Wine
    if not wine_path:
        wine_path = detect_wine()
    if not wine_path:
        return False, ("Wine not found. Install wine to run Win98 PC versions.\n"
                       "sudo apt install wine")

    try:
        cmd = [wine_path, exe]
        subprocess.Popen(cmd, cwd=work_dir,
                         env={**os.environ, 'WINEPREFIX':
                              os.path.expanduser('~/.wine_resbio')})
        return True, (f"Launched via Wine: {os.path.basename(exe)}\n"
                      f"Note: May need dgVoodoo2 ddraw.dll for proper display.")
    except Exception as e:
        return False, f"Wine launch error: {e}"


def open_in_filemanager(path: str) -> Tuple[bool, str]: #vers 1
    """Open a folder or file in the system file manager."""
    target = path if os.path.isdir(path) else os.path.dirname(path)
    for cmd in [["xdg-open", target], ["nautilus", target],
                ["dolphin", target], ["nemo", target]]:
        if shutil.which(cmd[0]):
            try:
                subprocess.Popen(cmd)
                return True, f"Opened: {target}"
            except Exception:
                pass
    return False, "No file manager found"
