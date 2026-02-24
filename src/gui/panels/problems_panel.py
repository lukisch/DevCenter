# -*- coding: utf-8 -*-
"""
DevCenter - Problems Panel
Anzeige von Fehlern, Warnungen und Hinweisen
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QPushButton, QLabel, QComboBox, QLineEdit
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QIcon
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum


class ProblemSeverity(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    HINT = "hint"


@dataclass
class Problem:
    """Ein Problem/Fehler/Warnung"""
    severity: ProblemSeverity
    message: str
    file_path: str
    line: int = 0
    column: int = 0
    source: str = ""  # z.B. "analyzer", "linter", "python"
    code: str = ""    # Fehlercode z.B. "E501"


class ProblemsPanel(QWidget):
    """
    Panel zur Anzeige von Code-Problemen
    
    Features:
    - Gruppierung nach Datei oder Schweregrad
    - Filter nach Schweregrad
    - Klick zum Navigieren
    - Live-Updates
    """
    
    problem_clicked = pyqtSignal(str, int, int)  # file, line, column
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._problems: List[Problem] = []
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Toolbar
        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(4, 4, 4, 4)
        
        # Filter
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Alle", "Fehler", "Warnungen", "Info"])
        self.filter_combo.currentIndexChanged.connect(self._apply_filter)
        toolbar.addWidget(QLabel("Filter:"))
        toolbar.addWidget(self.filter_combo)
        
        toolbar.addSpacing(10)
        
        # Suche
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Suchen...")
        self.search_input.textChanged.connect(self._apply_filter)
        self.search_input.setMaximumWidth(200)
        toolbar.addWidget(self.search_input)
        
        toolbar.addStretch()
        
        # Zähler
        self.error_count = QLabel("0 Fehler")
        self.error_count.setStyleSheet("color: #f44747;")
        toolbar.addWidget(self.error_count)
        
        self.warning_count = QLabel("0 Warnungen")
        self.warning_count.setStyleSheet("color: #cca700;")
        toolbar.addWidget(self.warning_count)
        
        toolbar.addSpacing(10)
        
        self.clear_button = QPushButton("Leeren")
        self.clear_button.clicked.connect(self.clear)
        toolbar.addWidget(self.clear_button)
        
        layout.addLayout(toolbar)
        
        # Tree
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Problem", "Datei", "Zeile"])
        self.tree.setColumnWidth(0, 400)
        self.tree.setColumnWidth(1, 200)
        self.tree.setColumnWidth(2, 50)
        self.tree.setRootIsDecorated(False)
        self.tree.setAlternatingRowColors(True)
        self.tree.itemDoubleClicked.connect(self._on_item_clicked)
        
        self.tree.setStyleSheet("""
            QTreeWidget {
                background-color: #1e1e1e;
                color: #cccccc;
                border: none;
                alternate-background-color: #252526;
            }
            QTreeWidget::item:selected {
                background-color: #094771;
            }
            QTreeWidget::item:hover {
                background-color: #2a2d2e;
            }
            QHeaderView::section {
                background-color: #252526;
                color: #cccccc;
                border: none;
                padding: 4px;
            }
        """)
        
        layout.addWidget(self.tree)
    
    def add_problem(self, problem: Problem):
        """Fügt ein Problem hinzu"""
        self._problems.append(problem)
        self._update_display()
    
    def add_problems(self, problems: List[Problem]):
        """Fügt mehrere Probleme hinzu"""
        self._problems.extend(problems)
        self._update_display()
    
    def set_problems(self, problems: List[Problem]):
        """Ersetzt alle Probleme"""
        self._problems = problems
        self._update_display()
    
    def clear(self):
        """Entfernt alle Probleme"""
        self._problems.clear()
        self._update_display()
    
    def clear_file(self, file_path: str):
        """Entfernt alle Probleme einer Datei"""
        self._problems = [p for p in self._problems if p.file_path != file_path]
        self._update_display()
    
    def _update_display(self):
        """Aktualisiert die Anzeige"""
        self.tree.clear()
        
        # Zähler
        errors = sum(1 for p in self._problems if p.severity == ProblemSeverity.ERROR)
        warnings = sum(1 for p in self._problems if p.severity == ProblemSeverity.WARNING)
        
        self.error_count.setText(f"{errors} Fehler")
        self.warning_count.setText(f"{warnings} Warnungen")
        
        # Gefilterte Liste
        filtered = self._get_filtered_problems()
        
        for problem in filtered:
            item = QTreeWidgetItem()
            
            # Icon basierend auf Schweregrad
            severity_icons = {
                ProblemSeverity.ERROR: "❌",
                ProblemSeverity.WARNING: "⚠️",
                ProblemSeverity.INFO: "ℹ️",
                ProblemSeverity.HINT: "💡"
            }
            icon = severity_icons.get(problem.severity, "")
            
            # Text
            message = f"{icon} {problem.message}"
            if problem.code:
                message += f" [{problem.code}]"
            
            item.setText(0, message)
            item.setText(1, problem.file_path.split('\\')[-1] if '\\' in problem.file_path else problem.file_path.split('/')[-1])
            item.setText(2, str(problem.line) if problem.line else "")
            
            # Farbe
            colors = {
                ProblemSeverity.ERROR: QColor("#f44747"),
                ProblemSeverity.WARNING: QColor("#cca700"),
                ProblemSeverity.INFO: QColor("#75beff"),
                ProblemSeverity.HINT: QColor("#89d185")
            }
            item.setForeground(0, colors.get(problem.severity, QColor("#cccccc")))
            
            # Daten speichern
            item.setData(0, Qt.ItemDataRole.UserRole, problem)
            
            self.tree.addTopLevelItem(item)
    
    def _get_filtered_problems(self) -> List[Problem]:
        """Gibt gefilterte Probleme zurück"""
        problems = self._problems
        
        # Schweregrad-Filter
        filter_idx = self.filter_combo.currentIndex()
        if filter_idx == 1:  # Fehler
            problems = [p for p in problems if p.severity == ProblemSeverity.ERROR]
        elif filter_idx == 2:  # Warnungen
            problems = [p for p in problems if p.severity == ProblemSeverity.WARNING]
        elif filter_idx == 3:  # Info
            problems = [p for p in problems if p.severity in (ProblemSeverity.INFO, ProblemSeverity.HINT)]
        
        # Text-Filter
        search = self.search_input.text().lower()
        if search:
            problems = [p for p in problems if search in p.message.lower() or search in p.file_path.lower()]
        
        return problems
    
    def _apply_filter(self):
        """Wendet Filter an"""
        self._update_display()
    
    def _on_item_clicked(self, item: QTreeWidgetItem, column: int):
        """Behandelt Doppelklick auf Problem"""
        problem = item.data(0, Qt.ItemDataRole.UserRole)
        if problem:
            self.problem_clicked.emit(problem.file_path, problem.line, problem.column)
    
    def get_error_count(self) -> int:
        """Gibt Anzahl der Fehler zurück"""
        return sum(1 for p in self._problems if p.severity == ProblemSeverity.ERROR)
    
    def get_warning_count(self) -> int:
        """Gibt Anzahl der Warnungen zurück"""
        return sum(1 for p in self._problems if p.severity == ProblemSeverity.WARNING)
