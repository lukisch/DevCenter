# -*- coding: utf-8 -*-
"""
DevCenter - Settings Dialog
Einstellungen für Editor, Build, AI und mehr
"""

import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QFormLayout, QLineEdit, QSpinBox, QCheckBox, QComboBox,
    QPushButton, QLabel, QFileDialog, QGroupBox, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class SettingsDialog(QDialog):
    """
    Einstellungen-Dialog
    
    Tabs:
    - Editor: Schrift, Tab-Größe, Auto-Save
    - Build: PyInstaller-Optionen
    - AI: API-Key, Modell
    - Sync: Backup-Pfade
    - Appearance: Theme, Farben
    """
    
    def __init__(self, settings_manager, parent=None):
        super().__init__(parent)
        self.settings = settings_manager
        self.setWindowTitle("Einstellungen")
        self.setMinimumSize(600, 500)
        self._setup_ui()
        self._load_settings()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Style
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #cccccc;
            }
            QTabWidget::pane {
                border: 1px solid #3c3c3c;
                background-color: #252526;
            }
            QTabBar::tab {
                background-color: #2d2d2d;
                color: #cccccc;
                padding: 8px 16px;
                border: none;
            }
            QTabBar::tab:selected {
                background-color: #1e1e1e;
                border-bottom: 2px solid #007acc;
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
            QLineEdit, QSpinBox, QComboBox {
                background-color: #3c3c3c;
                color: #cccccc;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 4px 8px;
            }
            QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
                border-color: #007acc;
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
            QPushButton:pressed {
                background-color: #094771;
            }
            QCheckBox {
                color: #cccccc;
            }
        """)
        
        # Tab Widget
        tabs = QTabWidget()
        tabs.addTab(self._create_editor_tab(), "Editor")
        tabs.addTab(self._create_build_tab(), "Build")
        tabs.addTab(self._create_ai_tab(), "AI")
        tabs.addTab(self._create_sync_tab(), "Sync")
        tabs.addTab(self._create_appearance_tab(), "Aussehen")
        
        layout.addWidget(tabs)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.reset_btn = QPushButton("Zurücksetzen")
        self.reset_btn.clicked.connect(self._reset_settings)
        btn_layout.addWidget(self.reset_btn)
        
        self.cancel_btn = QPushButton("Abbrechen")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        
        self.save_btn = QPushButton("Speichern")
        self.save_btn.clicked.connect(self._save_settings)
        btn_layout.addWidget(self.save_btn)
        
        layout.addLayout(btn_layout)
    
    def _create_editor_tab(self) -> QWidget:
        """Editor-Einstellungen"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Schrift
        font_group = QGroupBox("Schrift")
        font_layout = QFormLayout(font_group)
        
        self.font_family = QComboBox()
        self.font_family.addItems(["Consolas", "Courier New", "Monaco", "Fira Code", "JetBrains Mono"])
        font_layout.addRow("Schriftart:", self.font_family)
        
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 24)
        self.font_size.setValue(11)
        font_layout.addRow("Schriftgröße:", self.font_size)
        
        layout.addWidget(font_group)
        
        # Verhalten
        behavior_group = QGroupBox("Verhalten")
        behavior_layout = QFormLayout(behavior_group)
        
        self.tab_size = QSpinBox()
        self.tab_size.setRange(2, 8)
        self.tab_size.setValue(4)
        behavior_layout.addRow("Tab-Breite:", self.tab_size)
        
        self.line_numbers = QCheckBox("Zeilennummern anzeigen")
        self.line_numbers.setChecked(True)
        behavior_layout.addRow("", self.line_numbers)
        
        self.auto_complete = QCheckBox("Auto-Vervollständigung")
        self.auto_complete.setChecked(True)
        behavior_layout.addRow("", self.auto_complete)
        
        self.auto_save = QCheckBox("Auto-Speichern")
        self.auto_save.setChecked(False)
        behavior_layout.addRow("", self.auto_save)
        
        self.highlight_line = QCheckBox("Aktuelle Zeile hervorheben")
        self.highlight_line.setChecked(True)
        behavior_layout.addRow("", self.highlight_line)
        
        layout.addWidget(behavior_group)
        layout.addStretch()
        
        return widget
    
    def _create_build_tab(self) -> QWidget:
        """Build-Einstellungen"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # PyInstaller
        pi_group = QGroupBox("PyInstaller")
        pi_layout = QFormLayout(pi_group)
        
        pyinstaller_row = QHBoxLayout()
        self.pyinstaller_path = QLineEdit()
        self.pyinstaller_path.setPlaceholderText("(System-Standard)")
        pyinstaller_row.addWidget(self.pyinstaller_path)
        
        browse_btn = QPushButton("...")
        browse_btn.setMaximumWidth(40)
        browse_btn.clicked.connect(lambda: self._browse_file(self.pyinstaller_path, "PyInstaller auswählen"))
        pyinstaller_row.addWidget(browse_btn)
        pi_layout.addRow("PyInstaller:", pyinstaller_row)
        
        output_row = QHBoxLayout()
        self.output_dir = QLineEdit()
        self.output_dir.setText("dist")
        output_row.addWidget(self.output_dir)
        
        browse_out_btn = QPushButton("...")
        browse_out_btn.setMaximumWidth(40)
        browse_out_btn.clicked.connect(lambda: self._browse_folder(self.output_dir, "Ausgabeverzeichnis"))
        output_row.addWidget(browse_out_btn)
        pi_layout.addRow("Ausgabe:", output_row)
        
        layout.addWidget(pi_group)
        
        # Optionen
        opt_group = QGroupBox("Standard-Optionen")
        opt_layout = QFormLayout(opt_group)
        
        self.one_file = QCheckBox("One-File Modus")
        self.one_file.setChecked(True)
        opt_layout.addRow("", self.one_file)
        
        self.console_mode = QCheckBox("Konsole anzeigen")
        self.console_mode.setChecked(True)
        opt_layout.addRow("", self.console_mode)
        
        self.use_upx = QCheckBox("UPX-Komprimierung")
        self.use_upx.setChecked(False)
        opt_layout.addRow("", self.use_upx)
        
        layout.addWidget(opt_group)
        layout.addStretch()
        
        return widget
    
    def _create_ai_tab(self) -> QWidget:
        """AI-Einstellungen"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # API
        api_group = QGroupBox("Anthropic API")
        api_layout = QFormLayout(api_group)
        
        self.api_key = QLineEdit()
        self.api_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key.setPlaceholderText("sk-...")
        api_layout.addRow("API-Key:", self.api_key)
        
        show_key = QCheckBox("Anzeigen")
        show_key.toggled.connect(lambda checked: self.api_key.setEchoMode(
            QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password
        ))
        api_layout.addRow("", show_key)
        
        layout.addWidget(api_group)
        
        # Modell
        model_group = QGroupBox("Modell")
        model_layout = QFormLayout(model_group)
        
        self.ai_model = QComboBox()
        self.ai_model.addItems(["Claude Sonnet", "Claude Opus", "Claude Haiku"])
        model_layout.addRow("Standard-Modell:", self.ai_model)
        
        self.max_tokens = QSpinBox()
        self.max_tokens.setRange(256, 8192)
        self.max_tokens.setValue(4096)
        self.max_tokens.setSingleStep(256)
        model_layout.addRow("Max Tokens:", self.max_tokens)
        
        layout.addWidget(model_group)
        
        # Info
        info_label = QLabel(
            "💡 API-Key erhältlich unter: console.anthropic.com\n"
            "Der Key wird sicher im System-Keyring gespeichert."
        )
        info_label.setStyleSheet("color: #888; font-style: italic;")
        layout.addWidget(info_label)
        
        layout.addStretch()
        
        return widget
    
    def _create_sync_tab(self) -> QWidget:
        """Sync-Einstellungen"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Backup
        backup_group = QGroupBox("Backup")
        backup_layout = QFormLayout(backup_group)
        
        backup_row = QHBoxLayout()
        self.backup_path = QLineEdit()
        self.backup_path.setPlaceholderText("Backup-Verzeichnis")
        backup_row.addWidget(self.backup_path)
        
        browse_backup = QPushButton("...")
        browse_backup.setMaximumWidth(40)
        browse_backup.clicked.connect(lambda: self._browse_folder(self.backup_path, "Backup-Verzeichnis"))
        backup_row.addWidget(browse_backup)
        backup_layout.addRow("Backup-Pfad:", backup_row)
        
        self.auto_backup = QCheckBox("Automatische Backups")
        self.auto_backup.setChecked(False)
        backup_layout.addRow("", self.auto_backup)
        
        self.backup_interval = QSpinBox()
        self.backup_interval.setRange(5, 120)
        self.backup_interval.setValue(30)
        self.backup_interval.setSuffix(" min")
        backup_layout.addRow("Intervall:", self.backup_interval)
        
        layout.addWidget(backup_group)
        
        # Ausschlüsse
        exclude_group = QGroupBox("Ausschlüsse")
        exclude_layout = QVBoxLayout(exclude_group)
        
        self.excludes_edit = QLineEdit()
        self.excludes_edit.setText("__pycache__, .git, venv, dist, build")
        self.excludes_edit.setPlaceholderText("Komma-getrennte Liste")
        exclude_layout.addWidget(self.excludes_edit)
        
        exclude_hint = QLabel("Muster für Dateien/Ordner die nicht synchronisiert werden")
        exclude_hint.setStyleSheet("color: #888; font-size: 11px;")
        exclude_layout.addWidget(exclude_hint)
        
        layout.addWidget(exclude_group)
        layout.addStretch()
        
        return widget
    
    def _create_appearance_tab(self) -> QWidget:
        """Aussehen-Einstellungen"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Theme
        theme_group = QGroupBox("Theme")
        theme_layout = QFormLayout(theme_group)
        
        self.theme = QComboBox()
        self.theme.addItems(["Dunkel", "Hell", "System"])
        theme_layout.addRow("Farbschema:", self.theme)
        
        self.editor_theme = QComboBox()
        self.editor_theme.addItems(["VS Code Dark", "Monokai", "Dracula", "One Dark"])
        theme_layout.addRow("Editor-Theme:", self.editor_theme)
        
        layout.addWidget(theme_group)
        
        # Akzentfarbe
        accent_group = QGroupBox("Akzente")
        accent_layout = QFormLayout(accent_group)
        
        self.accent_color = QComboBox()
        self.accent_color.addItems(["Blau (#007acc)", "Grün (#4ec9b0)", "Orange (#ce9178)", "Lila (#c586c0)"])
        accent_layout.addRow("Akzentfarbe:", self.accent_color)
        
        layout.addWidget(accent_group)
        layout.addStretch()
        
        return widget
    
    def _browse_file(self, line_edit: QLineEdit, title: str):
        """Datei auswählen"""
        path, _ = QFileDialog.getOpenFileName(self, title)
        if path:
            line_edit.setText(path)
    
    def _browse_folder(self, line_edit: QLineEdit, title: str):
        """Ordner auswählen"""
        path = QFileDialog.getExistingDirectory(self, title)
        if path:
            line_edit.setText(path)
    
    def _load_settings(self):
        """Lädt Einstellungen in die UI"""
        # Editor
        self.font_family.setCurrentText(self.settings.get('editor.font_family', 'Consolas'))
        self.font_size.setValue(self.settings.get('editor.font_size', 11))
        self.tab_size.setValue(self.settings.get('editor.tab_size', 4))
        self.line_numbers.setChecked(self.settings.get('editor.line_numbers', True))
        self.auto_complete.setChecked(self.settings.get('editor.auto_complete', True))
        self.auto_save.setChecked(self.settings.get('editor.auto_save', False))
        
        # Build
        self.pyinstaller_path.setText(self.settings.get('build.pyinstaller_path', ''))
        self.output_dir.setText(self.settings.get('build.output_dir', 'dist'))
        self.one_file.setChecked(self.settings.get('build.one_file', True))
        self.console_mode.setChecked(self.settings.get('build.console', True))
        self.use_upx.setChecked(self.settings.get('build.upx', False))
        
        # AI
        self.api_key.setText(self.settings.get('ai.api_key', ''))
        self.max_tokens.setValue(self.settings.get('ai.max_tokens', 4096))
        
        # Sync
        self.backup_path.setText(self.settings.get('sync.backup_path', ''))
        self.auto_backup.setChecked(self.settings.get('sync.auto_backup', False))
        
        # Appearance
        theme_map = {'dark': 0, 'light': 1, 'system': 2}
        self.theme.setCurrentIndex(theme_map.get(self.settings.get('appearance.theme', 'dark'), 0))
    
    def _save_settings(self):
        """Speichert Einstellungen"""
        # Editor
        self.settings.set('editor.font_family', self.font_family.currentText())
        self.settings.set('editor.font_size', self.font_size.value())
        self.settings.set('editor.tab_size', self.tab_size.value())
        self.settings.set('editor.line_numbers', self.line_numbers.isChecked())
        self.settings.set('editor.auto_complete', self.auto_complete.isChecked())
        self.settings.set('editor.auto_save', self.auto_save.isChecked())
        
        # Build
        self.settings.set('build.pyinstaller_path', self.pyinstaller_path.text())
        self.settings.set('build.output_dir', self.output_dir.text())
        self.settings.set('build.one_file', self.one_file.isChecked())
        self.settings.set('build.console', self.console_mode.isChecked())
        self.settings.set('build.upx', self.use_upx.isChecked())
        
        # AI
        self.settings.set('ai.api_key', self.api_key.text())
        self.settings.set('ai.max_tokens', self.max_tokens.value())
        
        # Sync
        self.settings.set('sync.backup_path', self.backup_path.text())
        self.settings.set('sync.auto_backup', self.auto_backup.isChecked())
        
        # Appearance
        themes = ['dark', 'light', 'system']
        self.settings.set('appearance.theme', themes[self.theme.currentIndex()])
        
        self.accept()
    
    def _reset_settings(self):
        """Setzt auf Standardwerte zurück"""
        reply = QMessageBox.question(
            self, "Zurücksetzen",
            "Alle Einstellungen auf Standardwerte zurücksetzen?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.settings.reset_to_defaults()
            self._load_settings()
