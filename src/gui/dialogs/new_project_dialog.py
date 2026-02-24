# -*- coding: utf-8 -*-
"""
DevCenter - New Project Dialog
Dialog zum Erstellen eines neuen Projekts
"""

import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QTextEdit, QPushButton, QFileDialog,
    QLabel, QComboBox, QGroupBox, QCheckBox
)
from PyQt6.QtCore import Qt


class NewProjectDialog(QDialog):
    """Dialog zum Erstellen eines neuen Projekts"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Neues Projekt erstellen")
        self.setMinimumSize(500, 400)
        self.setModal(True)
        
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self):
        """Erstellt das UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        
        # Titel
        title = QLabel("🚀 Neues Python-Projekt")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #007acc;")
        layout.addWidget(title)
        
        # Projektdetails
        details_group = QGroupBox("Projektdetails")
        details_layout = QFormLayout(details_group)
        
        # Projektname
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Mein Python Projekt")
        self.name_edit.textChanged.connect(self._update_path)
        details_layout.addRow("Name:", self.name_edit)
        
        # Speicherort
        path_layout = QHBoxLayout()
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Projektverzeichnis wählen...")
        default_path = str(Path.home() / "Documents" / "DevCenter Projects")
        self.path_edit.setText(default_path)
        path_layout.addWidget(self.path_edit)
        
        browse_btn = QPushButton("📁 Durchsuchen")
        browse_btn.clicked.connect(self._browse_path)
        path_layout.addWidget(browse_btn)
        
        details_layout.addRow("Speicherort:", path_layout)
        
        # Vollständiger Pfad (nur Anzeige)
        self.full_path_label = QLabel()
        self.full_path_label.setStyleSheet("color: #888888; font-size: 11px;")
        details_layout.addRow("Vollständiger Pfad:", self.full_path_label)
        
        layout.addWidget(details_group)
        
        # Beschreibung
        desc_group = QGroupBox("Beschreibung (optional)")
        desc_layout = QVBoxLayout(desc_group)
        
        self.desc_edit = QTextEdit()
        self.desc_edit.setPlaceholderText("Projektbeschreibung eingeben...")
        self.desc_edit.setMaximumHeight(80)
        desc_layout.addWidget(self.desc_edit)
        
        layout.addWidget(desc_group)
        
        # Optionen
        options_group = QGroupBox("Optionen")
        options_layout = QVBoxLayout(options_group)
        
        self.git_check = QCheckBox("Git-Repository initialisieren")
        self.git_check.setChecked(True)
        options_layout.addWidget(self.git_check)
        
        self.venv_check = QCheckBox("Virtual Environment erstellen")
        self.venv_check.setChecked(False)
        options_layout.addWidget(self.venv_check)
        
        # Template-Auswahl
        template_layout = QHBoxLayout()
        template_layout.addWidget(QLabel("Projektvorlage:"))
        self.template_combo = QComboBox()
        self.template_combo.addItems([
            "Leeres Projekt",
            "CLI-Anwendung",
            "GUI-Anwendung (PyQt6)",
            "Web-API (Flask)",
            "Package/Library"
        ])
        template_layout.addWidget(self.template_combo)
        template_layout.addStretch()
        options_layout.addLayout(template_layout)
        
        layout.addWidget(options_group)
        
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Abbrechen")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        self.create_btn = QPushButton("✨ Projekt erstellen")
        self.create_btn.setDefault(True)
        self.create_btn.clicked.connect(self._validate_and_accept)
        button_layout.addWidget(self.create_btn)
        
        layout.addLayout(button_layout)
        
        # Initial-Update
        self._update_path()
    
    def _apply_styles(self):
        """Wendet Styles an"""
        self.setStyleSheet("""
            QDialog {
                background-color: #252526;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
                margin-top: 8px;
                padding: 12px;
                color: #cccccc;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 4px;
            }
            QLineEdit, QTextEdit, QComboBox {
                background-color: #3c3c3c;
                color: #cccccc;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 6px;
            }
            QLineEdit:focus, QTextEdit:focus {
                border: 1px solid #007acc;
            }
            QPushButton {
                background-color: #3c3c3c;
                color: #cccccc;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #505050;
            }
            QPushButton:default {
                background-color: #0e639c;
            }
            QPushButton:default:hover {
                background-color: #1177bb;
            }
            QLabel {
                color: #cccccc;
            }
            QCheckBox {
                color: #cccccc;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
        """)
    
    def _browse_path(self):
        """Öffnet den Verzeichnis-Dialog"""
        path = QFileDialog.getExistingDirectory(
            self, "Speicherort wählen",
            self.path_edit.text(),
            QFileDialog.Option.ShowDirsOnly
        )
        if path:
            self.path_edit.setText(path)
            self._update_path()
    
    def _update_path(self):
        """Aktualisiert die Pfadanzeige"""
        name = self.name_edit.text().strip()
        base_path = self.path_edit.text().strip()
        
        if name and base_path:
            # Sicherer Ordnername
            safe_name = "".join(c for c in name if c.isalnum() or c in " _-")
            safe_name = safe_name.replace(" ", "_")
            
            full_path = str(Path(base_path) / safe_name)
            self.full_path_label.setText(full_path)
        else:
            self.full_path_label.setText("")
    
    def _validate_and_accept(self):
        """Validiert die Eingaben und schließt den Dialog"""
        name = self.name_edit.text().strip()
        base_path = self.path_edit.text().strip()
        
        if not name:
            self.name_edit.setFocus()
            self.name_edit.setStyleSheet("border: 1px solid #cc0000;")
            return
        
        if not base_path or not os.path.exists(base_path):
            self.path_edit.setFocus()
            return
        
        # Prüfen ob Zielverzeichnis bereits existiert
        safe_name = "".join(c for c in name if c.isalnum() or c in " _-")
        safe_name = safe_name.replace(" ", "_")
        full_path = Path(base_path) / safe_name
        
        if full_path.exists():
            from PyQt6.QtWidgets import QMessageBox
            result = QMessageBox.question(
                self, "Verzeichnis existiert",
                f"Das Verzeichnis '{full_path}' existiert bereits.\nTrotzdem fortfahren?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if result != QMessageBox.StandardButton.Yes:
                return
        
        self.accept()
    
    def get_values(self) -> tuple:
        """
        Gibt die eingegebenen Werte zurück
        
        Returns:
            Tuple (name, path, description)
        """
        name = self.name_edit.text().strip()
        base_path = self.path_edit.text().strip()
        
        # Sicherer Ordnername
        safe_name = "".join(c for c in name if c.isalnum() or c in " _-")
        safe_name = safe_name.replace(" ", "_")
        
        full_path = str(Path(base_path) / safe_name)
        description = self.desc_edit.toPlainText().strip()
        
        return name, full_path, description
    
    def get_options(self) -> dict:
        """
        Gibt die ausgewählten Optionen zurück
        
        Returns:
            Dict mit Optionen
        """
        return {
            'init_git': self.git_check.isChecked(),
            'create_venv': self.venv_check.isChecked(),
            'template': self.template_combo.currentText()
        }


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    dialog = NewProjectDialog()
    if dialog.exec():
        print("Name, Path, Desc:", dialog.get_values())
        print("Options:", dialog.get_options())
    sys.exit()
