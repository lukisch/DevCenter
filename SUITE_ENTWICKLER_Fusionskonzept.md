# 🛠️ SUITE ENTWICKLER - Fusionskonzept

## Übersicht

**Ziel:** Bündelung aller Entwickler-Tools in eine integrierte Entwicklungsumgebung für Python-Projekte.

---

## 📦 Enthaltene Tools

| Tool | Funktion | Reifegrad | Zeilen |
|------|----------|-----------|--------|
| **ProFiler V14** | Datei-Management, PDF-Tools, OCR, Sync | 85% | 7575 |
| **PythonBox V8** | Python IDE mit Debugger, Git | 85% | 3381 |
| **ProSync V3.1** | Datei-Sync mit DB-Schutz | 85% | 1764 |
| **Entwicklerschleife V3** | AI-gestützte Code-Generierung | 75% | 1010 |
| **MethodenAnalyser V3** | Statische Code-Analyse | 85% | 1066 |
| **EncodingFixer** | Encoding-Reparatur (ftfy) | 70% | 57 |
| **UltimateKompilator V3.1** | Python→EXE mit Auto-Icons | 85% | 443 |
| **WinStorePackager V2.3** | Windows Store Vorbereitung | 80% | 1376 |
| **IcoBuilder** | Bild→ICO Konverter | 80% | 419 |
| **pyCuttertxt** | Code-Klassen-Extraktor | 75% | 91 |
| **ThirdPartyLicenses** | Lizenz-Generator | 100% | 27 |

---

## 🎯 Fusionskonzept: "DevCenter"

### Vision
Eine **All-in-One Desktop-IDE** für den kompletten Python-Entwicklungszyklus:
Code schreiben → Analysieren → Testen → Kompilieren → Veröffentlichen

### Kernmodule

```
┌─────────────────────────────────────────────────────────────────┐
│                        DevCenter                                │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │   EDITOR    │  │  ANALYZER   │  │       BUILDER           │ │
│  │ (PythonBox) │  │ (Methoden-  │  │ (Kompilator + Packager) │ │
│  │             │  │  Analyser)  │  │                         │ │
│  │ • Syntax HL │  │ • AST-Parse │  │ • PyInstaller           │ │
│  │ • Debugger  │  │ • Imports   │  │ • Icon-Konvertierung    │ │
│  │ • Git       │  │ • Duplikate │  │ • Lizenz-Sammlung       │ │
│  │ • Minimap   │  │ • Encoding  │  │ • MSIX-Manifest         │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    AI ASSISTANT                              ││
│  │              (Entwicklerschleife Advanced)                   ││
│  │                                                              ││
│  │  • Planner (Architektur)  • Coder (Code-Gen)                ││
│  │  • Checker (Validierung)  • Build-Integration               ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  ┌─────────────────────┐  ┌─────────────────────────────────┐  │
│  │   FILE MANAGER      │  │        UTILITIES               │  │
│  │ (ProFiler + ProSync)│  │                                 │  │
│  │                     │  │ • EncodingFixer                 │  │
│  │ • Projektordner     │  │ • IcoBuilder                    │  │
│  │ • DB-Sync           │  │ • pyCuttertxt (Code-Split)      │  │
│  │ • Versionierung     │  │ • ThirdPartyLicenses            │  │
│  └─────────────────────┘  └─────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🏗️ Architektur

### Layer-Struktur

```
DevCenter/
├── core/
│   ├── project_manager.py      # Projekt-Verwaltung
│   ├── settings_manager.py     # Zentrale Einstellungen
│   └── plugin_loader.py        # Plugin-System
│
├── modules/
│   ├── editor/                 # PythonBox-Integration
│   │   ├── code_editor.py
│   │   ├── debugger.py
│   │   └── git_integration.py
│   │
│   ├── analyzer/               # Analyse-Tools
│   │   ├── method_analyzer.py
│   │   ├── import_checker.py
│   │   └── encoding_fixer.py
│   │
│   ├── builder/                # Build-Pipeline
│   │   ├── kompilator.py
│   │   ├── icon_builder.py
│   │   ├── license_generator.py
│   │   └── store_packager.py
│   │
│   ├── ai_assistant/           # AI-Features
│   │   ├── planner.py
│   │   ├── coder.py
│   │   └── checker.py
│   │
│   └── file_manager/           # Datei-Verwaltung
│       ├── profiler_bridge.py
│       └── sync_manager.py
│
├── gui/
│   ├── main_window.py
│   ├── panels/
│   └── dialogs/
│
└── resources/
    ├── themes/
    └── icons/
```

---

## 🔄 Workflow-Integration

### Entwicklungszyklus

```
1. PROJEKT ERSTELLEN
   └── FileManager: Ordnerstruktur + Git Init

2. CODE SCHREIBEN
   └── Editor: PythonBox mit Auto-Complete

3. AI-UNTERSTÜTZUNG (optional)
   └── AI Assistant: Planen → Generieren → Prüfen

4. ANALYSIEREN
   └── Analyzer: Methoden, Imports, Encoding prüfen

5. TESTEN
   └── Editor: Debugger + Output Panel

6. BUILD
   └── Builder: Kompilieren + Icons + Lizenzen

7. VERÖFFENTLICHEN
   └── Store Packager: MSIX für Windows Store

8. SYNC
   └── FileManager: Backup + DB-sichere Synchronisation
```

---

## 📊 Feature-Matrix nach Fusion

| Feature | Vor Fusion | Nach Fusion |
|---------|------------|-------------|
| IDE-Funktionen | Verteilt auf 3 Tools | Integriert |
| Code-Analyse | Separates Tool | In IDE eingebettet |
| Build-Prozess | 3 manuelle Schritte | One-Click-Build |
| AI-Unterstützung | Standalone | Context-aware |
| Projekt-Sync | Manuell | Automatisch |

---

## ⚡ Synergien

1. **Editor + Analyzer:** Echtzeit-Fehleranzeige während des Tippens
2. **Editor + AI:** Code-Generierung direkt im Editor
3. **Analyzer + Builder:** Automatische Prüfung vor Build
4. **FileManager + Sync:** Nahtlose Backup-Integration
5. **IcoBuilder + Kompilator:** Icon-Pipeline automatisiert

---

## 🚀 Implementierungs-Roadmap

### Phase 1: Core (4 Wochen)
- [ ] Projekt-Skelett mit Plugin-System
- [ ] PythonBox als Editor-Modul integrieren
- [ ] Zentrale Settings-Verwaltung

### Phase 2: Analyse (2 Wochen)
- [ ] MethodenAnalyser einbinden
- [ ] EncodingFixer als Auto-Check
- [ ] Live-Analyse im Editor

### Phase 3: Build (3 Wochen)
- [ ] Kompilator-Integration
- [ ] IcoBuilder einbinden
- [ ] Lizenz-Generator automatisieren
- [ ] Store-Packager als Wizard

### Phase 4: AI (2 Wochen)
- [ ] Entwicklerschleife einbinden
- [ ] Editor-Context an AI übergeben
- [ ] Build-Integration

### Phase 5: FileManager (2 Wochen)
- [ ] ProFiler-Bridge für Projekt-DB
- [ ] ProSync für automatisches Backup
- [ ] Git-Status-Sync

---

## ✅ Fazit

**Empfehlung: FUSION EMPFOHLEN** ⭐⭐⭐⭐⭐

Die Tools ergänzen sich hervorragend und decken den kompletten Entwicklungszyklus ab. Eine Fusion würde:

- **Workflow verbessern:** Keine Tool-Wechsel mehr
- **Synergien nutzen:** Daten fließen zwischen Modulen
- **Wartung vereinfachen:** Ein Codebase statt 11
- **UX verbessern:** Einheitliche Oberfläche

**Geschätzter Aufwand:** 13 Wochen für MVP
**Empfohlenes Framework:** PyQt6 (bereits in PythonBox/ProSync verwendet)

---
*Analyse erstellt: 03.01.2026*


---

# 📋 DETAILLIERTER UMSETZUNGSPLAN

## 🎯 Projektziele & Scope

### MVP-Definition (Minimum Viable Product)
Das MVP umfasst:
- ✅ Funktionierender Code-Editor mit Syntax-Highlighting
- ✅ Integrierte Code-Analyse (Imports, Methoden)
- ✅ One-Click Build zu EXE
- ✅ Projekt-Management (Erstellen, Öffnen, Recent)
- ❌ AI-Features (Phase 2)
- ❌ Store-Packager (Phase 2)

### Nicht-Ziele für MVP
- Kein Multi-Language Support (nur Python)
- Keine Git-Integration (später)
- Keine Cloud-Sync

---

## 📅 PHASE 1: Projektfundament (Wochen 1-4)

### Woche 1: Projekt-Setup & Architektur

#### Tag 1-2: Repository & Struktur
```
DevCenter/
├── src/
│   ├── __init__.py
│   ├── main.py                 # Entry Point
│   ├── app.py                  # QApplication Setup
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── project_manager.py  # Projekt-CRUD
│   │   ├── settings_manager.py # QSettings Wrapper
│   │   ├── event_bus.py        # Signal-basierte Kommunikation
│   │   └── plugin_loader.py    # Plugin-System (für später)
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── project.py          # Project Dataclass
│   │   └── settings.py         # Settings Dataclass
│   │
│   ├── gui/
│   │   ├── __init__.py
│   │   ├── main_window.py
│   │   ├── widgets/
│   │   └── dialogs/
│   │
│   └── modules/                # Später befüllt
│       ├── editor/
│       ├── analyzer/
│       └── builder/
│
├── resources/
│   ├── icons/
│   ├── themes/
│   └── templates/
│
├── tests/
├── docs/
├── requirements.txt
├── setup.py
└── README.md
```

**Tasks:**
- [ ] Git Repository initialisieren
- [ ] Ordnerstruktur anlegen
- [ ] requirements.txt erstellen
- [ ] Basic README.md

**Deliverable:** Leeres aber strukturiertes Projekt

#### Tag 3-4: Core Framework
```python
# src/core/event_bus.py
from PyQt6.QtCore import QObject, pyqtSignal

class EventBus(QObject):
    """Zentrale Signal-Verteilung zwischen Modulen"""
    
    # Editor Events
    file_opened = pyqtSignal(str)           # path
    file_saved = pyqtSignal(str)            # path
    file_modified = pyqtSignal(str, bool)   # path, is_modified
    
    # Analyzer Events
    analysis_requested = pyqtSignal(str)    # path
    analysis_complete = pyqtSignal(dict)    # results
    errors_found = pyqtSignal(list)         # error_list
    
    # Builder Events
    build_requested = pyqtSignal(str)       # project_path
    build_progress = pyqtSignal(int, str)   # percent, message
    build_complete = pyqtSignal(bool, str)  # success, output_path
    
    # Project Events
    project_opened = pyqtSignal(str)        # project_path
    project_closed = pyqtSignal()
    
    _instance = None
    
    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
```

**Tasks:**
- [ ] EventBus implementieren
- [ ] SettingsManager implementieren (QSettings Wrapper)
- [ ] ProjectManager Grundgerüst

**Deliverable:** Funktionierendes Core-Framework

#### Tag 5: Hauptfenster Grundgerüst
```python
# src/gui/main_window.py
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DevCenter")
        self.setMinimumSize(1200, 800)
        
        self._setup_ui()
        self._setup_menu()
        self._setup_toolbar()
        self._setup_statusbar()
        self._connect_signals()
        self._restore_geometry()
    
    def _setup_ui(self):
        # Tab-Widget als zentrales Element
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        self.setCentralWidget(self.tab_widget)
        
        # Dock Widgets für Panels
        self._setup_project_dock()
        self._setup_output_dock()
```

**Tasks:**
- [ ] MainWindow Grundstruktur
- [ ] Menüleiste (File, Edit, View, Project, Build, Help)
- [ ] Toolbar (New, Open, Save, Run, Build)
- [ ] StatusBar
- [ ] Window State Speicherung

**Deliverable:** Lauffähiges Hauptfenster (leer)

### Woche 2: Projekt-Management

#### Tag 1-2: Project Model & Manager
```python
# src/models/project.py
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import json

@dataclass
class DevCenterProject:
    name: str
    path: Path
    main_file: Optional[str] = None
    python_version: str = "3.11"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_opened: Optional[str] = None
    
    # Build Settings
    build_output_dir: str = "dist"
    build_icon: Optional[str] = None
    build_onefile: bool = True
    build_console: bool = True
    
    # Analyzer Settings
    auto_analyze: bool = True
    analyze_on_save: bool = True
    
    def save(self):
        config_path = self.path / ".devcenter" / "project.json"
        config_path.parent.mkdir(exist_ok=True)
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(self.__dict__, f, indent=2, default=str)
    
    @classmethod
    def load(cls, path: Path) -> 'DevCenterProject':
        config_path = path / ".devcenter" / "project.json"
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls(**data)
```

**Tasks:**
- [ ] Project Dataclass
- [ ] ProjectManager.create_project()
- [ ] ProjectManager.open_project()
- [ ] ProjectManager.get_recent_projects()
- [ ] Project-Wizard Dialog

**Deliverable:** Projekte erstellen und öffnen funktioniert

#### Tag 3-4: Project Explorer Panel
```python
# src/gui/widgets/project_explorer.py
class ProjectExplorer(QDockWidget):
    file_double_clicked = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__("Project Explorer", parent)
        self.tree = QTreeView()
        self.model = QFileSystemModel()
        # ... Setup
```

**Tasks:**
- [ ] ProjectExplorer Widget
- [ ] Dateibaum mit Icons
- [ ] Kontextmenü (New File, Delete, Rename)
- [ ] Drag & Drop Support
- [ ] Filter für Python-Dateien

**Deliverable:** Navigierbarer Projektbaum

#### Tag 5: Recent Projects & Welcome Screen
```python
# src/gui/dialogs/welcome_dialog.py
class WelcomeDialog(QDialog):
    """Startbildschirm mit Recent Projects"""
    
    project_selected = pyqtSignal(str)
    new_project_requested = pyqtSignal()
```

**Tasks:**
- [ ] WelcomeDialog mit Recent Projects Liste
- [ ] "Kein Projekt offen" Placeholder
- [ ] Drag & Drop von .py Dateien auf Fenster

**Deliverable:** Benutzerfreundlicher Projektstart

### Woche 3: Editor-Integration (PythonBox)

#### Tag 1-2: Editor Widget Grundlage
```python
# src/modules/editor/code_editor.py
from PyQt6.Qsci import QsciScintilla, QsciLexerPython

class CodeEditor(QsciScintilla):
    """Python Code Editor basierend auf PythonBox"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_editor()
        self._setup_lexer()
        self._setup_margins()
        self._setup_autocompletion()
    
    def _setup_editor(self):
        # Font
        font = QFont("Consolas", 11)
        self.setFont(font)
        
        # Tabs
        self.setTabWidth(4)
        self.setIndentationsUseTabs(False)
        self.setAutoIndent(True)
        
        # Brace Matching
        self.setBraceMatching(QsciScintilla.BraceMatch.SloppyBraceMatch)
        
        # Current Line Highlight
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QColor("#ffffc0"))
    
    def _setup_margins(self):
        # Zeilennummern
        self.setMarginType(0, QsciScintilla.MarginType.NumberMargin)
        self.setMarginWidth(0, "00000")
        
        # Folding
        self.setFolding(QsciScintilla.FoldStyle.BoxedTreeFoldStyle)
```

**Tasks:**
- [ ] CodeEditor Widget (QScintilla-basiert)
- [ ] Python Lexer mit Farben
- [ ] Zeilennummern
- [ ] Code Folding
- [ ] Brace Matching
- [ ] Current Line Highlight

**Deliverable:** Funktionierender Syntax-Highlighted Editor

#### Tag 3: Editor Features
**Tasks:**
- [ ] Suchen & Ersetzen Dialog
- [ ] Gehe zu Zeile
- [ ] Minimap (optional)
- [ ] Undo/Redo
- [ ] Einrückung (Tab, Shift+Tab)

**Deliverable:** Vollwertiger Editor

#### Tag 4-5: Tab-Management & File Handling
```python
# src/modules/editor/editor_manager.py
class EditorManager:
    """Verwaltet alle offenen Editor-Tabs"""
    
    def open_file(self, path: str) -> CodeEditor:
        # Prüfen ob bereits offen
        if path in self.open_files:
            self.tab_widget.setCurrentWidget(self.open_files[path])
            return self.open_files[path]
        
        # Neue Tab erstellen
        editor = CodeEditor()
        editor.load_file(path)
        
        tab_index = self.tab_widget.addTab(editor, Path(path).name)
        self.open_files[path] = editor
        
        # Modified-Indikator
        editor.modificationChanged.connect(
            lambda modified: self._update_tab_title(path, modified)
        )
        
        return editor
```

**Tasks:**
- [ ] EditorManager Klasse
- [ ] Tab erstellen/schließen
- [ ] Modified-Indikator (*)
- [ ] "Speichern?" Dialog bei ungespeicherten Änderungen
- [ ] Datei-Encoding Handling (UTF-8)

**Deliverable:** Multi-Tab Editor funktioniert

### Woche 4: Editor Polish & Integration

#### Tag 1-2: Kontextmenü & Shortcuts
**Tasks:**
- [ ] Editor Kontextmenü
- [ ] Keyboard Shortcuts (Ctrl+S, Ctrl+F, etc.)
- [ ] "Ausführen" Funktion (F5)
- [ ] Output Panel für Ausführung

**Deliverable:** Professionelles Editor-Feeling

#### Tag 3-4: Output Panel
```python
# src/gui/widgets/output_panel.py
class OutputPanel(QDockWidget):
    """Ausgabe-Panel für Run & Build"""
    
    def __init__(self, parent=None):
        super().__init__("Output", parent)
        
        self.tabs = QTabWidget()
        
        # Run Output
        self.run_output = QPlainTextEdit()
        self.run_output.setReadOnly(True)
        self.tabs.addTab(self.run_output, "Run")
        
        # Build Output
        self.build_output = QPlainTextEdit()
        self.build_output.setReadOnly(True)
        self.tabs.addTab(self.build_output, "Build")
        
        # Problems (für Analyzer)
        self.problems_list = QTreeWidget()
        self.tabs.addTab(self.problems_list, "Problems")
```

**Tasks:**
- [ ] Output Panel mit Tabs
- [ ] Run Output (stdout/stderr)
- [ ] ANSI Color Support
- [ ] Clear Button
- [ ] Copy to Clipboard

**Deliverable:** Vollständiges Output-System

#### Tag 5: Python Runner
```python
# src/modules/editor/python_runner.py
class PythonRunner(QObject):
    output_received = pyqtSignal(str)
    error_received = pyqtSignal(str)
    finished = pyqtSignal(int)  # exit_code
    
    def run(self, script_path: str, args: list = None):
        self.process = QProcess()
        self.process.readyReadStandardOutput.connect(self._handle_stdout)
        self.process.readyReadStandardError.connect(self._handle_stderr)
        self.process.finished.connect(self._handle_finished)
        
        self.process.start("python", [script_path] + (args or []))
```

**Tasks:**
- [ ] PythonRunner mit QProcess
- [ ] Stop-Button
- [ ] Working Directory setzen
- [ ] Umgebungsvariablen

**Deliverable:** Scripts können ausgeführt werden

---

## 📅 PHASE 2: Code-Analyse (Wochen 5-6)

### Woche 5: MethodenAnalyser Integration

#### Tag 1-2: AST-Analyse Engine
```python
# src/modules/analyzer/ast_analyzer.py
import ast
from dataclasses import dataclass
from typing import List, Set

@dataclass
class AnalysisResult:
    imports: List[str]
    unused_imports: List[str]
    classes: List[dict]
    functions: List[dict]
    undefined_names: List[str]
    duplicate_code: List[dict]
    complexity_warnings: List[str]

class ASTAnalyzer:
    def analyze_file(self, path: str) -> AnalysisResult:
        with open(path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        tree = ast.parse(source)
        
        return AnalysisResult(
            imports=self._extract_imports(tree),
            unused_imports=self._find_unused_imports(tree, source),
            classes=self._extract_classes(tree),
            functions=self._extract_functions(tree),
            undefined_names=self._find_undefined(tree),
            duplicate_code=self._find_duplicates(source),
            complexity_warnings=self._check_complexity(tree)
        )
```

**Tasks:**
- [ ] AST Parser aus MethodenAnalyser extrahieren
- [ ] Import-Analyse
- [ ] Unbenutzte Imports erkennen
- [ ] Klassen/Funktionen extrahieren
- [ ] Complexity Check (optional)

**Deliverable:** Analyse-Engine funktioniert

#### Tag 3-4: Problems Panel Integration
```python
# src/modules/analyzer/problems_provider.py
class ProblemsProvider(QObject):
    problems_updated = pyqtSignal(list)
    
    def analyze_and_report(self, path: str):
        result = self.analyzer.analyze_file(path)
        
        problems = []
        for imp in result.unused_imports:
            problems.append({
                'type': 'warning',
                'message': f"Unused import: {imp}",
                'file': path,
                'line': self._find_import_line(imp),
                'source': 'analyzer'
            })
        
        self.problems_updated.emit(problems)
```

**Tasks:**
- [ ] Problems Provider
- [ ] Problems in TreeWidget anzeigen
- [ ] Doppelklick → Zur Zeile springen
- [ ] Severity Icons (Error, Warning, Info)

**Deliverable:** Probleme werden im UI angezeigt

#### Tag 5: Live-Analyse
**Tasks:**
- [ ] Analyse bei Datei-Speicherung
- [ ] Analyse bei Tab-Wechsel
- [ ] Debounce für Live-Analyse (optional)
- [ ] Inline-Markierungen im Editor (Squiggles)

**Deliverable:** Echtzeit-Feedback

### Woche 6: Encoding & Utilities

#### Tag 1-2: EncodingFixer Integration
```python
# src/modules/analyzer/encoding_fixer.py
import ftfy

class EncodingFixer:
    def fix_file(self, path: str, backup: bool = True) -> bool:
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        fixed = ftfy.fix_text(content)
        
        if fixed != content:
            if backup:
                shutil.copy(path, path + '.bak')
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(fixed)
            return True
        return False
```

**Tasks:**
- [ ] EncodingFixer Klasse
- [ ] "Fix Encoding" Menüpunkt
- [ ] Automatische Erkennung bei Öffnen
- [ ] Batch-Fix für ganzes Projekt

**Deliverable:** Encoding-Probleme lösbar

#### Tag 3-4: Code Navigation
```python
# src/modules/analyzer/code_navigator.py
class CodeNavigator:
    """Schnelle Navigation zu Klassen/Funktionen"""
    
    def get_symbols(self, path: str) -> List[dict]:
        # Liefert Liste von {name, type, line}
        pass
```

**Tasks:**
- [ ] Symbol-Liste (Outline View)
- [ ] "Go to Symbol" Dialog (Ctrl+Shift+O)
- [ ] Breadcrumb-Navigation
- [ ] Klick auf Funktionsname → Definition

**Deliverable:** Schnelle Code-Navigation

#### Tag 5: Refactoring Basics
**Tasks:**
- [ ] Rename Symbol (F2)
- [ ] Extract Method (optional)
- [ ] Organize Imports

**Deliverable:** Basis-Refactoring funktioniert

---

## 📅 PHASE 3: Build-System (Wochen 7-9)

### Woche 7: Kompilator Integration

#### Tag 1-2: Build Engine
```python
# src/modules/builder/build_engine.py
from PyInstaller.__main__ import run as pyinstaller_run

class BuildEngine(QObject):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(bool, str)
    
    def build(self, config: BuildConfig):
        self.progress.emit(10, "Preparing build...")
        
        # PyInstaller Args zusammenbauen
        args = [
            config.main_file,
            f'--distpath={config.output_dir}',
            f'--workpath={config.temp_dir}',
            f'--specpath={config.temp_dir}',
        ]
        
        if config.onefile:
            args.append('--onefile')
        
        if config.icon:
            args.append(f'--icon={config.icon}')
        
        if not config.console:
            args.append('--windowed')
        
        # Hidden imports
        for imp in config.hidden_imports:
            args.append(f'--hidden-import={imp}')
        
        self.progress.emit(30, "Running PyInstaller...")
        
        try:
            pyinstaller_run(args)
            self.progress.emit(100, "Build complete!")
            self.finished.emit(True, config.output_dir)
        except Exception as e:
            self.finished.emit(False, str(e))
```

**Tasks:**
- [ ] BuildEngine Klasse
- [ ] PyInstaller Integration
- [ ] Progress Reporting
- [ ] Error Handling
- [ ] Build in separatem Thread

**Deliverable:** EXE-Erstellung funktioniert

#### Tag 3-4: Build Configuration
```python
# src/modules/builder/build_config.py
@dataclass
class BuildConfig:
    main_file: str
    output_dir: str = "dist"
    onefile: bool = True
    console: bool = True
    icon: Optional[str] = None
    name: Optional[str] = None
    hidden_imports: List[str] = field(default_factory=list)
    data_files: List[tuple] = field(default_factory=list)
    exclude_modules: List[str] = field(default_factory=list)
```

**Tasks:**
- [ ] BuildConfig Dataclass
- [ ] Build Settings Dialog
- [ ] Speichern in Projektdatei
- [ ] Presets (Console App, GUI App, etc.)

**Deliverable:** Konfigurierbare Builds

#### Tag 5: IcoBuilder Integration
```python
# src/modules/builder/icon_builder.py
from PIL import Image

ICO_SIZES = [(16,16), (24,24), (32,32), (48,48), (64,64), (128,128), (256,256)]

class IconBuilder:
    def convert_to_ico(self, input_path: str, output_path: str = None):
        img = Image.open(input_path)
        img = self._make_square(img)
        
        if output_path is None:
            output_path = Path(input_path).with_suffix('.ico')
        
        img.save(output_path, format='ICO', sizes=ICO_SIZES)
        return output_path
```

**Tasks:**
- [ ] IconBuilder Klasse
- [ ] Icon-Auswahl im Build Dialog
- [ ] Automatische Konvertierung PNG→ICO
- [ ] Icon Preview

**Deliverable:** Icons werden automatisch konvertiert

### Woche 8: Build Polish & Licenses

#### Tag 1-2: License Generator
```python
# src/modules/builder/license_generator.py
import subprocess

class LicenseGenerator:
    def generate(self, output_path: str):
        result = subprocess.run(
            ['pip-licenses', '--with-license-file', '--format=plain'],
            capture_output=True,
            text=True
        )
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("THIRD-PARTY LICENSES\n")
            f.write("=" * 50 + "\n\n")
            f.write(result.stdout)
```

**Tasks:**
- [ ] LicenseGenerator Klasse
- [ ] Automatisch bei Build erstellen
- [ ] In dist-Ordner kopieren
- [ ] Optional: In EXE einbetten

**Deliverable:** Lizenzen werden generiert

#### Tag 3-4: Build Output Management
**Tasks:**
- [ ] dist-Ordner im Explorer anzeigen
- [ ] "Open Output Folder" Button
- [ ] Build History
- [ ] Clean Build Option

**Deliverable:** Übersichtliches Build-Management

#### Tag 5: One-Click Build
```python
# Toolbar Button "Build" (F6)
def on_build_clicked(self):
    project = self.project_manager.current_project
    
    if not project.main_file:
        self.ask_for_main_file()
        return
    
    config = BuildConfig(
        main_file=project.main_file,
        output_dir=project.path / project.build_output_dir,
        icon=project.build_icon,
        onefile=project.build_onefile,
        console=project.build_console
    )
    
    self.build_engine.build(config)
```

**Tasks:**
- [ ] One-Click Build Workflow
- [ ] Main File Auto-Detection
- [ ] Build mit Ctrl+Shift+B
- [ ] Quick Build (letzte Einstellungen)

**Deliverable:** Schneller Build-Prozess

### Woche 9: Store Packager (Optional)

#### Tag 1-3: MSIX Manifest Generator
```python
# src/modules/builder/store_packager.py
class StorePackager:
    def generate_manifest(self, config: StoreConfig):
        manifest = f'''<?xml version="1.0" encoding="utf-8"?>
<Package xmlns="http://schemas.microsoft.com/appx/manifest/foundation/windows10">
  <Identity Name="{config.package_name}"
            Publisher="{config.publisher}"
            Version="{config.version}" />
  <Properties>
    <DisplayName>{config.display_name}</DisplayName>
    <PublisherDisplayName>{config.publisher_name}</PublisherDisplayName>
    <Logo>{config.logo_path}</Logo>
  </Properties>
  <!-- ... -->
</Package>'''
        return manifest
```

**Tasks:**
- [ ] MSIX Manifest Template
- [ ] Store Assets Generator (alle Icon-Größen)
- [ ] Publisher Certificate Handling
- [ ] Store Packager Wizard

**Deliverable:** Windows Store Vorbereitung möglich

#### Tag 4-5: Build Profiles
**Tasks:**
- [ ] Build Profiles (Debug, Release, Store)
- [ ] Profile Manager
- [ ] Schnellwechsel in Toolbar

**Deliverable:** Verschiedene Build-Konfigurationen

---

## 📅 PHASE 4: AI-Integration (Wochen 10-11)

### Woche 10: Entwicklerschleife Basics

#### Tag 1-2: AI Service Layer
```python
# src/modules/ai/ai_service.py
from anthropic import Anthropic

class AIService(QObject):
    response_received = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self):
        self.client = Anthropic(api_key=self._get_api_key())
    
    def _get_api_key(self) -> str:
        # Aus Settings oder Keyring
        return keyring.get_password("devcenter", "anthropic_api_key")
    
    async def complete(self, prompt: str, context: str = None):
        messages = []
        if context:
            messages.append({"role": "user", "content": context})
        messages.append({"role": "user", "content": prompt})
        
        response = await self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            messages=messages
        )
        
        self.response_received.emit(response.content[0].text)
```

**Tasks:**
- [ ] AIService Klasse
- [ ] API Key Management (Keyring)
- [ ] Settings Dialog für API Key
- [ ] Rate Limiting

**Deliverable:** AI-Anbindung funktioniert

#### Tag 3-4: AI Assistant Panel
```python
# src/modules/ai/ai_panel.py
class AIAssistantPanel(QDockWidget):
    def __init__(self):
        super().__init__("AI Assistant")
        
        layout = QVBoxLayout()
        
        # Chat History
        self.chat_history = QTextBrowser()
        layout.addWidget(self.chat_history)
        
        # Input
        self.input_field = QPlainTextEdit()
        self.input_field.setMaximumHeight(100)
        layout.addWidget(self.input_field)
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.send_btn = QPushButton("Send")
        self.context_btn = QPushButton("Include Code")
        btn_layout.addWidget(self.context_btn)
        btn_layout.addWidget(self.send_btn)
        layout.addLayout(btn_layout)
```

**Tasks:**
- [ ] AI Panel Widget
- [ ] Chat-Interface
- [ ] "Include Current File" Option
- [ ] Code-Blöcke formatieren

**Deliverable:** Chat-Interface für AI

#### Tag 5: Code-Context Integration
**Tasks:**
- [ ] Aktuellen Code an AI senden
- [ ] Selektion als Context
- [ ] Projekt-Struktur als Context
- [ ] Error Messages als Context

**Deliverable:** AI kennt den Code-Kontext

### Woche 11: AI Features

#### Tag 1-2: Code Generation
```python
# src/modules/ai/code_generator.py
class CodeGenerator:
    PROMPTS = {
        'explain': "Explain this code:\n\n{code}",
        'improve': "Suggest improvements for this code:\n\n{code}",
        'document': "Add docstrings to this code:\n\n{code}",
        'test': "Generate unit tests for this code:\n\n{code}",
    }
    
    def generate(self, action: str, code: str):
        prompt = self.PROMPTS[action].format(code=code)
        return self.ai_service.complete(prompt)
```

**Tasks:**
- [ ] "Explain Code" Funktion
- [ ] "Improve Code" Funktion
- [ ] "Add Documentation" Funktion
- [ ] "Generate Tests" Funktion

**Deliverable:** AI-gestützte Code-Aktionen

#### Tag 3-4: Inline Suggestions
**Tasks:**
- [ ] Rechtsklick → "Ask AI about this"
- [ ] AI-Antwort als Panel oder Dialog
- [ ] "Insert Suggestion" Button
- [ ] Diff-View für Änderungen

**Deliverable:** Kontextbezogene AI-Hilfe

#### Tag 5: Entwicklerschleife Workflow
```python
# Planner → Coder → Checker Workflow
class DevelopmentLoop:
    async def run(self, task_description: str, project_context: str):
        # 1. Planner
        plan = await self.ai_service.complete(
            f"Plan the implementation for: {task_description}\nContext: {project_context}"
        )
        
        # 2. Coder
        code = await self.ai_service.complete(
            f"Implement this plan:\n{plan}"
        )
        
        # 3. Checker
        review = await self.ai_service.complete(
            f"Review this implementation:\n{code}"
        )
        
        return {'plan': plan, 'code': code, 'review': review}
```

**Tasks:**
- [ ] 3-Phasen Workflow implementieren
- [ ] Wizard für Entwicklerschleife
- [ ] Ergebnisse in Editor einfügen
- [ ] Iteration ermöglichen

**Deliverable:** Vollständige AI-Entwicklungsunterstützung

---

## 📅 PHASE 5: FileManager & Polish (Wochen 12-13)

### Woche 12: ProFiler Integration

#### Tag 1-2: ProFiler Bridge
```python
# src/modules/filemanager/profiler_bridge.py
class ProfilerBridge:
    """Verbindung zu ProFiler für Datei-Index"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
    
    def index_project(self, project_path: str):
        """Indiziert alle Dateien im Projekt"""
        for file in Path(project_path).rglob("*.py"):
            self._index_file(file)
    
    def search(self, query: str) -> List[dict]:
        """Suche in indizierten Dateien"""
        cursor = self.conn.execute(
            "SELECT path, content FROM files WHERE content LIKE ?",
            (f"%{query}%",)
        )
        return [{'path': row[0], 'content': row[1]} for row in cursor]
```

**Tasks:**
- [ ] ProfilerBridge Klasse
- [ ] Projekt-Indizierung
- [ ] Volltext-Suche
- [ ] Hash-basierte Duplikat-Erkennung

**Deliverable:** Schnelle Projekt-Suche

#### Tag 3-4: Global Search
```python
# src/gui/dialogs/search_dialog.py
class GlobalSearchDialog(QDialog):
    """Projekt-weite Suche (Ctrl+Shift+F)"""
    
    file_selected = pyqtSignal(str, int)  # path, line
```

**Tasks:**
- [ ] Global Search Dialog
- [ ] Suche in allen Dateien
- [ ] Regex-Support
- [ ] Ergebnis-Preview
- [ ] Replace All (optional)

**Deliverable:** Projekt-weite Suche

#### Tag 5: ProSync Integration
```python
# src/modules/filemanager/sync_manager.py
class SyncManager:
    """Automatische Backups mit ProSync-Logik"""
    
    def backup_project(self, project_path: str, target_path: str):
        # WAL Checkpoint für SQLite
        self._checkpoint_databases(project_path)
        
        # Sync mit Excludes
        excludes = ['__pycache__', '.git', 'dist', 'build', '*.pyc']
        self._sync_directory(project_path, target_path, excludes)
```

**Tasks:**
- [ ] SyncManager Klasse
- [ ] Auto-Backup bei Speichern (optional)
- [ ] Manual Backup Funktion
- [ ] Backup-Ziel konfigurieren

**Deliverable:** Automatische Backups

### Woche 13: Final Polish

#### Tag 1-2: Themes & Appearance
**Tasks:**
- [ ] Dark Theme
- [ ] Light Theme
- [ ] Theme Switcher
- [ ] Editor Color Schemes
- [ ] Font Settings

**Deliverable:** Anpassbare Optik

#### Tag 3: Settings Dialog
```python
# src/gui/dialogs/settings_dialog.py
class SettingsDialog(QDialog):
    """Zentrale Einstellungen"""
    
    def __init__(self):
        self.tabs = QTabWidget()
        self.tabs.addTab(GeneralSettingsPage(), "General")
        self.tabs.addTab(EditorSettingsPage(), "Editor")
        self.tabs.addTab(BuildSettingsPage(), "Build")
        self.tabs.addTab(AISettingsPage(), "AI")
        self.tabs.addTab(SyncSettingsPage(), "Sync")
```

**Tasks:**
- [ ] Settings Dialog mit Tabs
- [ ] Alle Einstellungen zentralisieren
- [ ] Import/Export Settings
- [ ] Reset to Defaults

**Deliverable:** Vollständige Einstellungsverwaltung

#### Tag 4: Keyboard Shortcuts
```python
# Wichtige Shortcuts
SHORTCUTS = {
    'Ctrl+N': 'New File',
    'Ctrl+O': 'Open File',
    'Ctrl+S': 'Save',
    'Ctrl+Shift+S': 'Save All',
    'F5': 'Run',
    'Ctrl+F5': 'Run Without Debugging',
    'F6': 'Build',
    'Ctrl+Shift+B': 'Build Configuration',
    'Ctrl+F': 'Find',
    'Ctrl+H': 'Replace',
    'Ctrl+Shift+F': 'Find in Files',
    'Ctrl+G': 'Go to Line',
    'Ctrl+P': 'Quick Open',
    'Ctrl+Shift+O': 'Go to Symbol',
    'F2': 'Rename',
    'Ctrl+Space': 'Autocomplete',
}
```

**Tasks:**
- [ ] Alle Shortcuts implementieren
- [ ] Shortcut Customization (optional)
- [ ] Shortcut Cheatsheet Dialog

**Deliverable:** Professionelle Tastatursteuerung

#### Tag 5: Testing & Bug Fixes
**Tasks:**
- [ ] Manuelle Tests aller Features
- [ ] Bug Fixes
- [ ] Performance-Optimierung
- [ ] Memory Leaks prüfen

**Deliverable:** Stabiles MVP

---

## 📋 Meilensteine & Deliverables

| Woche | Meilenstein | Deliverable |
|-------|-------------|-------------|
| 1 | Projekt-Setup | Strukturiertes Repository |
| 2 | Projekt-Management | Projekte erstellen/öffnen |
| 3 | Editor Basis | Syntax-Highlighted Editor |
| 4 | Editor Komplett | Multi-Tab Editor + Run |
| 5 | Analyse Basis | AST-Analyse funktioniert |
| 6 | Analyse Komplett | Live-Analyse + Navigation |
| 7 | Build Basis | EXE-Erstellung funktioniert |
| 8 | Build Komplett | One-Click Build + Licenses |
| 9 | Store Packager | MSIX-Vorbereitung (optional) |
| 10 | AI Basis | AI Chat funktioniert |
| 11 | AI Komplett | Code-Generierung + Workflow |
| 12 | FileManager | Suche + Backup |
| 13 | MVP Release | Stabile Version 1.0 |

---

## ⚠️ Risiken & Mitigationen

| Risiko | Wahrscheinlichkeit | Impact | Mitigation |
|--------|-------------------|--------|------------|
| PyInstaller Kompatibilität | Mittel | Hoch | Früh testen, Alternative: cx_Freeze |
| QScintilla Einarbeitung | Mittel | Mittel | PythonBox Code als Referenz |
| AI API Kosten | Niedrig | Mittel | Rate Limiting, lokale Alternative (Ollama) |
| Performance bei großen Projekten | Mittel | Mittel | Lazy Loading, Background Threads |
| Windows-spezifische Bugs | Hoch | Niedrig | Frühes Testen auf verschiedenen Windows-Versionen |

---

## 🔧 Technische Abhängigkeiten

```
requirements.txt:
PyQt6>=6.4.0
QScintilla>=2.13.0
pyinstaller>=5.0.0
Pillow>=9.0.0
anthropic>=0.18.0
keyring>=23.0.0
ftfy>=6.1.0
pip-licenses>=4.0.0
watchdog>=3.0.0
```

---

*Detaillierter Umsetzungsplan erstellt: 03.01.2026*
