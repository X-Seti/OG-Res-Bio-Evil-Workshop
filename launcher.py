#!/usr/bin/env python3
"""
X-Seti - December14 2025 - ResBio_Evil_Workshop - Root Launcher
#this belongs in root /launcher.py - Version: 5
"""
import sys
from pathlib import Path

# Get the root directory (where this launcher is located)
root_dir = Path(__file__).parent.resolve()

# Add root to path so we can import from apps/
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

# Add component directory to path
component_dir = root_dir / "apps" / "components" / "ResBio_Evil_Workshop"
if str(component_dir) not in sys.path:
    sys.path.insert(0, str(component_dir))

# Add depends path for component imports
depends_dir = component_dir / "depends"
if str(depends_dir) not in sys.path:
    sys.path.insert(0, str(depends_dir))

# Import and run ResBioEvilWorkshop
if __name__ == "__main__":
    try:
        print("Workshop Starting...")
        
        # Import the main module
        from apps.components.ResBio_Evil_Workshop.ResBio_Evil_Workshop import ResBioEvilWorkshop
        
        # No main() function - run workshop directly
        from PyQt6.QtWidgets import QApplication

        app = QApplication(sys.argv)
        workshop = ResBioEvilWorkshop()
        workshop.setWindowTitle("ResBio-Evil-Workshop - Standalone")
        workshop.resize(1200, 800)
        workshop.show()
        sys.exit(app.exec())
            
    except ImportError as e:
        print(f"ERROR: Failed to import ResBio_Evil_Workshop: {e}")
        print(f"Root directory: {root_dir}")
        print(f"Component directory: {component_dir}")
        print(f"Expected path: {component_dir}/ResBio_Evil_Workshop.py")
        print(f"Depends path: {depends_dir}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to start ResBioEvilWorkshop: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
