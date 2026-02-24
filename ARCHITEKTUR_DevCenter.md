# DevCenter - Architektur-Dokumentation

## Übersicht

DevCenter ist eine modulare Python-IDE, die nach dem Prinzip der losen Kopplung entwickelt wurde.
Die Architektur basiert auf drei Hauptschichten:

```
┌─────────────────────────────────────────────────────────────────┐
│                         GUI Layer                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │ MainWindow  │  │   Panels    │  │        Dialogs          │  │
│  │             │  │  Explorer   │  │  NewProject, Settings   │  │
│  │             │  │  Output     │  │  Build                  │  │
│  │             │  │  Problems   │  │                         │  │
│  │             │  │  AI Panel   │  │                         │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│                       Module Layer                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌───────────────┐   │
│  │  Editor  │  │ Analyzer │  │ Builder  │  │ AI Assistant  │   │
│  │          │  │          │  │          │  │               │   │
│  │ CodeEdit │  │ Methods  │  │ Kompilat │  │  AIService    │   │
│  │ Highlight│  │ Encoding │  │ Icon     │  │  DevLoop      │   │
│  │          │  │          │  │ License  │  │               │   │
│  └──────────┘  └──────────┘  └──────────┘  └───────────────┘   │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                     FileManager                            │  │
│  │            SyncManager      ProfilerBridge                 │  │
│  └───────────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│                        Core Layer                                │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │ ProjectManager  │  │ SettingsManager │  │    EventBus     │  │
│  │                 │  │   (Singleton)   │  │   (Pub/Sub)     │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Core Layer

### ProjectManager
- Verwaltet Projekt-Konfigurationen (ProjectConfig Dataclass)
- Erstellt Projekt-Struktur (src/, tests/, README.md, requirements.txt)
- Speichert/Lädt Projektdaten in `devcenter.json`
- Verwaltet Recent-Projects-Liste

### SettingsManager (Singleton)
- Zentraler Zugriff auf alle Einstellungen via `get_settings()`
- Dot-Notation für verschachtelte Schlüssel: `settings.get('editor.font_size')`
- Dataclass-basierte Konfiguration:
  - EditorSettings
  - BuildSettings
  - AISettings
  - SyncSettings
  - AppearanceSettings
- Persistenz in `%APPDATA%/DevCenter/settings.json`

### EventBus (Pub/Sub)
- Ermöglicht lose Kopplung zwischen Modulen
- Event-Typen: FILE_OPENED, FILE_SAVED, ANALYSIS_COMPLETED, BUILD_STARTED, etc.
- Convenience-Methoden: `emit_file_opened()`, `emit_status_message()`
- Event-History für Debugging

## Module Layer

### Editor Module
**CodeEditor** (QPlainTextEdit):
- PythonHighlighter für Syntax-Highlighting
- LineNumberArea Widget
- Auto-Indent, Smart Backspace
- Signals: `file_modified`, `cursor_position_changed`

### Analyzer Module
**MethodAnalyzer**:
- AST-basierte Python-Code-Analyse
- Erkennt: Klassen, Methoden, Imports, Variablen
- Berechnet: Zyklomatische Komplexität
- Warnungen: Mutable Defaults, Bare Except, TODOs

**EncodingFixer**:
- Encoding-Erkennung via chardet
- UTF-8 Konvertierung
- BOM-Erkennung

### Builder Module
**Kompilator**:
- PyInstaller-Wrapper
- BuildConfig Dataclass für Optionen
- Progress-Callbacks
- Spec-File-Generierung

**IcoBuilder**:
- Pillow-basierte Bild→ICO Konvertierung
- Multi-Size Icons (16-256px)
- Platzhalter-Generierung

**LicenseGenerator**:
- pip-licenses Integration
- Third-Party-Notices generieren
- Lizenz-Kompatibilitäts-Check

### AI Assistant Module
**AIService**:
- Anthropic Claude API Integration
- Async Completion mit History
- Spezialmethoden: generate_code, review_code, fix_error, explain_code

**DevelopmentLoop**:
- Automatisierte 3-Phasen-Entwicklung:
  1. Planner: Architektur erstellen
  2. Coder: Code implementieren
  3. Checker: Review durchführen

### FileManager Module
**SyncManager**:
- Datei-Synchronisation mit Muster-Ausschlüssen
- SQLite WAL-Checkpoint vor Backup
- Hash-Verifizierung nach Kopieren
- BackupScheduler für automatische Backups

**ProfilerBridge**:
- SQLite FTS5 Volltext-Index
- Datei-Indizierung mit Content-Vorschau
- Hash-basierte Duplikat-Erkennung
- Projekt-bezogene Filterung

## GUI Layer

### MainWindow
- 3-Panel-Layout: Explorer | Editor+Output | AI Assistant
- Menüleiste, Toolbar, Statusbar
- Tab-Management für Editor
- Event-Bus Integration

### Panels
- **ExplorerPanel**: QTreeView mit QFileSystemModel, Kontextmenü
- **OutputPanel**: Terminal mit QProcess, farbige Ausgabe
- **ProblemsPanel**: QTreeWidget für Fehler/Warnungen
- **AIAssistantPanel**: Chat-Interface mit Thread-Worker

### Dialogs
- **NewProjectDialog**: Projekt-Erstellung mit Templates
- **SettingsDialog**: 5-Tab Einstellungen
- **BuildDialog**: Build-Wizard mit Progress

## Datenfluss

```
User Action → GUI Event → Module → Core/Storage
     ↓                      ↓
EventBus ← Status/Results ←─┘
     ↓
GUI Update
```

## Erweiterbarkeit

### Neue Module hinzufügen
1. Erstelle `src/modules/neues_modul/`
2. Implementiere Hauptklasse
3. Registriere Events im EventBus
4. Erstelle Panel/Dialog falls nötig
5. Integriere in MainWindow

### Neue Analyse-Regeln
1. Erweitere `MethodAnalyzer._check_common_issues()`
2. Füge AST-Visitor hinzu falls komplex
3. Erstelle Problem mit passendem Severity

## Performance-Überlegungen

- **Lazy Loading**: Module werden bei Bedarf importiert
- **Thread-Worker**: AI-Anfragen und Build in separaten Threads
- **FTS5 Index**: Schnelle Volltext-Suche auch bei großen Projekten
- **WAL Mode**: Nicht-blockierende SQLite-Operationen

## Sicherheit

- API-Keys in System-Keyring (optional)
- Keine Netzwerk-Operationen ohne User-Aktion
- Sandbox für Prozess-Ausführung (QProcess)

---

**Version**: 1.0.0 | **Stand**: Januar 2026
