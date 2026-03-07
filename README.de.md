# 🚀 DevCenter

**Python Development Suite** - Eine integrierte Entwicklungsumgebung für den kompletten Python-Entwicklungszyklus

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.10+-green)
![License](https://img.shields.io/badge/license-GPL%20v3-blue)

## 📋 Übersicht

DevCenter ist eine All-in-One Desktop-IDE für Python-Projekte, die den kompletten Entwicklungszyklus unterstützt:

**Code schreiben → Analysieren → Testen → Kompilieren → Veröffentlichen**

### 🔧 Fusionierte Tools

DevCenter vereint 11 spezialisierte Entwicklertools zu einer kohärenten Suite:

| Ursprungstool | Modul | Funktion |
|---------------|-------|----------|
| PythonBox V8 | Editor | Code-Editor mit Syntax-Highlighting, Auto-Indent |
| MethodenAnalyser V3 | Analyzer | Statische Code-Analyse, Komplexitätsberechnung |
| EncodingFixer | Analyzer | Encoding-Erkennung und -Reparatur |
| UltimateKompilator V3.1 | Builder | Python → EXE Kompilierung via PyInstaller |
| IcoBuilder | Builder | Bild → ICO Konvertierung |
| ThirdPartyLicenses | Builder | Lizenz-Sammlung für Third-Party-Pakete |
| Entwicklerschleife V3 | AI Assistant | Claude API Integration für Code-Generierung |
| ProFiler V14 | FileManager | Datei-Indizierung und Volltext-Suche |
| ProSync V3.1 | FileManager | Intelligente Backup-Synchronisation |

## 🛠️ Installation

### Voraussetzungen
- Python 3.10 oder höher
- Windows 10/11 (primär), Linux/macOS (experimentell)

### Installation

```bash
# Repository klonen oder Dateien kopieren
cd DevCenter

# Abhängigkeiten installieren
pip install -r requirements.txt

# Starten
python main.py
```

### Abhängigkeiten

```
PyQt6>=6.4.0          # GUI-Framework
pyinstaller>=5.0      # EXE-Erstellung
Pillow>=9.0           # Bildverarbeitung
anthropic>=0.18.0     # Claude API
chardet>=5.0          # Encoding-Erkennung
keyring>=23.0         # Sichere Schlüsselspeicherung
```

## 📦 Projektstruktur

```
DevCenter/
├── main.py                      # Haupteinstiegspunkt
├── requirements.txt             # Abhängigkeiten
├── README.md                    # Diese Datei
│
├── src/
│   ├── __init__.py
│   │
│   ├── core/                    # Kernkomponenten
│   │   ├── project_manager.py   # Projektverwaltung
│   │   ├── settings_manager.py  # Einstellungen (Singleton)
│   │   └── event_bus.py         # Event-System (Pub/Sub)
│   │
│   ├── modules/
│   │   ├── editor/              # Code-Editor
│   │   │   └── code_editor.py   # Editor mit Syntax-Highlighting
│   │   │
│   │   ├── analyzer/            # Code-Analyse
│   │   │   ├── method_analyzer.py  # AST-basierte Analyse
│   │   │   └── encoding_fixer.py   # Encoding-Tools
│   │   │
│   │   ├── builder/             # Build-System
│   │   │   ├── kompilator.py       # PyInstaller-Wrapper
│   │   │   ├── icon_builder.py     # ICO-Konvertierung
│   │   │   └── license_generator.py # Lizenz-Sammlung
│   │   │
│   │   ├── ai_assistant/        # AI-Integration
│   │   │   └── ai_service.py    # Claude API + DevelopmentLoop
│   │   │
│   │   └── filemanager/         # Datei-Management
│   │       ├── sync_manager.py  # Backup-Synchronisation
│   │       └── profiler_bridge.py # Datei-Index
│   │
│   └── gui/
│       ├── main_window.py       # Hauptfenster
│       │
│       ├── panels/              # UI-Panels
│       │   ├── explorer_panel.py   # Datei-Navigator
│       │   ├── output_panel.py     # Terminal-Ausgabe
│       │   ├── problems_panel.py   # Fehler/Warnungen
│       │   └── ai_panel.py         # AI-Chat-Interface
│       │
│       └── dialogs/             # Dialoge
│           ├── new_project_dialog.py
│           ├── settings_dialog.py
│           └── build_dialog.py
│
├── resources/
│   ├── themes/                  # UI-Themes
│   └── icons/                   # Anwendungs-Icons
│
└── tests/
    └── test_core.py             # Unit-Tests
```

## ⚡ Features

### Editor
- ✅ Python Syntax-Highlighting (Keywords, Strings, Kommentare, Decorators)
- ✅ Zeilennummern mit aktueller Zeilen-Hervorhebung
- ✅ Auto-Indent (erhält Einrückung, fügt nach `:` hinzu)
- ✅ Smart Backspace (springt zu Tab-Stops)
- ✅ Kommentar-Toggle (Ctrl+/)
- ✅ Mehrere Editor-Tabs
- ✅ Drag & Drop Dateien

### Analyse
- ✅ Klassen- und Methoden-Erkennung
- ✅ Import-Analyse (genutzt/ungenutzt)
- ✅ Zyklomatische Komplexitäts-Berechnung
- ✅ Mutable Default Argument Warnung
- ✅ Bare Except Warnung
- ✅ TODO/FIXME Erkennung
- ✅ Encoding-Prüfung und -Reparatur

### Build
- ✅ One-Click EXE-Erstellung
- ✅ One-File und One-Directory Modi
- ✅ Icon-Konvertierung (PNG/JPG → ICO)
- ✅ Hidden Imports Verwaltung
- ✅ Zusätzliche Dateien einbinden
- ✅ UPX-Komprimierung (optional)
- ✅ Third-Party-Lizenzen sammeln

### AI-Assistent
- ✅ Claude API Integration
- ✅ Code-Generierung aus Beschreibungen
- ✅ Code-Review und Verbesserungsvorschläge
- ✅ Code-Erklärungen
- ✅ Fehler-Behebungshilfe
- ✅ Entwicklerschleife (Plan → Code → Review)

### Datei-Management
- ✅ Projekt-Explorer mit Kontextmenü
- ✅ SQLite-basierter Datei-Index
- ✅ Volltext-Suche im Code
- ✅ Duplikat-Erkennung (Hash-basiert)
- ✅ Automatische Backups mit WAL-Checkpoint
- ✅ Musterbasierte Ausschlüsse

## 🎨 Benutzeroberfläche

```
┌─────────────────────────────────────────────────────────────────┐
│  Datei  Bearbeiten  Ansicht  Ausführen  Analyse  Hilfe          │
├─────────────────────────────────────────────────────────────────┤
│  📁 Neu  📂 Öffnen  💾 Speichern  │  ▶ Ausführen  🔨 Build  │ 🤖 │
├────────────┬────────────────────────────────┬───────────────────┤
│ 📁 EXPLORER│  main.py  │  utils.py  │ ●app │   🤖 AI Assistent │
│            │─────────────────────────────────│                   │
│ 📁 src     │  1 │ # -*- coding: utf-8 -*-    │   [Chat-Verlauf]  │
│   📄 main  │  2 │ """                        │                   │
│   📄 utils │  3 │ DevCenter - Main           │   ─────────────   │
│   📁 gui   │  4 │ """                        │                   │
│            │  5 │                            │   [Input-Feld]    │
│            │  6 │ import sys                 │   [✨] [🔍] [📖]  │
│            ├────────────────────────────────┤                   │
│            │  🖥️ Terminal  │  ⚠️ Probleme   │                   │
│            │  $ python main.py              │                   │
│            │  Hello, World!                 │                   │
│            │  ✓ Prozess beendet (Code: 0)   │                   │
├────────────┴────────────────────────────────┴───────────────────┤
│  📁 DevCenter                              Ln 5, Col 1  │ UTF-8 │
└─────────────────────────────────────────────────────────────────┘
```

## ⌨️ Tastenkürzel

| Kürzel | Aktion |
|--------|--------|
| Ctrl+N | Neue Datei |
| Ctrl+O | Datei öffnen |
| Ctrl+S | Speichern |
| Ctrl+Shift+N | Neues Projekt |
| Ctrl+Shift+O | Projekt öffnen |
| Ctrl+Shift+S | Speichern unter |
| F5 | Ausführen |
| F6 | Build erstellen |
| Ctrl+/ | Kommentar umschalten |
| Ctrl+Shift+A | AI-Assistent umschalten |
| Ctrl+, | Einstellungen |

## 🔧 Konfiguration

Einstellungen werden gespeichert in:
- **Windows:** `%APPDATA%\DevCenter\settings.json`
- **Linux/macOS:** `~/.config/DevCenter/settings.json`

### Wichtige Einstellungen

```json
{
  "editor": {
    "font_family": "Consolas",
    "font_size": 11,
    "tab_size": 4,
    "line_numbers": true,
    "auto_save": false
  },
  "build": {
    "output_dir": "dist",
    "one_file": true,
    "console": true
  },
  "ai": {
    "api_key": "sk-...",
    "model": "claude-sonnet-4-20250514",
    "max_tokens": 4096
  },
  "sync": {
    "backup_path": "D:\\Backups\\DevCenter",
    "auto_backup": true,
    "excludes": ["__pycache__", ".git", "venv"]
  }
}
```

## 🧪 Tests

```bash
# Alle Tests ausführen
python -m pytest tests/ -v

# Oder mit unittest
python tests/test_core.py
```

## 📊 Statistiken

| Metrik | Wert |
|--------|------|
| Python-Dateien | 26 |
| Code-Zeilen | ~7.500 |
| Module | 5 (Core, Editor, Analyzer, Builder, FileManager, AI) |
| GUI-Panels | 4 |
| GUI-Dialoge | 3 |
| Unit-Tests | 20+ |

## 🗺️ Roadmap

### Version 1.1
- [ ] Code-Folding
- [ ] Erweiterte Suchen-Ersetzen
- [ ] Git-Integration
- [ ] Debugger-Unterstützung

### Version 1.2
- [ ] Plugin-System
- [ ] Weitere Themes
- [ ] MSIX-Packaging
- [ ] Auto-Update

## 📝 Lizenz

GPL v3 - Siehe [LICENSE](LICENSE)

Dieses Projekt verwendet PyQt6 (GPL).

## 🤝 Mitwirkende

Basiert auf dem Fusionskonzept der Entwickler-Suite.
Erstellt mit PyQt6 und Claude AI.

---

**DevCenter v1.0.0** | Januar 2026

---

English version: [README.md](README.md)
