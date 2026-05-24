#!/usr/bin/env python3
#this belongs in root /launcher.py - Version: 2
# X-Seti - May22 2026 - ResBio Evil Workshop - Root Launcher

import sys
import os
from pathlib import Path

root_dir = Path(__file__).parent.resolve()
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))


def _make_app_icon():
    """Render app_icon.svg to QIcon for QApplication and window."""
    try:
        from PyQt6.QtGui import QIcon, QPixmap, QPainter
        from PyQt6.QtSvg import QSvgRenderer
        from PyQt6.QtCore import Qt

        icon_path = root_dir / 'apps' / 'icons' / 'app_icon.svg'
        if not icon_path.exists():
            return QIcon()

        renderer = QSvgRenderer(str(icon_path))
        icon = QIcon()
        # Add multiple sizes so the taskbar/dock picks the best one
        for size in (16, 24, 32, 48, 64, 128, 256):
            pixmap = QPixmap(size, size)
            pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pixmap)
            renderer.render(painter)
            painter.end()
            icon.addPixmap(pixmap)
        return icon
    except Exception as e:
        print(f"Icon error: {e}")
        from PyQt6.QtGui import QIcon
        return QIcon()


def _check_dependencies():
    """Check required packages and warn about missing ones."""
    missing = []
    for pkg, install in [
        ('pycdlib',  'pycdlib'),
        ('py7zr',    'py7zr'),
        ('rarfile',  'rarfile'),
    ]:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(install)

    if missing:
        print(f"WARNING: Missing optional packages: {', '.join(missing)}")
        print(f"Install with: pip install {' '.join(missing)} --break-system-packages")


if __name__ == "__main__":
    try:
        print("ResBio Evil Workshop Starting...")
        _check_dependencies()
        from PyQt6.QtWidgets import QApplication
        from apps.components.ResBio_Evil_Workshop.ResBio_Evil_Workshop import ResBioEvilWorkshop

        app = QApplication(sys.argv)

        # Set app name for taskbar/WM_CLASS (must be before show())
        app.setApplicationName("ResBio-Evil-Workshop")
        app.setApplicationDisplayName("ResBio-Evil Workshop")
        app.setOrganizationName("X-Seti")

        # Set icon on QApplication - this is what Linux taskbar uses
        icon = _make_app_icon()
        app.setWindowIcon(icon)

        workshop = ResBioEvilWorkshop()
        workshop.setWindowIcon(icon)  # also set on window explicitly
        workshop.show()

        sys.exit(app.exec())

    except ImportError as e:
        print(f"ERROR: Failed to import ResBio_Evil_Workshop: {e}")
        import traceback; traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to start ResBioEvilWorkshop: {e}")
        import traceback; traceback.print_exc()
        sys.exit(1)
