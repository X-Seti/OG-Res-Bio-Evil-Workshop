#!/usr/bin/env python3
#this belongs in apps/gui/audio_player.py - Version: 1
# X-Seti - May22 2026 - ResBio-Evil-Workshop - Audio Player
"""
Audio Player - Compact widget for playing VAG/WAV/SND audio files.
Shows waveform, play/stop controls, position scrubber, volume.
Uses PyQt6.QtMultimedia - no external audio library needed.
"""

import os
import wave
import struct
import tempfile
from typing import Optional, List

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QSlider, QLabel, QFrame, QSizePolicy
)
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import Qt, QUrl, QTimer, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QFont

from apps.core.re_audio import get_audio_info, to_wav_file, scan_audio_files, AudioInfo

##Methods list -
# load_file
# play
# stop
# set_volume
# _on_position_changed
# _on_duration_changed
# _on_playback_state_changed
# _on_slider_moved
# _update_time_label
# paintEvent

##class WaveformWidget:
##class AudioPlayerWidget:


COL_BG      = QColor(16, 20, 26)
COL_WAVE    = QColor(0,  200, 100)
COL_WAVE_DIM= QColor(0,  100, 50)
COL_POS     = QColor(255, 200, 0)
COL_TEXT    = QColor(180, 180, 180)


class WaveformWidget(QWidget): #vers 1
    """Draws a waveform from WAV peak data. Click to seek."""

    seek_requested = pyqtSignal(float)  # 0.0-1.0 position

    def __init__(self, parent=None): #vers 1
        super().__init__(parent)
        self._peaks: List[float] = []
        self._position = 0.0   # 0.0-1.0
        self.setMinimumHeight(32)
        self.setMaximumHeight(40)
        self.setStyleSheet("background-color: #10141a;")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def set_peaks(self, peaks: List[float]): #vers 1
        self._peaks = peaks
        self.update()

    def set_position(self, pos: float): #vers 1
        self._position = max(0.0, min(1.0, pos))
        self.update()

    def paintEvent(self, event): #vers 1
        painter = QPainter(self)
        painter.fillRect(self.rect(), COL_BG)

        if not self._peaks:
            painter.setPen(QPen(QColor(40, 50, 40), 1))
            painter.setFont(QFont("Courier New", 7))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "no waveform")
            return

        w, h = self.width(), self.height()
        mid   = h // 2
        n     = len(self._peaks)
        pos_x = int(self._position * w)

        for i, peak in enumerate(self._peaks):
            x   = int(i * w / n)
            amp = int(peak * mid * 0.9)
            col = COL_WAVE if x <= pos_x else COL_WAVE_DIM
            painter.setPen(QPen(col, 1))
            painter.drawLine(x, mid - amp, x, mid + amp)

        # Playhead
        painter.setPen(QPen(COL_POS, 2))
        painter.drawLine(pos_x, 0, pos_x, h)

    def mousePressEvent(self, event): #vers 1
        pos = event.pos().x() / max(self.width(), 1)
        self.seek_requested.emit(pos)


def _build_peaks(wav_path: str, num_peaks: int = 400) -> List[float]: #vers 1
    """Build peak list from WAV file for waveform display."""
    peaks = []
    try:
        with wave.open(wav_path, 'rb') as wf:
            nframes   = wf.getnframes()
            sampwidth = wf.getsampwidth()
            nchans    = wf.getnchannels()
            if nframes == 0:
                return peaks

            chunk = max(1, nframes // num_peaks)
            fmt   = '<h' if sampwidth == 2 else '<b'
            scale = 32767.0 if sampwidth == 2 else 127.0

            for _ in range(num_peaks):
                raw = wf.readframes(chunk)
                if not raw:
                    break
                step = sampwidth * nchans
                vals = [struct.unpack_from(fmt, raw, i)[0]
                        for i in range(0, len(raw) - step + 1, step)]
                if vals:
                    pk = max(abs(v) for v in vals) / scale
                    peaks.append(min(1.0, pk))
                else:
                    peaks.append(0.0)
    except Exception:
        pass
    return peaks


class AudioPlayerWidget(QWidget): #vers 1
    """Compact audio player: waveform + controls + volume."""

    file_loaded = pyqtSignal(str)   # path of loaded file

    def __init__(self, parent=None): #vers 1
        super().__init__(parent)
        self._wav_temp: Optional[str] = None
        self._info: Optional[AudioInfo] = None
        self._player = QMediaPlayer(self)
        self._audio_output = QAudioOutput(self)
        self._player.setAudioOutput(self._audio_output)
        self._audio_output.setVolume(0.7)
        self._building_ui = True
        self._build_ui()
        self._building_ui = False
        self._connect_signals()

    def _build_ui(self): #vers 1
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)

        # Waveform
        self.waveform = WaveformWidget(self)
        layout.addWidget(self.waveform)

        # Controls row
        ctrl = QHBoxLayout()
        ctrl.setSpacing(4)

        self.play_btn = QPushButton("▶")
        self.play_btn.setMaximumWidth(32)
        self.play_btn.setMaximumHeight(22)
        self.play_btn.setToolTip("Play")
        self.play_btn.clicked.connect(self.play)
        ctrl.addWidget(self.play_btn)

        self.stop_btn = QPushButton("■")
        self.stop_btn.setMaximumWidth(32)
        self.stop_btn.setMaximumHeight(22)
        self.stop_btn.setToolTip("Stop")
        self.stop_btn.clicked.connect(self.stop)
        ctrl.addWidget(self.stop_btn)

        # Position scrubber
        self.pos_slider = QSlider(Qt.Orientation.Horizontal)
        self.pos_slider.setRange(0, 1000)
        self.pos_slider.setValue(0)
        self.pos_slider.setMaximumHeight(18)
        ctrl.addWidget(self.pos_slider, stretch=1)

        # Time label
        self.time_label = QLabel("0:00 / 0:00")
        self.time_label.setFont(QFont("Courier New", 7))
        self.time_label.setMinimumWidth(70)
        ctrl.addWidget(self.time_label)

        # Volume
        self.vol_slider = QSlider(Qt.Orientation.Horizontal)
        self.vol_slider.setRange(0, 100)
        self.vol_slider.setValue(70)
        self.vol_slider.setMaximumWidth(60)
        self.vol_slider.setMaximumHeight(18)
        self.vol_slider.setToolTip("Volume")
        ctrl.addWidget(self.vol_slider)

        # File name label
        self.file_label = QLabel("No audio loaded")
        self.file_label.setFont(QFont("Courier New", 7))
        self.file_label.setMaximumWidth(160)
        ctrl.addWidget(self.file_label)

        layout.addLayout(ctrl)
        self.setMaximumHeight(72)

    def _connect_signals(self): #vers 1
        self._player.positionChanged.connect(self._on_position_changed)
        self._player.durationChanged.connect(self._on_duration_changed)
        self._player.playbackStateChanged.connect(self._on_state_changed)
        self.pos_slider.sliderMoved.connect(self._on_slider_moved)
        self.vol_slider.valueChanged.connect(
            lambda v: self._audio_output.setVolume(v / 100.0))
        self.waveform.seek_requested.connect(self._on_waveform_seek)

    def load_file(self, path: str): #vers 1
        """Load any supported audio file (VAG/WAV/SND)."""
        self.stop()

        # Clean up previous temp file
        if self._wav_temp and os.path.exists(self._wav_temp):
            try: os.unlink(self._wav_temp)
            except OSError: pass
            self._wav_temp = None

        self._info = get_audio_info(path)
        if not self._info.valid and self._info.format == 'unknown':
            self.file_label.setText("Unsupported format")
            return

        # Decode to WAV if needed
        wav_path = to_wav_file(path)
        if wav_path is None:
            self.file_label.setText("Decode failed")
            return

        if wav_path != path:
            self._wav_temp = wav_path

        # Build waveform peaks
        peaks = _build_peaks(wav_path)
        self.waveform.set_peaks(peaks)
        self.waveform.set_position(0.0)

        # Set media source
        self._player.setSource(QUrl.fromLocalFile(wav_path))

        name = os.path.basename(path)
        short = name[:20] + ".." if len(name) > 20 else name
        dur = self._info.duration_str if self._info else "?"
        self.file_label.setText(f"{short}  [{self._info.format.upper()}]")
        self.time_label.setText(f"0:00 / {dur}")
        self.pos_slider.setValue(0)
        self.file_loaded.emit(path)

    def play(self): #vers 1
        if self._player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self._player.pause()
            self.play_btn.setText("▶")
        else:
            self._player.play()
            self.play_btn.setText("⏸")

    def stop(self): #vers 1
        self._player.stop()
        self.play_btn.setText("▶")
        self.pos_slider.setValue(0)
        self.waveform.set_position(0.0)

    def set_volume(self, vol: float): #vers 1
        self._audio_output.setVolume(max(0.0, min(1.0, vol)))
        self.vol_slider.setValue(int(vol * 100))

    def _on_position_changed(self, ms: int): #vers 1
        dur = self._player.duration()
        if dur > 0:
            frac = ms / dur
            self.pos_slider.setValue(int(frac * 1000))
            self.waveform.set_position(frac)
        self._update_time_label(ms)

    def _on_duration_changed(self, ms: int): #vers 1
        self._update_time_label(self._player.position())

    def _on_state_changed(self, state): #vers 1
        if state == QMediaPlayer.PlaybackState.StoppedState:
            self.play_btn.setText("▶")

    def _on_slider_moved(self, value: int): #vers 1
        dur = self._player.duration()
        if dur > 0:
            self._player.setPosition(int(value * dur / 1000))

    def _on_waveform_seek(self, frac: float): #vers 1
        dur = self._player.duration()
        if dur > 0:
            self._player.setPosition(int(frac * dur))

    def _update_time_label(self, pos_ms: int): #vers 1
        dur_ms = self._player.duration()
        def fmt(ms):
            s = ms // 1000
            return f"{s//60}:{s%60:02d}"
        self.time_label.setText(f"{fmt(pos_ms)} / {fmt(dur_ms)}")

    def closeEvent(self, event): #vers 1
        self.stop()
        if self._wav_temp and os.path.exists(self._wav_temp):
            try: os.unlink(self._wav_temp)
            except OSError: pass
        super().closeEvent(event)
