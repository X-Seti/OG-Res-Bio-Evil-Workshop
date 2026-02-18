#this belongs in depends/img_debug_functions.py - Version: 1
# X-Seti - February18 2025 - ResBio-Evil-Workshop 1.0 - Debug Functions
"""
Debug Functions - Logging and debugging utilities for file operations.
Provides console output for debug, error, warning, and success messages.
"""

import sys
from datetime import datetime
from typing import Optional

##Methods list -
# debug
# error
# info
# success
# warning
# log
# set_verbose
# is_verbose

##class img_debugger: -

class img_debugger: #vers 1
    """Debug logger for image and file operations"""
    
    VERBOSE = False
    DEBUG_ENABLED = True
    LOG_FILE = None
    
    @staticmethod
    def debug(msg: str, module: str = "DEBUG") -> None: #vers 1
        """Print debug message"""
        if img_debugger.DEBUG_ENABLED:
            timestamp = datetime.now().strftime("%H:%M:%S")
            output = f"[{timestamp}] {module}: {msg}"
            print(output, file=sys.stdout)
            if img_debugger.LOG_FILE:
                img_debugger._write_log(output)
    
    @staticmethod
    def error(msg: str, module: str = "ERROR") -> None: #vers 1
        """Print error message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        output = f"[{timestamp}] {module}: {msg}"
        print(output, file=sys.stderr)
        if img_debugger.LOG_FILE:
            img_debugger._write_log(output)
    
    @staticmethod
    def warning(msg: str, module: str = "WARN") -> None: #vers 1
        """Print warning message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        output = f"[{timestamp}] {module}: {msg}"
        print(output, file=sys.stdout)
        if img_debugger.LOG_FILE:
            img_debugger._write_log(output)
    
    @staticmethod
    def success(msg: str, module: str = "SUCCESS") -> None: #vers 1
        """Print success message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        output = f"[{timestamp}] {module}: {msg}"
        print(output, file=sys.stdout)
        if img_debugger.LOG_FILE:
            img_debugger._write_log(output)
    
    @staticmethod
    def info(msg: str, module: str = "INFO") -> None: #vers 1
        """Print info message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        output = f"[{timestamp}] {module}: {msg}"
        print(output, file=sys.stdout)
        if img_debugger.LOG_FILE:
            img_debugger._write_log(output)
    
    @staticmethod
    def log(msg: str, level: str = "INFO") -> None: #vers 1
        """Generic log function with level"""
        if level == "DEBUG":
            img_debugger.debug(msg)
        elif level == "ERROR":
            img_debugger.error(msg)
        elif level == "WARNING":
            img_debugger.warning(msg)
        elif level == "SUCCESS":
            img_debugger.success(msg)
        else:
            img_debugger.info(msg)
    
    @staticmethod
    def set_verbose(enabled: bool) -> None: #vers 1
        """Enable/disable verbose logging"""
        img_debugger.VERBOSE = enabled
        if enabled:
            img_debugger.debug("Verbose logging enabled")
        else:
            img_debugger.debug("Verbose logging disabled")
    
    @staticmethod
    def is_verbose() -> bool: #vers 1
        """Check if verbose logging is enabled"""
        return img_debugger.VERBOSE
    
    @staticmethod
    def enable_debug(enabled: bool = True) -> None: #vers 1
        """Enable/disable debug output"""
        img_debugger.DEBUG_ENABLED = enabled
    
    @staticmethod
    def set_log_file(filepath: Optional[str] = None) -> None: #vers 1
        """Set log file path for file-based logging"""
        img_debugger.LOG_FILE = filepath
        if filepath:
            img_debugger.debug(f"Log file set to: {filepath}")
    
    @staticmethod
    def _write_log(msg: str) -> None: #vers 1
        """Write message to log file"""
        try:
            if img_debugger.LOG_FILE:
                with open(img_debugger.LOG_FILE, 'a', encoding='utf-8') as f:
                    f.write(msg + '\n')
        except Exception as e:
            print(f"Failed to write to log file: {e}", file=sys.stderr)


# ===== USAGE EXAMPLES =====
"""
from depends.img_debug_functions import img_debugger

# Basic logging
img_debugger.debug("Loading file...")
img_debugger.error("File not found!")
img_debugger.warning("Missing data, using defaults")
img_debugger.success("Operation completed successfully")
img_debugger.info("Starting file conversion")

# Verbose mode
img_debugger.set_verbose(True)
if img_debugger.is_verbose():
    img_debugger.debug("Verbose details here...")

# File logging
img_debugger.set_log_file("debug.log")
img_debugger.debug("This will also be written to debug.log")

# Generic log with level
img_debugger.log("Something happened", level="WARNING")

# Enable/disable debug output
img_debugger.enable_debug(False)  # Suppress output
img_debugger.debug("Won't print")
img_debugger.enable_debug(True)   # Re-enable
"""
