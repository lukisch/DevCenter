# -*- coding: utf-8 -*-
"""
DevCenter - Code Editor
Syntax-highlighted Python Editor basierend auf PythonBox
"""

import sys
import re
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QPlainTextEdit, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QFrame, QMenu, QApplication
)
from PyQt6.QtCore import Qt, QRect, QSize, pyqtSignal, QRegularExpression
from PyQt6.QtGui import (
    QColor, QPainter, QTextFormat, QFont, QFontMetrics,
    QSyntaxHighlighter, QTextCharFormat, QTextCursor, QPalette,
    QKeySequence, QShortcut, QAction
)


class PythonHighlighter(QSyntaxHighlighter):
    """Syntax Highlighter für Python"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.highlighting_rules = []
        
        # Keywords
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#569cd6"))
        keyword_format.setFontWeight(QFont.Weight.Bold)
        
        keywords = [
            'and', 'as', 'assert', 'async', 'await', 'break', 'class',
            'continue', 'def', 'del', 'elif', 'else', 'except', 'finally',
            'for', 'from', 'global', 'if', 'import', 'in', 'is', 'lambda',
            'None', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return',
            'True', 'False', 'try', 'while', 'with', 'yield'
        ]
        
        for word in keywords:
            pattern = QRegularExpression(f"\\b{word}\\b")
            self.highlighting_rules.append((pattern, keyword_format))
        
        # Builtins
        builtin_format = QTextCharFormat()
        builtin_format.setForeground(QColor("#dcdcaa"))
        
        builtins = [
            'abs', 'all', 'any', 'bin', 'bool', 'bytes', 'callable', 'chr',
            'classmethod', 'compile', 'complex', 'dict', 'dir', 'divmod',
            'enumerate', 'eval', 'exec', 'filter', 'float', 'format',
            'frozenset', 'getattr', 'globals', 'hasattr', 'hash', 'help',
            'hex', 'id', 'input', 'int', 'isinstance', 'issubclass', 'iter',
            'len', 'list', 'locals', 'map', 'max', 'memoryview', 'min',
            'next', 'object', 'oct', 'open', 'ord', 'pow', 'print', 'property',
            'range', 'repr', 'reversed', 'round', 'set', 'setattr', 'slice',
            'sorted', 'staticmethod', 'str', 'sum', 'super', 'tuple', 'type',
            'vars', 'zip', '__import__'
        ]
        
        for word in builtins:
            pattern = QRegularExpression(f"\\b{word}\\b")
            self.highlighting_rules.append((pattern, builtin_format))
        
        # Class names (nach 'class')
        class_format = QTextCharFormat()
        class_format.setForeground(QColor("#4ec9b0"))
        class_format.setFontWeight(QFont.Weight.Bold)
        self.highlighting_rules.append(
            (QRegularExpression(r"\bclass\s+(\w+)"), class_format)
        )
        
        # Function definitions
        func_format = QTextCharFormat()
        func_format.setForeground(QColor("#dcdcaa"))
        self.highlighting_rules.append(
            (QRegularExpression(r"\bdef\s+(\w+)"), func_format)
        )
        
        # Self/cls
        self_format = QTextCharFormat()
        self_format.setForeground(QColor("#9cdcfe"))
        self_format.setFontItalic(True)
        self.highlighting_rules.append(
            (QRegularExpression(r"\b(self|cls)\b"), self_format)
        )
        
        # Numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#b5cea8"))
        self.highlighting_rules.append(
            (QRegularExpression(r"\b[0-9]+\.?[0-9]*([eE][+-]?[0-9]+)?\b"), number_format)
        )
        
        # Strings (single and double quotes)
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#ce9178"))
        self.highlighting_rules.append(
            (QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"'), string_format)
        )
        self.highlighting_rules.append(
            (QRegularExpression(r"'[^'\\]*(\\.[^'\\]*)*'"), string_format)
        )
        
        # Decorators
        decorator_format = QTextCharFormat()
        decorator_format.setForeground(QColor("#dcdcaa"))
        self.highlighting_rules.append(
            (QRegularExpression(r"@\w+"), decorator_format)
        )
        
        # Comments
        self.comment_format = QTextCharFormat()
        self.comment_format.setForeground(QColor("#6a9955"))
        self.highlighting_rules.append(
            (QRegularExpression(r"#[^\n]*"), self.comment_format)
        )
        
        # Multi-line strings
        self.multiline_string_format = QTextCharFormat()
        self.multiline_string_format.setForeground(QColor("#ce9178"))
    
    def highlightBlock(self, text):
        """Highlightet einen Textblock"""
        # Einfache Regeln
        for pattern, format in self.highlighting_rules:
            iterator = pattern.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)
        
        # Multi-line Strings (docstrings)
        self._highlight_multiline(text, '"""', 1, self.multiline_string_format)
        self._highlight_multiline(text, "'''", 2, self.multiline_string_format)
    
    def _highlight_multiline(self, text, delimiter, state, format):
        """Highlightet Multi-line Strings"""
        if self.previousBlockState() == state:
            start_index = 0
            add = 0
        else:
            start_index = text.find(delimiter)
            add = len(delimiter)
        
        while start_index >= 0:
            end_index = text.find(delimiter, start_index + add)
            
            if end_index == -1:
                self.setCurrentBlockState(state)
                comment_length = len(text) - start_index
            else:
                comment_length = end_index - start_index + len(delimiter)
            
            self.setFormat(start_index, comment_length, format)
            start_index = text.find(delimiter, start_index + comment_length)


class LineNumberArea(QWidget):
    """Widget für Zeilennummern"""
    
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor
    
    def sizeHint(self):
        """Gibt die empfohlene Groesse basierend auf Zeilennummernbreite zurueck."""
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        """Delegiert das Zeichnen an den Editor."""
        self.editor.line_number_area_paint_event(event)


class CodeEditor(QPlainTextEdit):
    """
    Fortgeschrittener Code-Editor mit:
    - Syntax Highlighting
    - Zeilennummern
    - Aktuelle Zeile hervorheben
    - Auto-Indent
    - Tab-Vervollständigung
    """
    
    # Signals
    file_modified = pyqtSignal(bool)
    cursor_position_changed = pyqtSignal(int, int)  # line, column
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.file_path: Optional[str] = None
        self._is_modified = False
        
        # Font
        font = QFont("Consolas", 11)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)
        
        # Tab-Einstellungen
        self.tab_size = 4
        tab_width = QFontMetrics(font).horizontalAdvance(' ') * self.tab_size
        self.setTabStopDistance(tab_width)
        
        # Appearance
        self._setup_appearance()
        
        # Syntax Highlighting
        self.highlighter = PythonHighlighter(self.document())
        
        # Line Number Area
        self.line_number_area = LineNumberArea(self)
        
        # Connections
        self.blockCountChanged.connect(self._update_line_number_area_width)
        self.updateRequest.connect(self._update_line_number_area)
        self.cursorPositionChanged.connect(self._highlight_current_line)
        self.cursorPositionChanged.connect(self._emit_cursor_position)
        self.textChanged.connect(self._on_text_changed)
        
        # Initial Setup
        self._update_line_number_area_width(0)
        self._highlight_current_line()
        
        # Context Menu
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
    
    def _setup_appearance(self):
        """Richtet das Erscheinungsbild ein"""
        # Farben
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Base, QColor("#1e1e1e"))
        palette.setColor(QPalette.ColorRole.Text, QColor("#d4d4d4"))
        self.setPalette(palette)
        
        # Style
        self.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                selection-background-color: #264f78;
                selection-color: #ffffff;
                border: none;
            }
        """)
        
        # Word Wrap aus
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
    
    def line_number_area_width(self) -> int:
        """Berechnet die Breite des Zeilennummern-Bereichs"""
        digits = 1
        max_num = max(1, self.blockCount())
        while max_num >= 10:
            max_num //= 10
            digits += 1
        
        space = 10 + self.fontMetrics().horizontalAdvance('9') * digits
        return space
    
    def _update_line_number_area_width(self, new_block_count):
        """Aktualisiert die Breite des Zeilennummern-Bereichs"""
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)
    
    def _update_line_number_area(self, rect, dy):
        """Aktualisiert den Zeilennummern-Bereich beim Scrollen"""
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), 
                                         self.line_number_area.width(), rect.height())
        
        if rect.contains(self.viewport().rect()):
            self._update_line_number_area_width(0)
    
    def resizeEvent(self, event):
        """Fenstergrößenänderung"""
        super().resizeEvent(event)
        
        cr = self.contentsRect()
        self.line_number_area.setGeometry(
            QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height())
        )
    
    def line_number_area_paint_event(self, event):
        """Zeichnet die Zeilennummern"""
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor("#1e1e1e"))
        
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())
        
        current_line = self.textCursor().blockNumber()
        
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                
                # Aktuelle Zeile hervorheben
                if block_number == current_line:
                    painter.setPen(QColor("#c6c6c6"))
                else:
                    painter.setPen(QColor("#858585"))
                
                painter.drawText(0, top, self.line_number_area.width() - 5,
                               self.fontMetrics().height(),
                               Qt.AlignmentFlag.AlignRight, number)
            
            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1
    
    def _highlight_current_line(self):
        """Hebt die aktuelle Zeile hervor"""
        extra_selections = []
        
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            line_color = QColor("#282828")
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)
        
        self.setExtraSelections(extra_selections)
    
    def _emit_cursor_position(self):
        """Sendet die aktuelle Cursor-Position"""
        cursor = self.textCursor()
        line = cursor.blockNumber() + 1
        column = cursor.columnNumber() + 1
        self.cursor_position_changed.emit(line, column)
    
    def _on_text_changed(self):
        """Text wurde geändert"""
        if not self._is_modified:
            self._is_modified = True
            self.file_modified.emit(True)
    
    def keyPressEvent(self, event):
        """Tastatureingabe"""
        # Tab -> Spaces
        if event.key() == Qt.Key.Key_Tab:
            if event.modifiers() == Qt.KeyboardModifier.NoModifier:
                cursor = self.textCursor()
                if cursor.hasSelection():
                    # Einrücken
                    self._indent_selection(cursor)
                else:
                    # Spaces einfügen
                    cursor.insertText(" " * self.tab_size)
                return
        
        # Shift+Tab -> Unindent
        if event.key() == Qt.Key.Key_Backtab:
            cursor = self.textCursor()
            self._unindent_selection(cursor)
            return
        
        # Enter -> Auto-Indent
        if event.key() == Qt.Key.Key_Return:
            cursor = self.textCursor()
            line = cursor.block().text()
            
            # Aktuelle Einrückung ermitteln
            indent = ""
            for char in line:
                if char in ' \t':
                    indent += char
                else:
                    break
            
            # Extra Einrückung nach : (if, for, def, class, etc.)
            stripped = line.rstrip()
            if stripped.endswith(':'):
                indent += " " * self.tab_size
            
            # Standard Enter + Auto-Indent
            super().keyPressEvent(event)
            self.textCursor().insertText(indent)
            return
        
        # Backspace am Zeilenanfang -> Unindent
        if event.key() == Qt.Key.Key_Backspace:
            cursor = self.textCursor()
            if cursor.columnNumber() > 0 and not cursor.hasSelection():
                line = cursor.block().text()
                col = cursor.columnNumber()
                
                # Prüfen ob nur Whitespace vor Cursor
                if line[:col].strip() == "":
                    # Bis zum vorherigen Tab-Stop löschen
                    spaces_to_delete = col % self.tab_size or self.tab_size
                    for _ in range(spaces_to_delete):
                        cursor.deletePreviousChar()
                    return
        
        super().keyPressEvent(event)
    
    def _indent_selection(self, cursor):
        """Rückt die Auswahl ein"""
        start = cursor.selectionStart()
        end = cursor.selectionEnd()
        
        cursor.setPosition(start)
        start_block = cursor.blockNumber()
        
        cursor.setPosition(end)
        end_block = cursor.blockNumber()
        
        cursor.setPosition(start)
        cursor.beginEditBlock()
        
        for _ in range(end_block - start_block + 1):
            cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
            cursor.insertText(" " * self.tab_size)
            cursor.movePosition(QTextCursor.MoveOperation.NextBlock)
        
        cursor.endEditBlock()
    
    def _unindent_selection(self, cursor):
        """Rückt die Auswahl aus"""
        start = cursor.selectionStart()
        end = cursor.selectionEnd()
        
        cursor.setPosition(start)
        start_block = cursor.blockNumber()
        
        cursor.setPosition(end)
        end_block = cursor.blockNumber()
        
        cursor.setPosition(start)
        cursor.beginEditBlock()
        
        for _ in range(end_block - start_block + 1):
            cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
            line = cursor.block().text()
            
            # Entferne führende Spaces
            spaces_to_remove = 0
            for i, char in enumerate(line):
                if char == ' ' and spaces_to_remove < self.tab_size:
                    spaces_to_remove += 1
                elif char == '\t' and spaces_to_remove == 0:
                    spaces_to_remove = 1
                    break
                else:
                    break
            
            for _ in range(spaces_to_remove):
                cursor.deleteChar()
            
            cursor.movePosition(QTextCursor.MoveOperation.NextBlock)
        
        cursor.endEditBlock()
    
    def _show_context_menu(self, position):
        """Zeigt das Kontextmenü"""
        menu = self.createStandardContextMenu()
        menu.addSeparator()
        
        # Zusätzliche Aktionen
        comment_action = QAction("Kommentieren/Entkommentieren", self)
        comment_action.setShortcut(QKeySequence("Ctrl+/"))
        comment_action.triggered.connect(self.toggle_comment)
        menu.addAction(comment_action)
        
        menu.exec(self.mapToGlobal(position))
    
    def toggle_comment(self):
        """Kommentiert/Entkommentiert die ausgewählten Zeilen"""
        cursor = self.textCursor()
        start = cursor.selectionStart()
        end = cursor.selectionEnd()
        
        cursor.setPosition(start)
        start_block = cursor.blockNumber()
        
        cursor.setPosition(end)
        end_block = cursor.blockNumber()
        
        cursor.setPosition(start)
        cursor.beginEditBlock()
        
        # Prüfen ob alle Zeilen kommentiert sind
        all_commented = True
        check_cursor = QTextCursor(cursor)
        for _ in range(end_block - start_block + 1):
            line = check_cursor.block().text().lstrip()
            if not line.startswith('#'):
                all_commented = False
                break
            check_cursor.movePosition(QTextCursor.MoveOperation.NextBlock)
        
        # Kommentieren oder Entkommentieren
        for _ in range(end_block - start_block + 1):
            cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
            line = cursor.block().text()
            
            if all_commented:
                # Entkommentieren
                pos = 0
                for i, char in enumerate(line):
                    if char == '#':
                        pos = i
                        break
                cursor.movePosition(QTextCursor.MoveOperation.Right, n=pos)
                cursor.deleteChar()
                if cursor.block().text()[pos:pos+1] == ' ':
                    cursor.deleteChar()
            else:
                # Kommentieren
                cursor.insertText("# ")
            
            cursor.movePosition(QTextCursor.MoveOperation.NextBlock)
        
        cursor.endEditBlock()
    
    def load_file(self, file_path: str) -> bool:
        """
        Lädt eine Datei in den Editor
        
        Args:
            file_path: Pfad zur Datei
            
        Returns:
            True bei Erfolg
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.setPlainText(content)
            self.file_path = file_path
            self._is_modified = False
            self.file_modified.emit(False)
            return True
            
        except Exception as e:
            print(f"Fehler beim Laden: {e}")
            return False
    
    def save_file(self, file_path: str = None) -> bool:
        """
        Speichert den Editor-Inhalt
        
        Args:
            file_path: Optional - neuer Speicherpfad
            
        Returns:
            True bei Erfolg
        """
        path = file_path or self.file_path
        
        if not path:
            return False
        
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(self.toPlainText())
            
            self.file_path = path
            self._is_modified = False
            self.file_modified.emit(False)
            return True
            
        except Exception as e:
            print(f"Fehler beim Speichern: {e}")
            return False
    
    def get_text(self) -> str:
        """Gibt den Text zurück"""
        return self.toPlainText()
    
    def is_modified(self) -> bool:
        """Prüft ob der Text geändert wurde"""
        return self._is_modified
    
    def go_to_line(self, line: int):
        """Springt zu einer bestimmten Zeile"""
        block = self.document().findBlockByLineNumber(line - 1)
        if block.isValid():
            cursor = self.textCursor()
            cursor.setPosition(block.position())
            self.setTextCursor(cursor)
            self.centerCursor()


if __name__ == "__main__":
    # Test
    app = QApplication(sys.argv)
    
    editor = CodeEditor()
    editor.setPlainText('''# -*- coding: utf-8 -*-
"""Test-Modul für den Code Editor"""

import os
from pathlib import Path

class TestClass:
    """Eine Test-Klasse"""
    
    def __init__(self, name: str):
        self.name = name
        self.value = 42
    
    def greet(self):
        """Begrüßung ausgeben"""
        print(f"Hello, {self.name}!")
        return True

def main():
    obj = TestClass("World")
    obj.greet()
    
    # Ein Kommentar
    numbers = [1, 2, 3, 4, 5]
    total = sum(numbers)
    print(f"Sum: {total}")

if __name__ == "__main__":
    main()
''')
    
    editor.resize(800, 600)
    editor.show()
    
    sys.exit(app.exec())
