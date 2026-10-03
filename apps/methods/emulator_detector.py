#!/usr/bin/env python3
#this belongs in apps/methods/emulator_detector.py - Version: 1
# X-Seti - December01 2025 - Multi-Emulator Launcher - Emulator Detector

"""
Emulator Detector - Finds emulators from multiple sources
- System installed (pacman/yay)
- Flatpak installed
- Local cores folder
"""

import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

##Methods list -
# detect_all_emulators
# detect_flatpak_emulators
# detect_local_cores
# detect_system_emulators

def detect_system_emulators() -> Dict[str, str]: #vers 1
    """Detect emulators installed via pacman/yay in /usr/bin"""
    emulators = {
        # PlayStation
        'pcsx2': 'PlayStation 2',
        'pcsx2-qt': 'PlayStation 2',
        'duckstation-qt': 'PlayStation 1',
        'epsxe': 'PlayStation 1',
        'ppsspp': 'PSP',
        'ppsspp-qt': 'PSP',

        # Nintendo
        'mupen64plus': 'Nintendo 64',
        'snes9x-gtk': 'Super Nintendo',
        'fceux': 'NES',
        'mgba-qt': 'Game Boy Advance',
        'desmume': 'Nintendo DS',
        'melonDS': 'Nintendo DS',
        'dolphin-emu': 'Nintendo GameCube',
        'cemu': 'Wii U',

        # Sega
        'blastem': 'Sega Genesis',

        # Computer platforms
        'fs-uae': 'Amiga',
        'amiberry': 'Amiga',
        'amiberry-lite': 'Amiga',
        'hatari': 'Atari ST',
        'stella': 'Atari 2600',
        'atari800': 'Atari 800',
        'cap32': 'Amstrad CPC',
        'caprice32': 'Amstrad CPC',
        'b2': 'BBC Micro',
        'vice': 'Commodore 64',
        'fuse': 'ZX Spectrum',
        'openmsx': 'MSX',
        'bluemsx': 'MSX',

        # Multi-system
        'mame': 'Arcade',
        'retroarch': 'Multi-System',
    }

    found = {}

    for emu_name, platform in emulators.items():
        try:
            result = subprocess.run(
                ['which', emu_name],
                capture_output=True,
                text=True,
                timeout=2
            )

            if result.returncode == 0:
                emu_path = result.stdout.strip()
                found[emu_name] = {'platform': platform, 'path': emu_path, 'source': 'system'}

        except Exception:
            pass

    return found

def detect_flatpak_emulators() -> Dict[str, str]: #vers 1
    """Detect emulators installed via Flatpak"""
    flatpak_emulators = {
        'org.DolphinEmu.dolphin-emu': ('dolphin-emu', 'Nintendo GameCube'),
        'net.rpcs3.RPCS3': ('rpcs3', 'PlayStation 3'),
        'org.ppsspp.PPSSPP': ('ppsspp', 'PSP'),
        'net.kuribo64.melonDS': ('melonds', 'Nintendo DS'),
        'io.github.m64p.m64p': ('mupen64plus', 'Nintendo 64'),
        'org.duckstation.DuckStation': ('duckstation', 'PlayStation 1'),
        'net.pcsx2.PCSX2': ('pcsx2', 'PlayStation 2'),
        'com.snes9x.Snes9x': ('snes9x', 'Super Nintendo'),
        'org.fceux.Fceux': ('fceux', 'NES'),
        'io.mgba.mGBA': ('mgba', 'Game Boy Advance'),
        'com.github.Rosalie241.RMG': ('rmg', 'Nintendo 64'),
        'io.github.shiiion.primehack': ('primehack', 'Nintendo Wii'),
        'info.cemu.Cemu': ('cemu', 'Wii U'),
        'com.github.AmatCoder.mednaffe': ('mednafen', 'Multi-System'),
    }

    found = {}

    try:
        # Check if flatpak is installed
        result = subprocess.run(
            ['which', 'flatpak'],
            capture_output=True,
            timeout=2
        )

        if result.returncode != 0:
            return found

        # List installed flatpaks
        result = subprocess.run(
            ['flatpak', 'list', '--app', '--columns=application'],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            installed_apps = result.stdout.strip().split('\n')

            for flatpak_id in flatpak_emulators:
                if flatpak_id in installed_apps:
                    emu_name, platform = flatpak_emulators[flatpak_id]
                    found[emu_name] = {
                        'platform': platform,
                        'path': f'flatpak run {flatpak_id}',
                        'source': 'flatpak',
                        'flatpak_id': flatpak_id
                    }

    except Exception as e:
        print(f"Error detecting flatpak emulators: {e}")

    return found

def detect_local_cores(cores_dir: Path) -> Dict[str, str]: #vers 1
    """Detect libretro cores in local cores/ directory"""
    if not cores_dir.exists():
        return {}

    core_platform_map = {
        'beetle_psx_hw': 'PlayStation 1',
        'beetle_psx': 'PlayStation 1',
        'pcsx_rearmed': 'PlayStation 1',
        'beetle_saturn': 'Sega Saturn',
        'flycast': 'Dreamcast',
        'mupen64plus_next': 'Nintendo 64',
        'parallel_n64': 'Nintendo 64',
        'snes9x': 'Super Nintendo',
        'bsnes': 'Super Nintendo',
        'nestopia': 'NES',
        'fceumm': 'NES',
        'mgba': 'Game Boy Advance',
        'gambatte': 'Game Boy',
        'melonds': 'Nintendo DS',
        'desmume': 'Nintendo DS',
        'genesis_plus_gx': 'Sega Genesis',
        'blastem': 'Sega Genesis',
        'ppsspp': 'PSP',
        'puae': 'Amiga',
        'hatari': 'Atari ST',
        'stella': 'Atari 2600',
        'prosystem': 'Atari 7800',
        'atari800': 'Atari 800',
        'cap32': 'Amstrad CPC',
        'fuse': 'ZX Spectrum',
        'bluemsx': 'MSX',
    }

    found = {}

    # Check for .so, .dll, .dylib files
    for ext in ['.so', '.dll', '.dylib']:
        for core_file in cores_dir.glob(f'*_libretro{ext}'):
            core_name = core_file.stem.replace('_libretro', '')

            if core_name in core_platform_map:
                found[core_name] = {
                    'platform': core_platform_map[core_name],
                    'path': str(core_file),
                    'source': 'local_core'
                }

    return found

def detect_all_emulators(cores_dir: Path = None) -> Tuple[Dict, Dict]: #vers 1
    """Detect all emulators from all sources

    Returns:
        Tuple of (emulators_dict, summary_dict)
    """
    print("\n=== Detecting Emulators ===")

    all_emulators = {}

    # Detect system emulators
    print("Scanning system emulators (pacman/yay)...")
    system_emus = detect_system_emulators()
    all_emulators.update(system_emus)
    print(f"  Found {len(system_emus)} system emulator(s)")

    # Detect flatpak emulators
    print("Scanning Flatpak emulators...")
    flatpak_emus = detect_flatpak_emulators()
    all_emulators.update(flatpak_emus)
    print(f"  Found {len(flatpak_emus)} Flatpak emulator(s)")

    # Detect local cores
    if cores_dir:
        print(f"Scanning local cores in {cores_dir}...")
        local_cores = detect_local_cores(cores_dir)
        all_emulators.update(local_cores)
        print(f"  Found {len(local_cores)} local core(s)")

    # Create summary
    summary = {
        'total': len(all_emulators),
        'system': len(system_emus),
        'flatpak': len(flatpak_emus),
        'local_cores': len(local_cores) if cores_dir else 0
    }

    print(f"\n✓ Total: {summary['total']} emulator(s)/core(s) detected")
    print("=" * 40)

    return all_emulators, summary
