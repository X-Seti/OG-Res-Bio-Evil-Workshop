# X-Seti - December27 2025 - Multi-Emulator Launcher - Emulator Window Arguments
#this belongs in apps/core/emulator_window_args.py - Version: 2
"""
Emulator Window Arguments Helper
Maps emulator names to window size command-line arguments
Special handling for cap32 which uses config overrides
"""

##Methods list -
# get_window_args

def get_window_args(emu, width=800, height=600, fullscreen=False, mel_settings=None): #vers 2
    """Get window arguments for specific emulator
    
    Args:
        emu: Emulator name (e.g., 'hatari', 'cap32')
        width: Desired window width (default: 800)
        height: Desired window height (default: 600)
        fullscreen: If True, return fullscreen arguments instead
        mel_settings: MELSettingsManager instance (for cap32 settings)
        
    Returns:
        List of command-line arguments for the emulator
    """
    emu = emu.lower()
    
    # Special handling for cap32/caprice32 - uses override syntax
    if emu in ['cap32', 'caprice32']:
        if mel_settings and hasattr(mel_settings, 'get_cap32_scale'):
            # Get cap32-specific settings from MEL
            scale = mel_settings.get_cap32_scale()
            style = mel_settings.get_cap32_style()
            window = mel_settings.get_cap32_window_mode()
            aspect = mel_settings.get_cap32_preserve_aspect()
            oglfilter = mel_settings.get_cap32_oglfilter()
        else:
            # Fallback defaults
            scale = 3       # 1152×810
            style = 11      # OpenGL scaling
            window = 1      # Windowed
            aspect = 1      # Preserve aspect
            oglfilter = 1   # Filter on
        
        # Override window mode if fullscreen requested
        if fullscreen:
            window = 0
        
        # Build override arguments
        args = [
            '-O', f'video.scr_scale={scale}',
            '-O', f'video.scr_style={style}',
            '-O', f'video.scr_window={window}',
            '-O', f'video.scr_preserve_aspect_ratio={aspect}',
        ]
        
        # Add OpenGL filter if using OpenGL style (11)
        if style == 11:
            args.extend(['-O', f'video.scr_oglfilter={oglfilter}'])
        
        return args
    
    # Fullscreen mode for other emulators
    if fullscreen:
        fullscreen_args = {
            # Atari
            'hatari': ['--fullscreen'],
            'stella': ['-fullscreen', '1'],
            'prosystem': [],
            
            # Acorn / BBC
            'b2': [],
            'beebem': [],
            'elkulator': [],
            
            # Others
            'atari800': ['-fullscreen'],
            'pcsx2': ['--fullscreen'],
            'pcsx2-qt': ['--fullscreen'],
            'duckstation-qt': ['-fullscreen'],
            'ppsspp': ['--fullscreen'],
            'ppsspp-qt': ['--fullscreen'],
            'dolphin-emu': ['-b'],
            'mupen64plus': ['--fullscreen'],
            'snes9x-gtk': ['--fullscreen'],
            'fceux': ['--fullscreen'],
            'mgba-qt': ['-f'],
            'melonds': ['--fullscreen'],
            'fuse': ['--full-screen'],
            'vice': ['-fullscreen'],
            'blastem': ['-f'],
            'mame': ['-window', '-nomaximize'],
            'retroarch': ['--fullscreen'],
        }
        return fullscreen_args.get(emu, ['--fullscreen'])
    
    # Window mode with size arguments
    window_args = {
        # Atari
        'hatari': ['--zoom', '2'],
        'stella': ['-windowedpos', f'{width}x{height}'],
        'atari800': ['-win-width', str(width), '-win-height', str(height)],
        'prosystem': [],
        
        # Acorn / BBC
        'b2': [],
        'beebem': [],
        'jsbeeb': [],
        'elkulator': [],
        
        # PlayStation
        'pcsx2': ['-width', str(width), '-height', str(height)],
        'pcsx2-qt': ['--'],
        'duckstation-qt': ['-width', str(width), '-height', str(height)],
        'epsxe': [],
        
        # PSP
        'ppsspp': ['--windowed'],
        'ppsspp-qt': ['--windowed'],
        'ppsspp-sdl': ['--windowed'],
        
        # Nintendo
        'mupen64plus': ['--resolution', f'{width}x{height}'],
        'snes9x-gtk': [],
        'snes9x': [],
        'fceux': ['--xscale', '2', '--yscale', '2'],
        'nestopia': [],
        'mgba-qt': [],
        'visualboyadvance': [],
        'vba': [],
        'melonds': [],
        'desmume': [],
        'dolphin-emu': ['-v', 'Null'],
        'citra': [],
        'citra-qt': [],
        
        # Sega
        'blastem': ['-w', str(width), str(height)],
        'gens': [],
        'fusion': [],
        
        # Amiga
        'fs-uae': ['--window-width', str(width), '--window-height', str(height)],
        'amiberry': [],
        'amiberry-lite': [],
        
        # Others
        'fuse': ['--graphics-filter', 'advmame2x'],
        'vice': ['-VICIIdscan'],
        'mame': ['-window', '-nomaximize', '-resolution', f'{width}x{height}'],
        'mednafen': [],
        'retroarch': ['--size', f'{width}x{height}'],
        'bluemsx': [],
        'bsnes': [],
    }
    
    return window_args.get(emu, [])


# Emulator notes for reference
EMULATOR_NOTES = {
    'cap32': 'Uses -O video.option=value syntax. Scale 1-8, style 0-11',
    'hatari': 'Uses --zoom levels, not pixel dimensions',
    'stella': 'Atari 2600 emulator, uses -windowedpos WIDTHxHEIGHT',
    'atari800': 'Atari 8-bit, supports -win-width and -win-height',
    'prosystem': 'Atari 7800, no window size arguments',
    'b2': 'BBC Micro, no window size arguments',
    'pcsx2': 'PlayStation 2, supports -width/-height',
    'duckstation-qt': 'PlayStation 1, supports -width/-height',
    'ppsspp': 'PSP emulator, use --windowed flag',
    'mupen64plus': 'N64, uses --resolution WIDTHxHEIGHT',
    'fceux': 'NES, uses scale factors not dimensions',
    'blastem': 'Genesis/MD, uses -w WIDTH HEIGHT',
    'mame': 'Multiple systems, uses -resolution WIDTHxHEIGHT',
    'retroarch': 'Frontend for libretro cores, uses --size WIDTHxHEIGHT',
}
