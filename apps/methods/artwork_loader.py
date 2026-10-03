#!/usr/bin/env python3
#this belongs in apps/methods/artwork_loader.py - Version: 1
# X-Seti - November22 2025 - Multi-Emulator Launcher - Artwork Loader

"""
Artwork Loader - Handles loading game artwork (thumbnails and title images)
Supports 64x64 thumbnails for game list and full-size title art for display panel
"""

from pathlib import Path
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtGui import QPainter

# Around line 30, add after self.generic_icon = ...
from apps.methods.retroarch_artwork import RetroArchArtwork

##Methods list -
# __init__
# get_game_icon
# get_generic_icon
# get_title_artwork

class ArtworkLoader: #vers 1
    """Loads and caches game artwork"""
    
    def __init__(self, artwork_dir=None): #vers 1
        """Initialize artwork loader
        
        Args:
            artwork_dir: Path to artwork directory (defaults to ./artwork)
        """
        if artwork_dir is None:
            artwork_dir = Path.cwd() / "artwork"
        
        self.artwork_dir = Path(artwork_dir)
        self.artwork_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache for loaded pixmaps
        self.icon_cache = {}
        self.title_cache = {}

        # Generic icon (SVG-based)
        self.generic_icon = self._create_generic_icon()
        self.retroarch = RetroArchArtwork()
        if self.retroarch.thumbnails_dir:
            from apps.utils.debug_logger import info
            info(f"RetroArch artwork enabled: {self.retroarch.thumbnails_dir}", "ARTWORK")

    def _create_generic_icon(self, size=64): #vers 1
        """Create generic game controller icon for missing artwork
        
        Args:
            size: Icon size in pixels
            
        Returns:
            QIcon with generic controller graphic
        """
        svg_data = f'''<svg width="{size}" height="{size}" viewBox="0 0 64 64">
            <rect width="64" height="64" fill="#2c3e50" rx="4"/>
            <path d="M 16 24 Q 14 24 14 26 L 14 38 Q 14 40 16 40 L 22 40 Q 24 40 24 38 L 24 26 Q 24 24 22 24 Z" 
                  fill="none" stroke="#ecf0f1" stroke-width="2"/>
            <path d="M 42 24 Q 40 24 40 26 L 40 38 Q 40 40 42 40 L 48 40 Q 50 40 50 38 L 50 26 Q 50 24 48 24 Z" 
                  fill="none" stroke="#ecf0f1" stroke-width="2"/>
            <path d="M 24 32 L 40 32" stroke="#ecf0f1" stroke-width="2"/>
            <text x="32" y="56" font-family="Arial" font-size="8" fill="#ecf0f1" text-anchor="middle">No Artwork</text>
        </svg>'''
        
        renderer = QSvgRenderer(svg_data.encode())
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        
        return QIcon(pixmap)
    
    def get_game_icon(self, game_name, platform, size=64): #vers 1
        """Get game icon (64x64 thumbnail) for game list
        
        Args:
            game_name: Name of the game
            platform: Platform name
            size: Icon size (default 64)
            
        Returns:
            QIcon - either loaded artwork or generic icon
        """
        cache_key = f"{platform}/{game_name}_{size}"
        
        # Check cache first
        if cache_key in self.icon_cache:
            return self.icon_cache[cache_key]
        
        # Try to find artwork file
        artwork_path = self._find_artwork_file(game_name, platform, "thumbnails")
        
        if artwork_path and artwork_path.exists():
            # Load the artwork
            pixmap = QPixmap(str(artwork_path))
            if not pixmap.isNull():
                # Scale to requested size maintaining aspect ratio
                scaled_pixmap = pixmap.scaled(
                    size, size,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                icon = QIcon(scaled_pixmap)
                self.icon_cache[cache_key] = icon
                return icon
        
        # Return generic icon if artwork not found
        return self.generic_icon
    
    def get_title_artwork(self, game_name, platform): #vers 1
        """Get full-size title artwork for display panel
        
        Args:
            game_name: Name of the game
            platform: Platform name
            
        Returns:
            QPixmap - title artwork or None if not found
        """
        cache_key = f"{platform}/{game_name}_title"
        
        # Check cache first
        if cache_key in self.title_cache:
            return self.title_cache[cache_key]
        
        # Try to find title artwork
        artwork_path = self._find_artwork_file(game_name, platform, "titles")
        
        if artwork_path and artwork_path.exists():
            pixmap = QPixmap(str(artwork_path))
            if not pixmap.isNull():
                self.title_cache[cache_key] = pixmap
                return pixmap
        
        return None
    
    def _find_artwork_file(self, game_name, platform, subdir): #vers 3
        """Find artwork file - checks RetroArch first, then local

        Searches for artwork in:
        - RetroArch thumbnails (if configured)
        - artwork/[platform]/[subdir]/[game_name].png
        - artwork/[game_name].png (root level)

        Args:
            game_name: Name of the game
            platform: Platform name
            subdir: Subdirectory ("thumbnails" or "titles")

        Returns:
            Path to artwork file or None
        """
        # Try RetroArch artwork first
        if self.retroarch and self.retroarch.thumbnails_dir:
            artwork_type = 'Named_Boxarts' if subdir == 'thumbnails' else 'Named_Titles'
            retroarch_artwork = self.retroarch.get_game_artwork(platform, game_name, artwork_type)
            if retroarch_artwork:
                return retroarch_artwork

        # Clean game name for filename
        clean_name = game_name.replace(" ", "_").replace(":", "").replace("/", "_")
        
        # Check platform-specific directories
        platform_dir = self.artwork_dir / platform / subdir
        
        # Try common image extensions
        for ext in ['.png', '.jpg', '.jpeg', '.bmp', '.gif']:
            artwork_file = platform_dir / f"{clean_name}{ext}"
            if artwork_file.exists():
                return artwork_file
        
        # Also check root level (backwards compatibility)
        for ext in ['.png', '.jpg', '.jpeg', '.bmp', '.gif']:
            artwork_file = self.artwork_dir / f"{clean_name}{ext}"
            if artwork_file.exists():
                return artwork_file
        
        return None
    
    def get_generic_icon(self, size=64): #vers 1
        """Get generic controller icon
        
        Args:
            size: Icon size in pixels
            
        Returns:
            QIcon with generic game controller
        """
        if size == 64:
            return self.generic_icon
        else:
            # Create new generic icon at requested size
            return self._create_generic_icon(size)
    
    def clear_cache(self): #vers 1
        """Clear artwork cache"""
        self.icon_cache.clear()
        self.title_cache.clear()
