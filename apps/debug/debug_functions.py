#!/usr/bin/env python3
#this belongs in apps/debug/debug_functions.py - Version: 1
# X-Seti - May22 2026 - ResBio-Evil-Workshop - Debug Functions
"""
Debug logger for ResBio-Evil-Workshop.
Matches the img_debugger interface from IMG Factory so all existing
debug calls work without changes.
Accepts optional category as second argument: debug(msg, category="")
"""

import sys
import os
from datetime import datetime
from typing import Any, Optional

##Methods list -
# debug
# info
# warning
# error
# success
# log

##class ImgDebugger:


class ImgDebugger: #vers 1
    """Debug logger with level filtering and optional category tagging."""

    def __init__(self, enabled: bool = True, prefix: str = "ResBio"): #vers 1
        self.enabled       = enabled
        self.prefix        = prefix
        self.error_count   = 0
        self.warning_count = 0
        self.trace_calls   = False
        self._log_to_file  = False
        self._log_path: Optional[str] = None

    def log(self, level: str, message: str, category: str = ""): #vers 1
        if not self.enabled:
            return
        cat = f"[{category}] " if category else ""
        ts  = datetime.now().strftime("%H:%M:%S")
        line = f"[{ts}] [{self.prefix}] [{level}] {cat}{message}"
        print(line, file=sys.stderr if level == "ERROR" else sys.stdout)
        if self._log_to_file and self._log_path:
            try:
                with open(self._log_path, 'a', encoding='utf-8') as f:
                    f.write(line + "\n")
            except OSError:
                pass

    def debug(self, message: str, *args): #vers 1
        category = args[0] if args else ""
        self.log("DEBUG", message, category)

    def info(self, message: str, *args): #vers 1
        category = args[0] if args else ""
        self.log("INFO", message, category)

    def warning(self, message: str, *args): #vers 1
        category = args[0] if args else ""
        self.warning_count += 1
        self.log("WARNING", message, category)

    def error(self, message: str, *args): #vers 1
        category = args[0] if args else ""
        self.error_count += 1
        self.log("ERROR", message, category)

    def success(self, message: str, *args): #vers 1
        category = args[0] if args else ""
        self.log("SUCCESS", message, category)

    def enable_file_log(self, path: str): #vers 1
        self._log_to_file = True
        self._log_path    = path

    def disable_file_log(self): #vers 1
        self._log_to_file = False

    def reset_counts(self): #vers 1
        self.error_count   = 0
        self.warning_count = 0


# Singleton instance - import this everywhere
img_debugger = ImgDebugger(enabled=True)
