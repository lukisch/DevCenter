# -*- coding: utf-8 -*-
"""
DevCenter - Output Panel
Terminal-Ausgabe und Prozess-Steuerung
"""

import os
import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPlainTextEdit,
    QPushButton, QComboBox, QLabel, QToolBar
)
from PyQt6.QtCore import Qt, pyqtSignal, QProcess, QTimer
from PyQt6.QtGui import QFont, QTextCharFormat, QColor, QTextCursor


class OutputPanel(QWidget):
    """
    Terminal/Output Panel für Programmausgaben
    
    Features:
    - ANSI-Farbunterstützung (basic)
    - Prozess-Verwaltung (Start/Stop)
    - Ausgabe-Filter
    - Scrolling-Kontrolle
    """
    
    process_started = pyqtSignal(str)  # command
    process_finished = pyqtSignal(int)  # exit_code
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._process: QProcess = None
        self._auto_scroll = True
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Toolbar
        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(4, 4, 4, 4)
        
        self.run_button = QPushButton("▶ Ausführen")
        self.run_button.clicked.connect(self._on_run_clicked)
        toolbar.addWidget(self.run_button)
        
        self.stop_button = QPushButton("⬛ Stopp")
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self._on_stop_clicked)
        toolbar.addWidget(self.stop_button)
        
        toolbar.addSpacing(20)
        
        self.clear_button = QPushButton("🗑 Leeren")
        self.clear_button.clicked.connect(self.clear)
        toolbar.addWidget(self.clear_button)
        
        toolbar.addStretch()
        
        self.auto_scroll_btn = QPushButton("↓ Auto-Scroll")
        self.auto_scroll_btn.setCheckable(True)
        self.auto_scroll_btn.setChecked(True)
        self.auto_scroll_btn.clicked.connect(self._toggle_auto_scroll)
        toolbar.addWidget(self.auto_scroll_btn)
        
        layout.addLayout(toolbar)
        
        # Output Text
        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setFont(QFont("Consolas", 10))
        self.output.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1e1e1e;
                color: #cccccc;
                border: none;
                selection-background-color: #264f78;
            }
        """)
        self.output.setMaximumBlockCount(10000)  # Max Zeilen
        layout.addWidget(self.output)
        
        # Status
        self.status_label = QLabel("Bereit")
        self.status_label.setStyleSheet("padding: 2px 4px; color: #888;")
        layout.addWidget(self.status_label)
    
    def _toggle_auto_scroll(self):
        self._auto_scroll = self.auto_scroll_btn.isChecked()
    
    def _on_run_clicked(self):
        """Wird vom MainWindow überschrieben/verbunden"""
        pass
    
    def _on_stop_clicked(self):
        if self._process and self._process.state() == QProcess.ProcessState.Running:
            self._process.kill()
    
    def run_command(self, command: str, cwd: str = None):
        """
        Führt einen Shell-Befehl aus
        
        Args:
            command: Auszuführender Befehl
            cwd: Arbeitsverzeichnis
        """
        if self._process and self._process.state() == QProcess.ProcessState.Running:
            self.append_error("Ein Prozess läuft bereits!")
            return
        
        self._process = QProcess(self)
        self._process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self._process.readyReadStandardOutput.connect(self._on_output)
        self._process.finished.connect(self._on_finished)
        self._process.errorOccurred.connect(self._on_error)
        
        if cwd:
            self._process.setWorkingDirectory(cwd)
        
        # Windows vs Unix
        if sys.platform == 'win32':
            self._process.start('cmd', ['/c', command])
        else:
            self._process.start('bash', ['-c', command])
        
        self.run_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.status_label.setText(f"Läuft: {command[:50]}...")
        
        self.append_info(f"$ {command}\n")
        self.process_started.emit(command)
    
    def run_python_file(self, file_path: str, args: list = None):
        """
        Führt eine Python-Datei aus
        
        Args:
            file_path: Pfad zur Python-Datei
            args: Zusätzliche Argumente
        """
        cmd = f'"{sys.executable}" "{file_path}"'
        if args:
            cmd += ' ' + ' '.join(args)
        
        cwd = os.path.dirname(file_path)
        self.run_command(cmd, cwd)
    
    def _on_output(self):
        if self._process:
            data = self._process.readAllStandardOutput()
            text = bytes(data).decode('utf-8', errors='replace')
            self.append_output(text)
    
    def _on_finished(self, exit_code, exit_status):
        self.run_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
        if exit_code == 0:
            self.append_success(f"\n✓ Prozess beendet (Code: {exit_code})")
            self.status_label.setText("Erfolgreich beendet")
        else:
            self.append_error(f"\n✗ Prozess beendet mit Fehler (Code: {exit_code})")
            self.status_label.setText(f"Beendet mit Fehler: {exit_code}")
        
        self.process_finished.emit(exit_code)
    
    def _on_error(self, error):
        error_messages = {
            QProcess.ProcessError.FailedToStart: "Prozess konnte nicht gestartet werden",
            QProcess.ProcessError.Crashed: "Prozess abgestürzt",
            QProcess.ProcessError.Timedout: "Zeitüberschreitung",
            QProcess.ProcessError.WriteError: "Schreibfehler",
            QProcess.ProcessError.ReadError: "Lesefehler",
            QProcess.ProcessError.UnknownError: "Unbekannter Fehler"
        }
        self.append_error(f"\n⚠ {error_messages.get(error, 'Fehler')}")
    
    def append_output(self, text: str):
        """Fügt normale Ausgabe hinzu"""
        self.output.moveCursor(QTextCursor.MoveOperation.End)
        self.output.insertPlainText(text)
        
        if self._auto_scroll:
            self.output.verticalScrollBar().setValue(
                self.output.verticalScrollBar().maximum()
            )
    
    def append_info(self, text: str):
        """Fügt Info-Text hinzu (grau)"""
        cursor = self.output.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        
        fmt = QTextCharFormat()
        fmt.setForeground(QColor("#888888"))
        cursor.insertText(text, fmt)
        
        if self._auto_scroll:
            self.output.verticalScrollBar().setValue(
                self.output.verticalScrollBar().maximum()
            )
    
    def append_error(self, text: str):
        """Fügt Fehler-Text hinzu (rot)"""
        cursor = self.output.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        
        fmt = QTextCharFormat()
        fmt.setForeground(QColor("#f44747"))
        cursor.insertText(text, fmt)
        
        if self._auto_scroll:
            self.output.verticalScrollBar().setValue(
                self.output.verticalScrollBar().maximum()
            )
    
    def append_success(self, text: str):
        """Fügt Erfolgs-Text hinzu (grün)"""
        cursor = self.output.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        
        fmt = QTextCharFormat()
        fmt.setForeground(QColor("#4ec9b0"))
        cursor.insertText(text, fmt)
        
        if self._auto_scroll:
            self.output.verticalScrollBar().setValue(
                self.output.verticalScrollBar().maximum()
            )
    
    def clear(self):
        """Leert die Ausgabe"""
        self.output.clear()
        self.status_label.setText("Bereit")
    
    def is_running(self) -> bool:
        """Prüft ob ein Prozess läuft"""
        return self._process and self._process.state() == QProcess.ProcessState.Running
