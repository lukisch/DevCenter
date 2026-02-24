# -*- coding: utf-8 -*-
"""
DevCenter - Main Window
Hauptfenster der Anwendung mit vollständiger Panel-Integration
"""

import sys
import os
from pathlib import Path
from typing import Optional, Dict

from PyQt6.QtWidgets import (
    QMainWindow, QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QMenuBar, QMenu, QToolBar, QStatusBar, QSplitter,
    QLabel, QPushButton, QMessageBox, QFileDialog, QDockWidget
)
from PyQt6.QtCore import Qt, QTimer, QSize, pyqtSignal
from PyQt6.QtGui import QAction, QFont, QKeySequence

# Lokale Imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.project_manager import ProjectManager, ProjectConfig
from core.settings_manager import SettingsManager, get_settings
from core.event_bus import EventBus, EventType, get_event_bus
from modules.editor.code_editor import CodeEditor
from modules.analyzer import MethodAnalyzer, AnalysisResult
from modules.ai_assistant import AIService

# GUI Imports
from gui.panels.explorer_panel import ExplorerPanel
from gui.panels.output_panel import OutputPanel
from gui.panels.problems_panel import ProblemsPanel, Problem, ProblemSeverity
from gui.panels.ai_panel import AIAssistantPanel
from gui.dialogs.new_project_dialog import NewProjectDialog
from gui.dialogs.settings_dialog import SettingsDialog
from gui.dialogs.build_dialog import BuildDialog


class MainWindow(QMainWindow):
    """
    DevCenter Hauptfenster
    
    Layout:
    ┌─────────────────────────────────────────────────────────────┐
    │  Menüleiste                                                 │
    ├─────────────────────────────────────────────────────────────┤
    │  Toolbar                                                    │
    ├────────────┬────────────────────────────┬───────────────────┤
    │            │                            │                   │
    │  Explorer  │     Editor (Tabs)          │   AI Assistant    │
    │            │                            │   (optional)      │
    │            ├────────────────────────────┤                   │
    │            │   Output / Problems        │                   │
    │            │                            │                   │
    ├────────────┴────────────────────────────┴───────────────────┤
    │  Statusleiste                                               │
    └─────────────────────────────────────────────────────────────┘
    """
    
    def __init__(self):
        super().__init__()
        
        # Manager initialisieren
        self.settings = get_settings()
        self.project_manager = ProjectManager()
        self.event_bus = get_event_bus()
        self.analyzer = MethodAnalyzer()
        self.ai_service = AIService(self.settings.get('ai.api_key', ''))
        
        # Aktives Projekt
        self.current_project: Optional[ProjectConfig] = None
        self.open_files: Dict[str, CodeEditor] = {}
        
        # UI Setup
        self.setWindowTitle("DevCenter")
        self.setMinimumSize(1200, 800)
        
        self._apply_dark_theme()
        self._setup_ui()
        self._setup_menus()
        self._setup_toolbar()
        self._setup_statusbar()
        self._setup_connections()
        self._restore_state()
        
        # Welcome oder letztes Projekt
        self._show_welcome()
    
    def _apply_dark_theme(self):
        """Wendet das dunkle Theme an"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QMenuBar {
                background-color: #252526;
                color: #cccccc;
                border-bottom: 1px solid #3c3c3c;
            }
            QMenuBar::item:selected {
                background-color: #094771;
            }
            QMenu {
                background-color: #252526;
                color: #cccccc;
                border: 1px solid #3c3c3c;
            }
            QMenu::item:selected {
                background-color: #094771;
            }
            QToolBar {
                background-color: #252526;
                border: none;
                spacing: 4px;
                padding: 4px;
            }
            QToolBar::separator {
                width: 1px;
                background-color: #3c3c3c;
                margin: 4px 8px;
            }
            QToolButton {
                background-color: transparent;
                color: #cccccc;
                border: none;
                border-radius: 4px;
                padding: 4px 8px;
            }
            QToolButton:hover {
                background-color: #3c3c3c;
            }
            QToolButton:pressed {
                background-color: #094771;
            }
            QStatusBar {
                background-color: #007acc;
                color: white;
            }
            QTabWidget::pane {
                border: none;
                background-color: #1e1e1e;
            }
            QTabBar::tab {
                background-color: #2d2d2d;
                color: #969696;
                padding: 8px 16px;
                border: none;
                border-right: 1px solid #252526;
            }
            QTabBar::tab:selected {
                background-color: #1e1e1e;
                color: #ffffff;
                border-bottom: 2px solid #007acc;
            }
            QTabBar::tab:hover:!selected {
                background-color: #2a2d2e;
            }
            QTabBar::close-button {
                image: url(close.png);
            }
            QSplitter::handle {
                background-color: #252526;
            }
            QSplitter::handle:horizontal {
                width: 2px;
            }
            QSplitter::handle:vertical {
                height: 2px;
            }
        """)
    
    def _setup_ui(self):
        """Erstellt das UI-Layout"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Haupt-Splitter (horizontal)
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(self.main_splitter)
        
        # --- Linke Seitenleiste (Explorer) ---
        self.explorer_panel = ExplorerPanel()
        self.explorer_panel.setMinimumWidth(200)
        self.explorer_panel.setMaximumWidth(400)
        self.main_splitter.addWidget(self.explorer_panel)
        
        # --- Mittlerer Bereich (Editor + Output) ---
        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(0)
        
        # Editor-Tabs
        self.editor_tabs = QTabWidget()
        self.editor_tabs.setTabsClosable(True)
        self.editor_tabs.setMovable(True)
        self.editor_tabs.setDocumentMode(True)
        center_layout.addWidget(self.editor_tabs, stretch=3)
        
        # Output-Splitter (vertikal)
        self.output_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Output Tabs (Terminal + Problems)
        self.output_tabs = QTabWidget()
        self.output_tabs.setMaximumHeight(250)
        
        self.output_panel = OutputPanel()
        self.output_tabs.addTab(self.output_panel, "🖥️ Terminal")
        
        self.problems_panel = ProblemsPanel()
        self.output_tabs.addTab(self.problems_panel, "⚠️ Probleme")
        
        center_layout.addWidget(self.output_tabs, stretch=1)
        
        self.main_splitter.addWidget(center_widget)
        
        # --- Rechte Seitenleiste (AI Assistant) ---
        self.ai_panel = AIAssistantPanel()
        self.ai_panel.setMinimumWidth(300)
        self.ai_panel.setMaximumWidth(500)
        self.ai_panel.set_ai_service(self.ai_service)
        self.ai_panel.setVisible(False)  # Standardmäßig versteckt
        self.main_splitter.addWidget(self.ai_panel)
        
        # Splitter-Größen
        self.main_splitter.setSizes([250, 700, 350])
        
        # Welcome-Widget für leeren Editor-Bereich
        self.welcome_widget = self._create_welcome_widget()
        self.editor_tabs.addTab(self.welcome_widget, "🏠 Willkommen")
    
    def _create_welcome_widget(self) -> QWidget:
        """Erstellt den Willkommens-Bildschirm"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Logo/Titel
        title = QLabel("🚀 DevCenter")
        title.setStyleSheet("font-size: 48px; color: #007acc; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        subtitle = QLabel("Python Development Suite")
        subtitle.setStyleSheet("font-size: 18px; color: #888; margin-bottom: 30px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)
        
        # Aktionen
        actions_layout = QVBoxLayout()
        actions_layout.setSpacing(10)
        actions_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        new_project_btn = QPushButton("📁 Neues Projekt erstellen")
        new_project_btn.setStyleSheet(self._get_welcome_button_style())
        new_project_btn.clicked.connect(self._new_project)
        actions_layout.addWidget(new_project_btn)
        
        open_project_btn = QPushButton("📂 Projekt öffnen")
        open_project_btn.setStyleSheet(self._get_welcome_button_style())
        open_project_btn.clicked.connect(self._open_project)
        actions_layout.addWidget(open_project_btn)
        
        open_file_btn = QPushButton("📄 Datei öffnen")
        open_file_btn.setStyleSheet(self._get_welcome_button_style())
        open_file_btn.clicked.connect(self._open_file)
        actions_layout.addWidget(open_file_btn)
        
        layout.addLayout(actions_layout)
        
        # Letzte Projekte
        layout.addSpacing(30)
        recent_label = QLabel("Letzte Projekte:")
        recent_label.setStyleSheet("color: #888; font-size: 14px;")
        layout.addWidget(recent_label)
        
        recent_projects = self.project_manager.get_recent_projects()
        for project in recent_projects[:5]:
            btn = QPushButton(f"  📁 {project['name']}")
            btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    color: #4ec9b0;
                    border: none;
                    text-align: left;
                    padding: 4px;
                }
                QPushButton:hover {
                    color: #007acc;
                    text-decoration: underline;
                }
            """)
            btn.setProperty("project_path", project['path'])
            btn.clicked.connect(lambda checked, p=project['path']: self._open_project_path(p))
            layout.addWidget(btn)
        
        layout.addStretch()
        
        return widget
    
    def _get_welcome_button_style(self) -> str:
        return """
            QPushButton {
                background-color: #0e639c;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 12px 24px;
                font-size: 14px;
                min-width: 250px;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
            QPushButton:pressed {
                background-color: #094771;
            }
        """
    
    def _setup_menus(self):
        """Erstellt die Menüleiste"""
        menubar = self.menuBar()
        
        # === Datei-Menü ===
        file_menu = menubar.addMenu("&Datei")
        
        new_project_action = QAction("Neues Projekt...", self)
        new_project_action.setShortcut(QKeySequence("Ctrl+Shift+N"))
        new_project_action.triggered.connect(self._new_project)
        file_menu.addAction(new_project_action)
        
        open_project_action = QAction("Projekt öffnen...", self)
        open_project_action.setShortcut(QKeySequence("Ctrl+Shift+O"))
        open_project_action.triggered.connect(self._open_project)
        file_menu.addAction(open_project_action)
        
        file_menu.addSeparator()
        
        new_file_action = QAction("Neue Datei", self)
        new_file_action.setShortcut(QKeySequence("Ctrl+N"))
        new_file_action.triggered.connect(self._new_file)
        file_menu.addAction(new_file_action)
        
        open_file_action = QAction("Datei öffnen...", self)
        open_file_action.setShortcut(QKeySequence("Ctrl+O"))
        open_file_action.triggered.connect(self._open_file)
        file_menu.addAction(open_file_action)
        
        file_menu.addSeparator()
        
        save_action = QAction("Speichern", self)
        save_action.setShortcut(QKeySequence("Ctrl+S"))
        save_action.triggered.connect(self._save_file)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Speichern unter...", self)
        save_as_action.setShortcut(QKeySequence("Ctrl+Shift+S"))
        save_as_action.triggered.connect(self._save_file_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        settings_action = QAction("Einstellungen...", self)
        settings_action.setShortcut(QKeySequence("Ctrl+,"))
        settings_action.triggered.connect(self._show_settings)
        file_menu.addAction(settings_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Beenden", self)
        exit_action.setShortcut(QKeySequence("Alt+F4"))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # === Bearbeiten-Menü ===
        edit_menu = menubar.addMenu("&Bearbeiten")
        
        undo_action = QAction("Rückgängig", self)
        undo_action.setShortcut(QKeySequence("Ctrl+Z"))
        undo_action.triggered.connect(self._undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("Wiederholen", self)
        redo_action.setShortcut(QKeySequence("Ctrl+Y"))
        redo_action.triggered.connect(self._redo)
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        cut_action = QAction("Ausschneiden", self)
        cut_action.setShortcut(QKeySequence("Ctrl+X"))
        cut_action.triggered.connect(self._cut)
        edit_menu.addAction(cut_action)
        
        copy_action = QAction("Kopieren", self)
        copy_action.setShortcut(QKeySequence("Ctrl+C"))
        copy_action.triggered.connect(self._copy)
        edit_menu.addAction(copy_action)
        
        paste_action = QAction("Einfügen", self)
        paste_action.setShortcut(QKeySequence("Ctrl+V"))
        paste_action.triggered.connect(self._paste)
        edit_menu.addAction(paste_action)
        
        edit_menu.addSeparator()
        
        find_action = QAction("Suchen...", self)
        find_action.setShortcut(QKeySequence("Ctrl+F"))
        find_action.triggered.connect(self._find)
        edit_menu.addAction(find_action)
        
        replace_action = QAction("Ersetzen...", self)
        replace_action.setShortcut(QKeySequence("Ctrl+H"))
        replace_action.triggered.connect(self._replace)
        edit_menu.addAction(replace_action)
        
        # === Ansicht-Menü ===
        view_menu = menubar.addMenu("&Ansicht")
        
        self.toggle_explorer_action = QAction("Explorer", self)
        self.toggle_explorer_action.setCheckable(True)
        self.toggle_explorer_action.setChecked(True)
        self.toggle_explorer_action.triggered.connect(self._toggle_explorer)
        view_menu.addAction(self.toggle_explorer_action)
        
        self.toggle_output_action = QAction("Ausgabe", self)
        self.toggle_output_action.setCheckable(True)
        self.toggle_output_action.setChecked(True)
        self.toggle_output_action.triggered.connect(self._toggle_output)
        view_menu.addAction(self.toggle_output_action)
        
        self.toggle_ai_action = QAction("AI-Assistent", self)
        self.toggle_ai_action.setCheckable(True)
        self.toggle_ai_action.setChecked(False)
        self.toggle_ai_action.setShortcut(QKeySequence("Ctrl+Shift+A"))
        self.toggle_ai_action.triggered.connect(self._toggle_ai_panel)
        view_menu.addAction(self.toggle_ai_action)
        
        # === Ausführen-Menü ===
        run_menu = menubar.addMenu("&Ausführen")
        
        run_action = QAction("▶ Ausführen", self)
        run_action.setShortcut(QKeySequence("F5"))
        run_action.triggered.connect(self._run_current)
        run_menu.addAction(run_action)
        
        run_menu.addSeparator()
        
        build_action = QAction("🔨 Build erstellen...", self)
        build_action.setShortcut(QKeySequence("F6"))
        build_action.triggered.connect(self._show_build_dialog)
        run_menu.addAction(build_action)
        
        # === Analyse-Menü ===
        analyze_menu = menubar.addMenu("&Analyse")
        
        analyze_file_action = QAction("📊 Aktuelle Datei analysieren", self)
        analyze_file_action.setShortcut(QKeySequence("Ctrl+Shift+A"))
        analyze_file_action.triggered.connect(self._analyze_current_file)
        analyze_menu.addAction(analyze_file_action)
        
        analyze_project_action = QAction("📊 Projekt analysieren", self)
        analyze_project_action.triggered.connect(self._analyze_project)
        analyze_menu.addAction(analyze_project_action)
        
        # === Hilfe-Menü ===
        help_menu = menubar.addMenu("&Hilfe")
        
        about_action = QAction("Über DevCenter", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _setup_toolbar(self):
        """Erstellt die Toolbar"""
        toolbar = QToolBar("Hauptwerkzeugleiste")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(20, 20))
        self.addToolBar(toolbar)
        
        # Projekt-Aktionen
        toolbar.addAction("📁 Neu").triggered.connect(self._new_project)
        toolbar.addAction("📂 Öffnen").triggered.connect(self._open_project)
        toolbar.addSeparator()
        
        # Datei-Aktionen
        toolbar.addAction("💾 Speichern").triggered.connect(self._save_file)
        toolbar.addSeparator()
        
        # Ausführen
        toolbar.addAction("▶ Ausführen").triggered.connect(self._run_current)
        toolbar.addAction("🔨 Build").triggered.connect(self._show_build_dialog)
        toolbar.addSeparator()
        
        # Analyse
        toolbar.addAction("📊 Analysieren").triggered.connect(self._analyze_current_file)
        toolbar.addSeparator()
        
        # AI
        self.ai_toolbar_btn = toolbar.addAction("🤖 AI")
        self.ai_toolbar_btn.setCheckable(True)
        self.ai_toolbar_btn.triggered.connect(self._toggle_ai_panel)
    
    def _setup_statusbar(self):
        """Erstellt die Statusleiste"""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        
        # Projekt-Name
        self.project_label = QLabel("Kein Projekt")
        self.statusbar.addWidget(self.project_label)
        
        # Spacer
        spacer = QWidget()
        spacer.setFixedWidth(20)
        self.statusbar.addWidget(spacer)
        
        # Cursor-Position
        self.cursor_label = QLabel("Ln 1, Col 1")
        self.statusbar.addPermanentWidget(self.cursor_label)
        
        # Encoding
        self.encoding_label = QLabel("UTF-8")
        self.statusbar.addPermanentWidget(self.encoding_label)
    
    def _setup_connections(self):
        """Verbindet Signale"""
        # Explorer
        self.explorer_panel.file_selected.connect(self._open_file_path)
        
        # Editor Tabs
        self.editor_tabs.tabCloseRequested.connect(self._close_tab)
        self.editor_tabs.currentChanged.connect(self._on_tab_changed)
        
        # Problems Panel
        self.problems_panel.problem_clicked.connect(self._goto_problem)
        
        # AI Panel
        self.ai_panel.code_generated.connect(self._on_code_generated)
        
        # Event Bus
        self.event_bus.subscribe(EventType.STATUS_MESSAGE, self._on_status_message)
    
    def _restore_state(self):
        """Stellt den Fensterzustand wieder her"""
        state = self.settings.get('window.state', {})
        
        if 'geometry' in state:
            pass  # TODO: Geometrie wiederherstellen
        
        if 'maximized' in state and state['maximized']:
            self.showMaximized()
    
    def _show_welcome(self):
        """Zeigt Welcome-Screen oder öffnet letztes Projekt"""
        # Prüfen ob letztes Projekt geöffnet werden soll
        if self.settings.get('general.open_last_project', False):
            recent = self.project_manager.get_recent_projects()
            if recent:
                self._open_project_path(recent[0]['path'])
    
    # === Datei-Operationen ===
    
    def _new_project(self):
        """Erstellt ein neues Projekt"""
        dialog = NewProjectDialog(self)
        if dialog.exec():
            name, path, description = dialog.get_project_info()
            options = dialog.get_options()
            
            project = self.project_manager.create_project(name, path, description)
            if project:
                self._load_project(project)
    
    def _open_project(self):
        """Öffnet ein bestehendes Projekt"""
        path = QFileDialog.getExistingDirectory(self, "Projekt öffnen")
        if path:
            self._open_project_path(path)
    
    def _open_project_path(self, path: str):
        """Öffnet ein Projekt von einem Pfad"""
        project = self.project_manager.open_project(path)
        if project:
            self._load_project(project)
        else:
            QMessageBox.warning(self, "Fehler", f"Projekt konnte nicht geöffnet werden:\n{path}")
    
    def _load_project(self, project: ProjectConfig):
        """Lädt ein Projekt in die UI"""
        self.current_project = project
        self.explorer_panel.set_root_path(project.path)
        self.project_label.setText(f"📁 {project.name}")
        self.setWindowTitle(f"DevCenter - {project.name}")
        
        # Hauptdatei öffnen wenn vorhanden
        if project.main_file:
            main_path = os.path.join(project.path, project.main_file)
            if os.path.exists(main_path):
                self._open_file_path(main_path)
    
    def _new_file(self):
        """Erstellt eine neue leere Datei"""
        editor = CodeEditor()
        self.editor_tabs.addTab(editor, "Unbenannt")
        self.editor_tabs.setCurrentWidget(editor)
        self._connect_editor(editor)
    
    def _open_file(self):
        """Öffnet eine Datei via Dialog"""
        path, _ = QFileDialog.getOpenFileName(
            self, "Datei öffnen",
            filter="Python-Dateien (*.py *.pyw);;Alle Dateien (*.*)"
        )
        if path:
            self._open_file_path(path)
    
    def _open_file_path(self, path: str):
        """Öffnet eine Datei von einem Pfad"""
        # Bereits geöffnet?
        if path in self.open_files:
            editor = self.open_files[path]
            self.editor_tabs.setCurrentWidget(editor)
            return
        
        # Neue Datei öffnen
        editor = CodeEditor()
        if editor.load_file(path):
            self.open_files[path] = editor
            name = os.path.basename(path)
            index = self.editor_tabs.addTab(editor, name)
            self.editor_tabs.setCurrentIndex(index)
            self._connect_editor(editor)
        else:
            QMessageBox.warning(self, "Fehler", f"Datei konnte nicht geöffnet werden:\n{path}")
    
    def _connect_editor(self, editor: CodeEditor):
        """Verbindet Editor-Signale"""
        editor.file_modified.connect(self._on_file_modified)
        editor.cursor_position_changed.connect(self._on_cursor_changed)
    
    def _save_file(self):
        """Speichert die aktuelle Datei"""
        editor = self._get_current_editor()
        if not editor:
            return
        
        if editor.file_path:
            editor.save_file()
            self._update_tab_title(editor)
        else:
            self._save_file_as()
    
    def _save_file_as(self):
        """Speichert unter neuem Namen"""
        editor = self._get_current_editor()
        if not editor:
            return
        
        path, _ = QFileDialog.getSaveFileName(
            self, "Speichern unter",
            filter="Python-Dateien (*.py);;Alle Dateien (*.*)"
        )
        
        if path:
            editor.save_file(path)
            self.open_files[path] = editor
            self._update_tab_title(editor)
    
    def _close_tab(self, index: int):
        """Schließt einen Tab"""
        widget = self.editor_tabs.widget(index)
        
        if isinstance(widget, CodeEditor):
            if widget.is_modified():
                reply = QMessageBox.question(
                    self, "Ungespeicherte Änderungen",
                    "Die Datei wurde geändert. Speichern?",
                    QMessageBox.StandardButton.Save |
                    QMessageBox.StandardButton.Discard |
                    QMessageBox.StandardButton.Cancel
                )
                
                if reply == QMessageBox.StandardButton.Save:
                    self._save_file()
                elif reply == QMessageBox.StandardButton.Cancel:
                    return
            
            # Aus open_files entfernen
            if widget.file_path in self.open_files:
                del self.open_files[widget.file_path]
        
        self.editor_tabs.removeTab(index)
    
    def _get_current_editor(self) -> Optional[CodeEditor]:
        """Gibt den aktuellen Editor zurück"""
        widget = self.editor_tabs.currentWidget()
        if isinstance(widget, CodeEditor):
            return widget
        return None
    
    def _update_tab_title(self, editor: CodeEditor):
        """Aktualisiert den Tab-Titel"""
        index = self.editor_tabs.indexOf(editor)
        if index >= 0:
            name = os.path.basename(editor.file_path) if editor.file_path else "Unbenannt"
            if editor.is_modified():
                name = "● " + name
            self.editor_tabs.setTabText(index, name)
    
    # === Editor-Callbacks ===
    
    def _on_file_modified(self):
        """Wird aufgerufen wenn Datei geändert wurde"""
        editor = self.sender()
        if isinstance(editor, CodeEditor):
            self._update_tab_title(editor)
    
    def _on_cursor_changed(self, line: int, column: int):
        """Aktualisiert Cursor-Position in Statusleiste"""
        self.cursor_label.setText(f"Ln {line}, Col {column}")
    
    def _on_tab_changed(self, index: int):
        """Wird aufgerufen wenn Tab gewechselt wird"""
        editor = self._get_current_editor()
        if editor:
            # Kontext für AI-Panel aktualisieren
            selected = editor.textCursor().selectedText()
            if selected:
                self.ai_panel.set_context(selected, os.path.basename(editor.file_path or ""))
    
    # === Bearbeiten-Operationen ===
    
    def _undo(self):
        editor = self._get_current_editor()
        if editor:
            editor.undo()
    
    def _redo(self):
        editor = self._get_current_editor()
        if editor:
            editor.redo()
    
    def _cut(self):
        editor = self._get_current_editor()
        if editor:
            editor.cut()
    
    def _copy(self):
        editor = self._get_current_editor()
        if editor:
            editor.copy()
    
    def _paste(self):
        editor = self._get_current_editor()
        if editor:
            editor.paste()
    
    def _find(self):
        """TODO: Such-Dialog"""
        pass
    
    def _replace(self):
        """TODO: Ersetzen-Dialog"""
        pass
    
    # === Ansicht-Operationen ===
    
    def _toggle_explorer(self):
        """Schaltet Explorer-Panel um"""
        self.explorer_panel.setVisible(self.toggle_explorer_action.isChecked())
    
    def _toggle_output(self):
        """Schaltet Output-Panel um"""
        self.output_tabs.setVisible(self.toggle_output_action.isChecked())
    
    def _toggle_ai_panel(self):
        """Schaltet AI-Panel um"""
        visible = not self.ai_panel.isVisible()
        self.ai_panel.setVisible(visible)
        self.toggle_ai_action.setChecked(visible)
        self.ai_toolbar_btn.setChecked(visible)
    
    # === Ausführen ===
    
    def _run_current(self):
        """Führt aktuelle Datei aus"""
        editor = self._get_current_editor()
        if not editor or not editor.file_path:
            QMessageBox.warning(self, "Fehler", "Keine Datei zum Ausführen vorhanden.")
            return
        
        # Zuerst speichern
        if editor.is_modified():
            self._save_file()
        
        # Ausführen
        self.output_tabs.setCurrentWidget(self.output_panel)
        self.output_panel.run_python_file(editor.file_path)
    
    def _show_build_dialog(self):
        """Zeigt den Build-Dialog"""
        editor = self._get_current_editor()
        if not editor or not editor.file_path:
            QMessageBox.warning(self, "Fehler", "Keine Datei zum Kompilieren vorhanden.")
            return
        
        dialog = BuildDialog(
            editor.file_path,
            self.current_project.path if self.current_project else None,
            self
        )
        dialog.exec()
    
    # === Analyse ===
    
    def _analyze_current_file(self):
        """Analysiert die aktuelle Datei"""
        editor = self._get_current_editor()
        if not editor or not editor.file_path:
            return
        
        result = self.analyzer.analyze_file(editor.file_path)
        self._show_analysis_results(result)
    
    def _analyze_project(self):
        """Analysiert das gesamte Projekt"""
        if not self.current_project:
            QMessageBox.warning(self, "Fehler", "Kein Projekt geöffnet.")
            return
        
        results = self.analyzer.analyze_directory(self.current_project.path)
        
        # Alle Probleme sammeln
        all_problems = []
        for path, result in results.items():
            for err in result.errors:
                all_problems.append(Problem(
                    severity=ProblemSeverity.ERROR,
                    message=err['message'],
                    file_path=path,
                    line=err.get('line', 0)
                ))
            for warn in result.warnings:
                all_problems.append(Problem(
                    severity=ProblemSeverity.WARNING,
                    message=warn['message'],
                    file_path=path,
                    line=warn.get('line', 0)
                ))
        
        self.problems_panel.set_problems(all_problems)
        self.output_tabs.setCurrentWidget(self.problems_panel)
        
        self.statusbar.showMessage(
            f"Analyse abgeschlossen: {len(results)} Dateien, "
            f"{self.problems_panel.get_error_count()} Fehler, "
            f"{self.problems_panel.get_warning_count()} Warnungen",
            5000
        )
    
    def _show_analysis_results(self, result: AnalysisResult):
        """Zeigt Analyse-Ergebnisse"""
        problems = []
        
        for err in result.errors:
            problems.append(Problem(
                severity=ProblemSeverity.ERROR,
                message=err['message'],
                file_path=result.file_path,
                line=err.get('line', 0),
                source='analyzer'
            ))
        
        for warn in result.warnings:
            problems.append(Problem(
                severity=ProblemSeverity.WARNING,
                message=warn['message'],
                file_path=result.file_path,
                line=warn.get('line', 0),
                source='analyzer'
            ))
        
        self.problems_panel.clear_file(result.file_path)
        self.problems_panel.add_problems(problems)
        self.output_tabs.setCurrentWidget(self.problems_panel)
    
    def _goto_problem(self, file_path: str, line: int, column: int):
        """Springt zu einem Problem"""
        self._open_file_path(file_path)
        editor = self._get_current_editor()
        if editor:
            editor.go_to_line(line)
    
    # === AI ===
    
    def _on_code_generated(self, code: str):
        """Wird aufgerufen wenn AI Code generiert hat"""
        editor = self._get_current_editor()
        if editor:
            # Am Cursor einfügen
            cursor = editor.textCursor()
            cursor.insertText(code)
    
    # === Einstellungen & Hilfe ===
    
    def _show_settings(self):
        """Zeigt den Einstellungen-Dialog"""
        dialog = SettingsDialog(self.settings, self)
        if dialog.exec():
            # Settings wurden gespeichert, neu laden
            self._apply_settings()
    
    def _apply_settings(self):
        """Wendet geänderte Einstellungen an"""
        # API-Key aktualisieren
        self.ai_service.set_api_key(self.settings.get('ai.api_key', ''))
        
        # Editor-Einstellungen auf alle offenen Editoren anwenden
        # TODO: Implementieren
    
    def _show_about(self):
        """Zeigt den Über-Dialog"""
        QMessageBox.about(
            self,
            "Über DevCenter",
            """<h2>🚀 DevCenter</h2>
            <p><b>Version 1.0.0</b></p>
            <p>Python Development Suite</p>
            <p>Eine integrierte Entwicklungsumgebung für den<br>
            kompletten Python-Entwicklungszyklus.</p>
            <hr>
            <p>Fusionierte Tools:</p>
            <ul>
            <li>PythonBox - Code Editor</li>
            <li>MethodenAnalyser - Code Analysis</li>
            <li>UltimateKompilator - Build System</li>
            <li>Entwicklerschleife - AI Assistant</li>
            <li>ProFiler/ProSync - File Management</li>
            </ul>
            <hr>
            <p>© 2026 - Erstellt mit PyQt6</p>
            """
        )
    
    # === Events ===
    
    def _on_status_message(self, event):
        """Zeigt Status-Nachricht"""
        message = event.data.get('message', '')
        timeout = event.data.get('timeout', 3000)
        self.statusbar.showMessage(message, timeout)
    
    def closeEvent(self, event):
        """Wird beim Schließen aufgerufen"""
        # Ungespeicherte Dateien prüfen
        for path, editor in self.open_files.items():
            if editor.is_modified():
                reply = QMessageBox.question(
                    self, "Ungespeicherte Änderungen",
                    f"'{os.path.basename(path)}' wurde geändert. Speichern?",
                    QMessageBox.StandardButton.Save |
                    QMessageBox.StandardButton.Discard |
                    QMessageBox.StandardButton.Cancel
                )
                
                if reply == QMessageBox.StandardButton.Save:
                    editor.save_file()
                elif reply == QMessageBox.StandardButton.Cancel:
                    event.ignore()
                    return
        
        # Fenster-Status speichern
        self.settings.save_window_state(self.saveGeometry(), self.saveState())
        
        event.accept()


def main():
    """Haupteinstiegspunkt"""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
