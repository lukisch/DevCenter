# -*- coding: utf-8 -*-
"""
DevCenter - Build Dialog
Wizard für EXE-Erstellung
"""

import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit,
    QCheckBox, QComboBox, QPushButton, QLabel, QGroupBox,
    QFileDialog, QProgressBar, QTextEdit, QTabWidget, QWidget,
    QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from typing import Optional


class BuildWorker(QThread):
    """Worker Thread für Build-Prozess"""
    
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, kompilator, config):
        super().__init__()
        self.kompilator = kompilator
        self.config = config
    
    def run(self):
        """Fuehrt den Build-Prozess im Hintergrund aus."""
        def progress_callback(percent, message):
            self.progress.emit(percent, message)
        
        self.kompilator.set_progress_callback(progress_callback)
        result = self.kompilator.build(self.config)
        
        if result.success:
            self.finished.emit(True, result.output_path)
        else:
            self.finished.emit(False, result.error_message or "Build fehlgeschlagen")


class BuildDialog(QDialog):
    """
    Build-Dialog für EXE-Erstellung
    
    Features:
    - Basis-Konfiguration
    - Erweiterte Optionen
    - Icon-Auswahl
    - Live-Fortschritt
    - Build-Log
    """
    
    build_started = pyqtSignal()
    build_finished = pyqtSignal(bool, str)
    
    def __init__(self, script_path: str, project_path: str = None, parent=None):
        super().__init__(parent)
        self.script_path = script_path
        self.project_path = project_path or os.path.dirname(script_path)
        self._worker: Optional[BuildWorker] = None
        
        self.setWindowTitle("Build erstellen")
        self.setMinimumSize(550, 600)
        self._setup_ui()
        self._load_defaults()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Style
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #cccccc;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
                margin-top: 12px;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QLineEdit, QComboBox {
                background-color: #3c3c3c;
                color: #cccccc;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 4px 8px;
            }
            QPushButton {
                background-color: #0e639c;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 16px;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
            QPushButton:disabled {
                background-color: #3c3c3c;
                color: #888;
            }
            QCheckBox {
                color: #cccccc;
            }
            QProgressBar {
                border: 1px solid #3c3c3c;
                border-radius: 4px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #0e639c;
            }
        """)
        
        # Tabs
        tabs = QTabWidget()
        tabs.addTab(self._create_basic_tab(), "Basis")
        tabs.addTab(self._create_advanced_tab(), "Erweitert")
        tabs.addTab(self._create_files_tab(), "Dateien")
        
        layout.addWidget(tabs)
        
        # Progress
        progress_group = QGroupBox("Fortschritt")
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Bereit")
        self.status_label.setStyleSheet("color: #888;")
        progress_layout.addWidget(self.status_label)
        
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMaximumHeight(120)
        self.log_output.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #cccccc;
                border: 1px solid #3c3c3c;
                font-family: Consolas;
                font-size: 10px;
            }
        """)
        progress_layout.addWidget(self.log_output)
        
        layout.addWidget(progress_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.cancel_btn = QPushButton("Abbrechen")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        
        self.build_btn = QPushButton("🔨 Build starten")
        self.build_btn.clicked.connect(self._start_build)
        btn_layout.addWidget(self.build_btn)
        
        layout.addLayout(btn_layout)
    
    def _create_basic_tab(self) -> QWidget:
        """Basis-Einstellungen"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Skript
        script_group = QGroupBox("Skript")
        script_layout = QFormLayout(script_group)
        
        self.script_input = QLineEdit()
        self.script_input.setText(self.script_path)
        self.script_input.setReadOnly(True)
        script_layout.addRow("Datei:", self.script_input)
        
        self.name_input = QLineEdit()
        self.name_input.setText(os.path.splitext(os.path.basename(self.script_path))[0])
        script_layout.addRow("Name:", self.name_input)
        
        layout.addWidget(script_group)
        
        # Ausgabe
        output_group = QGroupBox("Ausgabe")
        output_layout = QFormLayout(output_group)
        
        output_row = QHBoxLayout()
        self.output_input = QLineEdit()
        self.output_input.setText(os.path.join(self.project_path, "dist"))
        output_row.addWidget(self.output_input)
        
        browse_btn = QPushButton("...")
        browse_btn.setMaximumWidth(40)
        browse_btn.clicked.connect(self._browse_output)
        output_row.addWidget(browse_btn)
        output_layout.addRow("Verzeichnis:", output_row)
        
        layout.addWidget(output_group)
        
        # Optionen
        options_group = QGroupBox("Optionen")
        options_layout = QVBoxLayout(options_group)
        
        self.one_file_check = QCheckBox("One-File (einzelne EXE)")
        self.one_file_check.setChecked(True)
        options_layout.addWidget(self.one_file_check)
        
        self.console_check = QCheckBox("Konsole anzeigen")
        self.console_check.setChecked(True)
        options_layout.addWidget(self.console_check)
        
        self.clean_check = QCheckBox("Alte Build-Dateien löschen")
        self.clean_check.setChecked(True)
        options_layout.addWidget(self.clean_check)
        
        layout.addWidget(options_group)
        
        # Icon
        icon_group = QGroupBox("Icon")
        icon_layout = QHBoxLayout(icon_group)
        
        self.icon_input = QLineEdit()
        self.icon_input.setPlaceholderText("(Standard-Icon)")
        icon_layout.addWidget(self.icon_input)
        
        browse_icon_btn = QPushButton("...")
        browse_icon_btn.setMaximumWidth(40)
        browse_icon_btn.clicked.connect(self._browse_icon)
        icon_layout.addWidget(browse_icon_btn)
        
        layout.addWidget(icon_group)
        layout.addStretch()
        
        return widget
    
    def _create_advanced_tab(self) -> QWidget:
        """Erweiterte Einstellungen"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Optimierung
        opt_group = QGroupBox("Optimierung")
        opt_layout = QVBoxLayout(opt_group)
        
        self.upx_check = QCheckBox("UPX-Komprimierung verwenden")
        opt_layout.addWidget(self.upx_check)
        
        self.strip_check = QCheckBox("Debug-Symbole entfernen")
        opt_layout.addWidget(self.strip_check)
        
        layout.addWidget(opt_group)
        
        # Metadaten
        meta_group = QGroupBox("Metadaten (optional)")
        meta_layout = QFormLayout(meta_group)
        
        self.version_input = QLineEdit()
        self.version_input.setPlaceholderText("1.0.0")
        meta_layout.addRow("Version:", self.version_input)
        
        self.company_input = QLineEdit()
        self.company_input.setPlaceholderText("Firmenname")
        meta_layout.addRow("Firma:", self.company_input)
        
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Beschreibung der Anwendung")
        meta_layout.addRow("Beschreibung:", self.description_input)
        
        self.copyright_input = QLineEdit()
        self.copyright_input.setPlaceholderText("© 2026")
        meta_layout.addRow("Copyright:", self.copyright_input)
        
        layout.addWidget(meta_group)
        layout.addStretch()
        
        return widget
    
    def _create_files_tab(self) -> QWidget:
        """Zusätzliche Dateien"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Hidden Imports
        imports_group = QGroupBox("Hidden Imports")
        imports_layout = QVBoxLayout(imports_group)
        
        self.imports_list = QListWidget()
        self.imports_list.setMaximumHeight(100)
        imports_layout.addWidget(self.imports_list)
        
        imports_btn_layout = QHBoxLayout()
        
        self.import_input = QLineEdit()
        self.import_input.setPlaceholderText("Modul-Name")
        imports_btn_layout.addWidget(self.import_input)
        
        add_import_btn = QPushButton("+")
        add_import_btn.setMaximumWidth(40)
        add_import_btn.clicked.connect(self._add_import)
        imports_btn_layout.addWidget(add_import_btn)
        
        remove_import_btn = QPushButton("-")
        remove_import_btn.setMaximumWidth(40)
        remove_import_btn.clicked.connect(self._remove_import)
        imports_btn_layout.addWidget(remove_import_btn)
        
        imports_layout.addLayout(imports_btn_layout)
        
        layout.addWidget(imports_group)
        
        # Data Files
        data_group = QGroupBox("Zusätzliche Dateien")
        data_layout = QVBoxLayout(data_group)
        
        self.data_list = QListWidget()
        self.data_list.setMaximumHeight(100)
        data_layout.addWidget(self.data_list)
        
        add_data_btn = QPushButton("Datei hinzufügen...")
        add_data_btn.clicked.connect(self._add_data_file)
        data_layout.addWidget(add_data_btn)
        
        layout.addWidget(data_group)
        
        # Exclude
        exclude_group = QGroupBox("Ausgeschlossene Module")
        exclude_layout = QVBoxLayout(exclude_group)
        
        self.exclude_input = QLineEdit()
        self.exclude_input.setPlaceholderText("Komma-getrennt: tkinter, unittest")
        exclude_layout.addWidget(self.exclude_input)
        
        layout.addWidget(exclude_group)
        layout.addStretch()
        
        return widget
    
    def _load_defaults(self):
        """Lädt Standard-Werte"""
        # Prüfen ob requirements.txt Hidden Imports hat
        req_path = os.path.join(self.project_path, "requirements.txt")
        if os.path.exists(req_path):
            try:
                with open(req_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            pkg = line.split('==')[0].split('>=')[0].split('[')[0]
                            self.imports_list.addItem(pkg)
            except:
                pass
    
    def _browse_output(self):
        """Ausgabeverzeichnis wählen"""
        path = QFileDialog.getExistingDirectory(self, "Ausgabeverzeichnis")
        if path:
            self.output_input.setText(path)
    
    def _browse_icon(self):
        """Icon-Datei wählen"""
        path, _ = QFileDialog.getOpenFileName(
            self, "Icon auswählen",
            filter="Icons (*.ico);;Bilder (*.png *.jpg)"
        )
        if path:
            self.icon_input.setText(path)
    
    def _add_import(self):
        """Hidden Import hinzufügen"""
        name = self.import_input.text().strip()
        if name:
            self.imports_list.addItem(name)
            self.import_input.clear()
    
    def _remove_import(self):
        """Hidden Import entfernen"""
        row = self.imports_list.currentRow()
        if row >= 0:
            self.imports_list.takeItem(row)
    
    def _add_data_file(self):
        """Daten-Datei hinzufügen"""
        path, _ = QFileDialog.getOpenFileName(self, "Datei hinzufügen")
        if path:
            self.data_list.addItem(path)
    
    def _start_build(self):
        """Startet den Build"""
        # Import hier um zirkuläre Imports zu vermeiden
        try:
            from ...modules.builder import Kompilator, BuildConfig
        except ImportError:
            self.log_output.append("❌ Builder-Modul nicht verfügbar")
            return
        
        # Config erstellen
        hidden_imports = [
            self.imports_list.item(i).text() 
            for i in range(self.imports_list.count())
        ]
        
        data_files = []
        for i in range(self.data_list.count()):
            path = self.data_list.item(i).text()
            data_files.append((path, '.'))
        
        exclude = [
            m.strip() for m in self.exclude_input.text().split(',')
            if m.strip()
        ]
        
        config = BuildConfig(
            script_path=self.script_path,
            output_dir=self.output_input.text(),
            name=self.name_input.text(),
            one_file=self.one_file_check.isChecked(),
            console=self.console_check.isChecked(),
            icon=self.icon_input.text() or None,
            hidden_imports=hidden_imports,
            exclude_modules=exclude,
            data_files=data_files,
            upx=self.upx_check.isChecked(),
            strip=self.strip_check.isChecked(),
            clean=self.clean_check.isChecked(),
            version=self.version_input.text() or None,
            company=self.company_input.text() or None,
            copyright=self.copyright_input.text() or None,
            description=self.description_input.text() or None
        )
        
        # UI deaktivieren
        self.build_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.log_output.clear()
        self.status_label.setText("Build läuft...")
        
        # Worker starten
        kompilator = Kompilator()
        self._worker = BuildWorker(kompilator, config)
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_finished)
        self._worker.start()
        
        self.build_started.emit()
    
    def _on_progress(self, percent: int, message: str):
        """Fortschritts-Update"""
        self.progress_bar.setValue(percent)
        self.status_label.setText(message[:80])
        self.log_output.append(message)
    
    def _on_finished(self, success: bool, result: str):
        """Build abgeschlossen"""
        self.build_btn.setEnabled(True)
        
        if success:
            self.progress_bar.setValue(100)
            self.status_label.setText("✅ Build erfolgreich!")
            self.log_output.append(f"\n✅ Ausgabe: {result}")
            self.build_finished.emit(True, result)
        else:
            self.status_label.setText("❌ Build fehlgeschlagen")
            self.log_output.append(f"\n❌ Fehler: {result}")
            self.build_finished.emit(False, result)
