#!/usr/bin/env python3
#this belongs in apps/gui/scd_browser.py - Version: 1
# X-Seti - May22 2026 - ResBio-Evil-Workshop - SCD Script Browser
"""
SCD Script Browser - View RE1 room script data as hex + basic opcode labels.
RDT offset[6] = init script (SCD), offset[7] = exec script (SCD).
Shows raw bytes in hex, with known opcode annotations alongside.
"""

from typing import Optional, List, Dict

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFrame, QTextEdit, QComboBox, QSplitter
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QTextCharFormat, QTextCursor

from apps.core.re1_formats import RDTFile

##Methods list -
# load_rdt
# _show_script
# _disassemble_scd
# _hex_dump

##class SCDBrowser:


# RE1 SCD opcode table (subset of known opcodes)
RE1_SCD_OPCODES: Dict[int, str] = {
    0x00: "NOP",
    0x01: "EVT_END",
    0x02: "EVT_NEXT",
    0x03: "EVT_CHAIN",
    0x04: "EVT_EXEC",
    0x05: "EVT_KILL",
    0x06: "IFEL_CK",
    0x07: "ELSE_CK",
    0x08: "ENDIF",
    0x09: "SLEEP",
    0x0A: "SLEEPING",
    0x0B: "WSLEEP",
    0x0C: "WSLEEPING",
    0x0D: "FOR",
    0x0E: "FOR2",
    0x0F: "NEXT",
    0x10: "WHILE",
    0x11: "EWHILE",
    0x12: "DO",
    0x13: "EDWHILE",
    0x14: "SWITCH",
    0x15: "CASE",
    0x16: "DEFAULT",
    0x17: "ESWITCH",
    0x18: "GOTO",
    0x19: "GOSUB",
    0x1A: "RETURN",
    0x1B: "BREAK",
    0x1C: "FOR3",
    0x1D: "FOR3_2",
    0x1E: "BREAK2",
    0x1F: "NOP1F",
    0x20: "BEGIN",
    0x21: "MIZU",
    0x22: "AOT_SET",
    0x23: "OBJ_MODEL_SET",
    0x24: "WORK_SET",
    0x25: "SPEED_SET",
    0x26: "ADD_SPEED",
    0x27: "ADD_ASPEED",
    0x28: "POS_SET",
    0x29: "DIR_SET",
    0x2A: "MEMBER_SET",
    0x2B: "MEMBER_SET2",
    0x2C: "SE_ON",
    0x2D: "SCA_ID_SET",
    0x2E: "FLICKER",
    0x2F: "GAME_OVER",
    0x30: "WIRE_CUT",
    0x31: "LIFE_SET",
    0x32: "POISON_CK",
    0x33: "POISON_CLR",
    0x34: "HEAL",
    0x35: "SAVE",
    0x36: "EVT_EXEC2",
    0x37: "ITEM_AOT_SET",
    0x38: "SCE_RND",
    0x39: "CUT_CHG",
    0x3A: "CUT_OLD",
    0x3B: "MESSAGE_ON",
    0x3C: "ITEM_CK",
    0x3D: "ITEM_GET",
    0x3E: "ITEM_GET2",
    0x3F: "ITEM_LOST",
    0x40: "ITEM_CK2",
    0x41: "RECON",
    0x42: "RECON2",
    0x43: "BGM_CTL",
    0x44: "BGMF_CTL",
    0x45: "SE_CTL",
    0x46: "KEY_CK",
    0x47: "KEY_CK2",
    0x48: "TRG_CK",
    0x49: "SCE_ESPR_ON",
    0x4A: "DOOR_AOT_SET",
    0x4B: "CUT_AUTO",
    0x4C: "MEMBER_CMP",
    0x4D: "PLYR_DIR",
    0x4E: "EFECT_MV",
    0x4F: "ROOM_CHANGE",
}

# Opcode argument sizes (bytes after opcode byte)
RE1_SCD_ARG_SIZES: Dict[int, int] = {
    0x00: 0,  # NOP
    0x01: 0,  # EVT_END
    0x02: 1,  # EVT_NEXT
    0x06: 2,  # IFEL_CK
    0x07: 2,  # ELSE_CK
    0x08: 0,  # ENDIF
    0x09: 1,  # SLEEP
    0x22: 11, # AOT_SET
    0x28: 6,  # POS_SET
    0x29: 6,  # DIR_SET
    0x37: 11, # ITEM_AOT_SET
    0x39: 1,  # CUT_CHG
    0x3B: 3,  # MESSAGE_ON
    0x3C: 2,  # ITEM_CK
    0x3D: 2,  # ITEM_GET
    0x4A: 18, # DOOR_AOT_SET
    0x4F: 6,  # ROOM_CHANGE
}


class SCDBrowser(QWidget): #vers 1
    """SCD script browser widget."""

    def __init__(self, parent=None): #vers 1
        super().__init__(parent)
        self._rdt: Optional[RDTFile] = None
        self._build_ui()

    def _build_ui(self): #vers 1
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Toolbar
        tb = QFrame()
        tb.setFrameStyle(QFrame.Shape.StyledPanel)
        tb.setMaximumHeight(32)
        tl = QHBoxLayout(tb)
        tl.setContentsMargins(4, 2, 4, 2)
        tl.setSpacing(6)

        tl.addWidget(QLabel("Script:"))
        self.script_combo = QComboBox()
        self.script_combo.addItems(["Init Script (offset[6])",
                                     "Exec Script (offset[7])"])
        self.script_combo.currentIndexChanged.connect(self._on_script_changed)
        self.script_combo.setMaximumWidth(200)
        tl.addWidget(self.script_combo)
        tl.addStretch()
        self._info = QLabel("No RDT loaded")
        self._info.setFont(QFont("Courier New", 8))
        tl.addWidget(self._info)
        layout.addWidget(tb)

        # Splitter: hex | disasm
        splitter = QSplitter(Qt.Orientation.Horizontal)

        self.hex_view = QTextEdit()
        self.hex_view.setReadOnly(True)
        self.hex_view.setFont(QFont("Courier New", 9))
        self.hex_view.setStyleSheet("background: #0e1014; color: #aaaaaa;")
        self.hex_view.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        splitter.addWidget(self.hex_view)

        self.asm_view = QTextEdit()
        self.asm_view.setReadOnly(True)
        self.asm_view.setFont(QFont("Courier New", 9))
        self.asm_view.setStyleSheet("background: #0c1210; color: #88ccaa;")
        self.asm_view.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        splitter.addWidget(self.asm_view)

        splitter.setSizes([400, 300])
        layout.addWidget(splitter, stretch=1)

    def load_rdt(self, rdt: RDTFile): #vers 1
        self._rdt = rdt
        self._show_script(self.script_combo.currentIndex())

    def _on_script_changed(self, index: int): #vers 1
        if self._rdt:
            self._show_script(index)

    def _show_script(self, script_index: int): #vers 1
        """Display init or exec script."""
        if not self._rdt or not self._rdt.header:
            self.hex_view.setPlainText("No RDT loaded")
            self.asm_view.setPlainText("")
            return

        offsets = self._rdt.header.offsets
        # offset[6]=init, offset[7]=exec
        offset_idx = 6 + script_index
        if offset_idx >= len(offsets):
            self.hex_view.setPlainText("Offset not available")
            return

        script_offset = offsets[offset_idx]
        if script_offset == 0 or script_offset >= len(self._rdt.raw_data):
            self.hex_view.setPlainText(
                f"Script offset 0x{script_offset:08X} — no data")
            self.asm_view.setPlainText("")
            return

        # Extract script bytes — read until EVT_END or 2KB limit
        data  = self._rdt.raw_data
        start = script_offset
        end   = min(start + 2048, len(data))
        script_bytes = data[start:end]

        self._info.setText(
            f"Offset: 0x{start:08X}  Size: {len(script_bytes)}B")

        self.hex_view.setPlainText(self._hex_dump(script_bytes, start))
        self.asm_view.setPlainText(self._disassemble_scd(script_bytes, start))

    def _hex_dump(self, data: bytes, base_offset: int = 0) -> str: #vers 1
        """Format bytes as hex dump: offset | hex bytes | ascii."""
        lines = []
        for i in range(0, len(data), 16):
            chunk  = data[i:i+16]
            hex_   = ' '.join(f"{b:02X}" for b in chunk)
            ascii_ = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
            lines.append(f"{base_offset+i:08X}  {hex_:<47}  {ascii_}")
        return '\n'.join(lines)

    def _disassemble_scd(self, data: bytes, base_offset: int = 0) -> str: #vers 1
        """Basic SCD disassembly — opcode + argument bytes."""
        lines = []
        pos = 0
        max_ops = 512

        for _ in range(max_ops):
            if pos >= len(data):
                break

            op    = data[pos]
            name  = RE1_SCD_OPCODES.get(op, f"UNK_{op:02X}")
            args  = RE1_SCD_ARG_SIZES.get(op, 1)  # default 1 unknown arg byte
            arg_bytes = data[pos+1:pos+1+args]
            arg_str = ' '.join(f"{b:02X}" for b in arg_bytes)

            lines.append(
                f"{base_offset+pos:08X}  {op:02X}  {name:<16} {arg_str}")

            if op == 0x01:  # EVT_END
                lines.append("")
                break

            pos += 1 + args

        return '\n'.join(lines)
