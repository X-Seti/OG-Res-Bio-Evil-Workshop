#!/usr/bin/env python3
#this belongs in apps/version.py - Version: 1
# X-Seti - May22 2026 - ResBio-Evil-Workshop - Version Info
"""
Central version constants. Import from here everywhere.
"""

APP_NAME    = "ResBio-Evil Workshop"
APP_VERSION = "0.6"
APP_BUILD   = "May 22 2026"
APP_AUTHOR  = "X-Seti"

def title_string(suffix: str = "") -> str: #vers 1
    """Return formatted window title string."""
    base = f"{APP_NAME} v{APP_VERSION} (build {APP_BUILD})"
    return f"{base}: {suffix}" if suffix else base
