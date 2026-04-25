#!/usr/bin/env python3
#this belongs in root /launcher.py - Version: 1
# X-Seti - April25 2026 - ResBio Evil Workshop - Root Launcher

import sys
from pathlib import Path

root_dir = Path(__file__).parent.resolve()
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

if __name__ == "__main__":
    try:
        print("ResBio Evil Workshop Starting...")
        from PyQt6.QtWidgets import QApplication
        from apps.components.ResBio_Evil_Workshop.ResBio_Evil_Workshop import ResBioEvilWorkshop
        app = QApplication(sys.argv)
        workshop = ResBioEvilWorkshop()
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
