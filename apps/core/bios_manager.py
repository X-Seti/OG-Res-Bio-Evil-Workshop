#!/usr/bin/env python3
#this belongs in apps/core/bios_manager.py - Version: 1
# X-Seti - November20 2025 - Multi-Emulator Launcher - BIOS Manager

"""
BIOS Manager
Scans, identifies, and verifies BIOS files for emulator platforms
Handles complex filenames and maps to emulator requirements
"""

import os
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple

##Methods list -
# __init__
# get_bios_for_platform
# get_bios_info
# scan_bios_directory
# verify_platform_bios
# _calculate_md5
# _identify_platform_from_filename
# _map_bios_to_emulator_name
# _normalize_filename

##class BiosManager -

class BiosManager: #vers 1
    """Manages BIOS file scanning and verification"""
    
    # BIOS filename patterns for platform identification
    PLATFORM_PATTERNS = {
        "Amiga": [
            "kick", "kickstart", "amiga",
            "a500", "a600", "a1200", "a2000", "a3000", "a4000"
        ],
        "PlayStation 1": [
            "scph", "psxonpsp", "ps-", "playstation"
        ],
        "PlayStation 2": [
            "scph", "ps2", "playstation 2"
        ],
        "PlayStation 3": [
            "ps3", "playstation 3", "ps3updat"
        ],
        "Sega Saturn": [
            "saturn", "sega_101", "mpr-"
        ],
        "Sega Dreamcast": [
            "dc_", "dreamcast", "dc_boot", "dc_flash"
        ],
        "Nintendo 64": [
            "pifdata", "n64"
        ],
        "Nintendo DS": [
            "firmware", "bios7", "bios9", "nds"
        ],
        "Game Boy Advance": [
            "gba", "agb", "bios"
        ],
        "Atari ST": [
            "tos", "atari st", "st.img"
        ],
        "Atari 800": [
            "atari", "atarixl", "ataribas", "atariosb"
        ],
        "Commodore 64": [
            "c64", "commodore 64", "kernal", "basic", "chargen"
        ],
        "MSX": [
            "msx"
        ],
        "Neo Geo": [
            "neogeo", "neo-geo", "ng-"
        ],
        "Arcade": [
            "neogeo", "cps", "namco"
        ]
    }
    
    # Known BIOS files and their MD5 hashes (for verification)
    KNOWN_BIOS = {
        "Amiga": {
            "kick34005.A500": {
                "description": "Kickstart 3.1 rev 40.63 (A500/A600/A2000)",
                "md5": "82a21c1890cae844b3df741f2762d48d",
                "required": False
            },
            "kick40068.A1200": {
                "description": "Kickstart 3.1 rev 40.68 (A1200)",
                "md5": "646773759326fbac3b2311fd8c8793ee",
                "required": False
            },
            "kick40070.A3000": {
                "description": "Kickstart 3.1 rev 40.70 (A3000)",
                "md5": "9bdedde6a4f33555b4a270c8ca53297d",
                "required": False
            }
        },
        "PlayStation 1": {
            "scph1001.bin": {
                "description": "SCPH-1001 (NTSC-U)",
                "md5": "924e392ed05558ffdb115408c263dccf",
                "required": True
            },
            "scph5501.bin": {
                "description": "SCPH-5501 (NTSC-U)",
                "md5": "490f666e1afb15b7362b406ed1cea246",
                "required": False
            },
            "scph7001.bin": {
                "description": "SCPH-7001 (NTSC-U)",
                "md5": "1e68c231d0896b7eadcad1d7d8e76129",
                "required": False
            }
        },
        "PlayStation 2": {
            "SCPH10000.bin": {
                "description": "PS2 BIOS (Japan)",
                "md5": None,
                "required": False
            },
            "SCPH39001.bin": {
                "description": "PS2 BIOS (USA)",
                "md5": None,
                "required": True
            }
        }
    }
    
    def __init__(self, base_dir: Path): #vers 1
        """Initialize BIOS manager
        
        Args:
            base_dir: Base directory containing bios-roms folder
        """
        self.base_dir = Path(base_dir)
        self.bios_dir = self.base_dir / "bios-roms"
        
        # Cache for scanned BIOS files
        self.scanned_bios = {}  # {platform: [bios_files]}
        self.bios_info = {}     # {file_path: bios_info}
        
    def scan_bios_directory(self) -> Dict[str, List[Path]]: #vers 1
        """Scan BIOS directory and organize by platform
        
        Returns:
            Dict mapping platform names to list of BIOS file paths
        """
        if not self.bios_dir.exists():
            print(f"BIOS directory not found: {self.bios_dir}")
            return {}
            
        print(f"Scanning BIOS directory: {self.bios_dir}")
        
        bios_files = {}
        
        # Scan all files
        for file_path in self.bios_dir.rglob("*"):
            if not file_path.is_file():
                continue
                
            # Skip non-BIOS extensions
            ext = file_path.suffix.lower()
            if ext not in ['.rom', '.bin', '.img', '.zip']:
                continue
                
            # Identify platform from filename
            platform = self._identify_platform_from_filename(file_path.name)
            
            if platform:
                if platform not in bios_files:
                    bios_files[platform] = []
                    
                bios_files[platform].append(file_path)
                
                # Store info
                self.bios_info[str(file_path)] = {
                    "platform": platform,
                    "original_name": file_path.name,
                    "size": file_path.stat().st_size,
                    "extension": ext
                }
            else:
                print(f"  Unknown BIOS file: {file_path.name}")
                
        self.scanned_bios = bios_files
        
        # Print summary
        print(f"\nBIOS Files Found:")
        print("=" * 60)
        for platform, files in sorted(bios_files.items()):
            print(f"{platform}: {len(files)} file(s)")
            for f in files[:3]:  # Show first 3
                print(f"  - {f.name}")
            if len(files) > 3:
                print(f"  ... and {len(files) - 3} more")
        print("=" * 60)
        
        return bios_files
        
    def verify_platform_bios(self, platform: str, required_files: List[str] = None) -> Tuple[bool, str]: #vers 1
        """Verify that required BIOS files exist for a platform
        
        Args:
            platform: Platform name (e.g. "PlayStation 1")
            required_files: Optional list of required BIOS filenames
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        if platform not in self.scanned_bios:
            # Try scanning if not already done
            if not self.scanned_bios:
                self.scan_bios_directory()
                
        if platform not in self.scanned_bios:
            return False, f"No BIOS files found for {platform}"
            
        platform_bios = self.scanned_bios[platform]
        
        if not platform_bios:
            return False, f"No BIOS files for {platform}"
            
        # If no specific files required, just check we have something
        if not required_files:
            return True, f"Found {len(platform_bios)} BIOS file(s) for {platform}"
            
        # Check for required files
        found_files = [f.name.lower() for f in platform_bios]
        missing = []
        
        for required in required_files:
            # Try exact match
            if required.lower() not in found_files:
                # Try partial match (for complex filenames)
                partial_match = False
                for found in found_files:
                    if required.lower() in found:
                        partial_match = True
                        break
                        
                if not partial_match:
                    missing.append(required)
                    
        if missing:
            return False, f"Missing BIOS files: {', '.join(missing)}"
            
        return True, f"All required BIOS files present for {platform}"
        
    def get_bios_for_platform(self, platform: str) -> List[Path]: #vers 1
        """Get list of BIOS files for a platform
        
        Args:
            platform: Platform name
            
        Returns:
            List of BIOS file paths
        """
        if platform not in self.scanned_bios:
            self.scan_bios_directory()
            
        return self.scanned_bios.get(platform, [])
        
    def get_bios_info(self, file_path: Path) -> Optional[Dict]: #vers 1
        """Get information about a BIOS file
        
        Args:
            file_path: Path to BIOS file
            
        Returns:
            Dict with BIOS information or None
        """
        return self.bios_info.get(str(file_path))
        
    def _identify_platform_from_filename(self, filename: str) -> Optional[str]: #vers 1
        """Identify platform from BIOS filename
        
        Args:
            filename: BIOS filename
            
        Returns:
            Platform name or None
        """
        filename_lower = filename.lower()
        
        # Check each platform's patterns
        for platform, patterns in self.PLATFORM_PATTERNS.items():
            for pattern in patterns:
                if pattern.lower() in filename_lower:
                    return platform
                    
        return None
        
    def _normalize_filename(self, filename: str) -> str: #vers 1
        """Normalize complex BIOS filename to simple emulator name
        
        Examples:
            "Kickstart v3.1 rev 40.70 (1994)(Commodore)(A3000)plus.rom" 
            -> "kick40070.A3000"
            
        Args:
            filename: Original filename
            
        Returns:
            Normalized filename
        """
        # Extract version numbers
        import re
        
        filename_lower = filename.lower()
        
        # Amiga Kickstart patterns
        if "kick" in filename_lower:
            # Extract revision number (e.g. 40.70)
            rev_match = re.search(r'(\d+\.\d+)', filename)
            if rev_match:
                rev = rev_match.group(1).replace('.', '')
                
                # Extract model (A500, A1200, etc.)
                model_match = re.search(r'\(?(A\d+)\)?', filename, re.IGNORECASE)
                if model_match:
                    model = model_match.group(1).upper()
                    return f"kick{rev}.{model}"
                else:
                    return f"kick{rev}"
                    
        # PlayStation patterns
        if "scph" in filename_lower:
            # Extract model number
            scph_match = re.search(r'scph[-]?(\d+)', filename_lower)
            if scph_match:
                model = scph_match.group(1)
                return f"scph{model}.bin"
                
        # Default: return original name without path
        return Path(filename).stem
        
    def _map_bios_to_emulator_name(self, platform: str, bios_path: Path) -> str: #vers 1
        """Map BIOS file to expected emulator filename
        
        Args:
            platform: Platform name
            bios_path: Path to BIOS file
            
        Returns:
            Expected emulator filename
        """
        normalized = self._normalize_filename(bios_path.name)
        
        # Add appropriate extension
        if platform == "Amiga":
            return f"{normalized}.rom"
        elif "PlayStation" in platform:
            return f"{normalized}.bin"
        elif platform == "Atari ST":
            return f"{normalized}.img"
        else:
            return normalized
            
    def _calculate_md5(self, file_path: Path) -> str: #vers 1
        """Calculate MD5 hash of file
        
        Args:
            file_path: Path to file
            
        Returns:
            MD5 hash as hex string
        """
        md5_hash = hashlib.md5()
        
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5_hash.update(chunk)
                
        return md5_hash.hexdigest()


def create_bios_links(bios_manager: BiosManager, target_dir: Path) -> None: #vers 1
    """Create organized BIOS directory structure with symlinks
    
    This creates a clean bios/ directory organized by platform,
    with symlinks to the actual files in bios-roms/
    
    Args:
        bios_manager: BiosManager instance
        target_dir: Target directory for organized structure (e.g. bios/)
    """
    target_dir = Path(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\nCreating organized BIOS structure in: {target_dir}")
    print("=" * 60)
    
    for platform, bios_files in bios_manager.scanned_bios.items():
        platform_dir = target_dir / platform
        platform_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"\n{platform}:")
        
        for bios_path in bios_files:
            # Create normalized filename
            normalized = bios_manager._map_bios_to_emulator_name(platform, bios_path)
            link_path = platform_dir / normalized
            
            # Create symlink if it doesn't exist
            if not link_path.exists():
                try:
                    link_path.symlink_to(bios_path)
                    print(f"  Created: {normalized} -> {bios_path.name}")
                except Exception as e:
                    print(f"  Failed to create link for {normalized}: {e}")
            else:
                print(f"  Exists: {normalized}")
                
    print("\n" + "=" * 60)
    print("BIOS organization complete!")


# CLI testing
if __name__ == "__main__":
    import sys
    
    base_dir = Path.cwd()
    
    if len(sys.argv) > 1 and sys.argv[1] == "scan":
        # Scan BIOS directory
        manager = BiosManager(base_dir)
        bios_files = manager.scan_bios_directory()
        
        if not bios_files:
            print("\nNo BIOS files found.")
            print(f"Place BIOS files in: {base_dir / 'bios-roms'}")
        else:
            print(f"\nTotal: {sum(len(files) for files in bios_files.values())} BIOS files")
            
    elif len(sys.argv) > 1 and sys.argv[1] == "organize":
        # Create organized structure
        manager = BiosManager(base_dir)
        manager.scan_bios_directory()
        
        target = base_dir / "bios"
        create_bios_links(manager, target)
        
    elif len(sys.argv) > 2 and sys.argv[1] == "verify":
        # Verify platform BIOS
        platform = sys.argv[2]
        
        manager = BiosManager(base_dir)
        manager.scan_bios_directory()
        
        success, message = manager.verify_platform_bios(platform)
        
        if success:
            print(f"✓ {message}")
        else:
            print(f"✗ {message}")
            
    else:
        print("Multi-Emulator Launcher - BIOS Manager")
        print("=" * 60)
        print("\nUsage:")
        print("  python bios_manager.py scan                - Scan BIOS directory")
        print("  python bios_manager.py organize            - Create organized structure")
        print("  python bios_manager.py verify <platform>   - Verify platform BIOS")
        print("\nExamples:")
        print("  python bios_manager.py scan")
        print("  python bios_manager.py organize")
        print('  python bios_manager.py verify "PlayStation 1"')
