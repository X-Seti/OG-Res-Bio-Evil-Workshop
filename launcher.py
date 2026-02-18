#!/usr/bin/env python3
"""
X-Seti - December14 2025 - Bio-Res-Evil-Workshop - Root Launcher
#this belongs in root /launcher.py - Version: 3
"""
import sys
from pathlib import Path

# Get the root directory (where this launcher is located)
root_dir = Path(__file__).parent.resolve()

# Add root to path so we can import from apps/
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

# Import and run GUIWorkshop from apps/components/Resbio-Evil-Workshop/
if __name__ == "__main__":
    try:
        print("Workshop Starting...")
        
        # Import the main module
        from apps.components.Resbio-Evil-Workshop.Biores-evil-workshop import GUIWorkshop
        
        # No main() function - run workshop directly
        from PyQt6.QtWidgets import QApplication

        app = QApplication(sys.argv)
        workshop = GUIWorkshop()
        workshop.setWindowTitle("Bio-Res-Evil-Workshop - Standalone")
        workshop.resize(1200, 800)
        workshop.show()
        sys.exit(app.exec())
            
    except ImportError as e:
        print(f"ERROR: Failed to import col_workshop: {e}")
        print(f"Root directory: {root_dir}")
        print(f"Expected path: {root_dir}/apps/components/Resbio-Evil-Workshop/Biores-evil-workshop.py")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to start GUI_Workshop: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
