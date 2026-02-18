#!/usr/bin/env python3
"""
X-Seti - December14 2025 - Run_Workshop - Root Launcher
#this belongs in root /launcher.py - Version: 2
"""
import sys
from pathlib import Path

# Get the root directory (where this launcher is located)
root_dir = Path(__file__).parent.resolve()

# Add root to path so we can import from apps/
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

# Now import and run col_workshop from apps/components/Col_Editor/
if __name__ == "__main__":
    try:
        print("Workshop Starting...")
        
        # Import the main module
        from apps.components.Tmp_Template.gui_template import gui_workshop
        
        # No main() function - run workshop directly
        from PyQt6.QtWidgets import QApplication

        app = QApplication(sys.argv)
        workshop = Tmp_Template.GUIWorkshop()
        workshop.setWindowTitle("Run Workshop 1.5 - Standalone")
        workshop.resize(1200, 800)
        workshop.show()
        sys.exit(app.exec())
            
    except ImportError as e:
        print(f"ERROR: Failed to import col_workshop: {e}")
        print(f"Root directory: {root_dir}")
        print(f"Expected path: {root_dir}/apps/components/Tmp_Template/gui_template.py")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to start GUI_Workshop: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
