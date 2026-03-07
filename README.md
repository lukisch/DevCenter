# DevCenter

**Python Development Suite** - An integrated development environment for the complete Python development cycle

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.10+-green)
![License](https://img.shields.io/badge/license-GPL%20v3-blue)

## Overview

DevCenter is an all-in-one desktop IDE for Python projects that supports the complete development cycle:

**Write code -> Analyze -> Test -> Compile -> Publish**

### Fused Tools

DevCenter combines 11 specialized developer tools into one coherent suite:

| Original Tool | Module | Function |
|---------------|--------|----------|
| PythonBox V8 | Editor | Code editor with syntax highlighting, auto-indent |
| MethodenAnalyser V3 | Analyzer | Static code analysis, complexity calculation |
| EncodingFixer | Analyzer | Encoding detection and repair |
| UltimateKompilator V3.1 | Builder | Python -> EXE compilation via PyInstaller |
| IcoBuilder | Builder | Image -> ICO conversion |
| ThirdPartyLicenses | Builder | License collection for third-party packages |
| Entwicklerschleife V3 | AI Assistant | Claude API integration for code generation |
| ProFiler V14 | FileManager | File indexing and full-text search |
| ProSync V3.1 | FileManager | Intelligent backup synchronization |

## Installation

### Prerequisites
- Python 3.10 or higher
- Windows 10/11 (primary), Linux/macOS (experimental)

### Setup

```bash
# Clone the repository or copy files
cd DevCenter

# Install dependencies
pip install -r requirements.txt

# Run
python main.py
```

### Dependencies

```
PyQt6>=6.4.0            # GUI framework
pyinstaller>=5.0        # EXE creation
Pillow>=9.0             # Image processing
anthropic>=0.18.0       # Claude API
chardet>=5.0            # Encoding detection
keyring>=23.0           # Secure key storage
```

## Project Structure

```
DevCenter/
+-- main.py                        # Main entry point
+-- requirements.txt               # Dependencies
+-- README.md                      # This file
|
+-- src/
|   +-- __init__.py
|   |
|   +-- core/                      # Core components
|   |   +-- project_manager.py     # Project management
|   |   +-- settings_manager.py    # Settings (singleton)
|   |   +-- event_bus.py           # Event system (pub/sub)
|   |
|   +-- modules/
|   |   +-- editor/                # Code editor
|   |   |   +-- code_editor.py     # Editor with syntax highlighting
|   |   |
|   |   +-- analyzer/              # Code analysis
|   |   |   +-- method_analyzer.py # AST-based analysis
|   |   |   +-- encoding_fixer.py  # Encoding tools
|   |   |
|   |   +-- builder/               # Build system
|   |   |   +-- kompilator.py      # PyInstaller wrapper
|   |   |   +-- icon_builder.py    # ICO conversion
|   |   |   +-- license_generator.py # License collection
|   |   |
|   |   +-- ai_assistant/          # AI integration
|   |   |   +-- ai_service.py      # Claude API + development loop
|   |   |
|   |   +-- filemanager/           # File management
|   |       +-- sync_manager.py    # Backup synchronization
|   |       +-- profiler_bridge.py # File index
|   |
|   +-- gui/
|       +-- main_window.py         # Main window
|       |
|       +-- panels/                # UI panels
|       |   +-- explorer_panel.py  # File navigator
|       |   +-- output_panel.py    # Terminal output
|       |   +-- problems_panel.py  # Errors/warnings
|       |   +-- ai_panel.py        # AI chat interface
|       |
|       +-- dialogs/               # Dialogs
|           +-- new_project_dialog.py
|           +-- settings_dialog.py
|           +-- build_dialog.py
|
+-- resources/
|   +-- themes/                    # UI themes
|   +-- icons/                     # Application icons
|
+-- tests/
    +-- test_core.py               # Unit tests
```

## Features

### Editor
- Python syntax highlighting (keywords, strings, comments, decorators)
- Line numbers with current line highlighting
- Auto-indent (preserves indentation, adds after `:`)
- Smart backspace (jumps to tab stops)
- Comment toggle (Ctrl+/)
- Multiple editor tabs
- Drag & drop files

### Analysis
- Class and method detection
- Import analysis (used/unused)
- Cyclomatic complexity calculation
- Mutable default argument warning
- Bare except warning
- TODO/FIXME detection
- Encoding check and repair

### Build
- One-click EXE creation
- One-file and one-directory modes
- Icon conversion (PNG/JPG -> ICO)
- Hidden imports management
- Include additional files
- UPX compression (optional)
- Third-party license collection

### AI Assistant
- Claude API integration
- Code generation from descriptions
- Code review and improvement suggestions
- Code explanations
- Error fixing assistance
- Development loop (plan -> code -> review)

### File Management
- Project explorer with context menu
- SQLite-based file index
- Full-text search in code
- Duplicate detection (hash-based)
- Automatic backups with WAL checkpoint
- Pattern-based exclusions

## User Interface

```
+------------------------------------------------------------------+
|  File  Edit  View  Run  Analysis  Help                           |
+------------------------------------------------------------------+
|  New  Open  Save  |  Run  Build  |  AI  |
+------------+-------------------------------------+-------------------+
| EXPLORER   |  main.py  |  utils.py  | app       |   AI Assistant    |
|            |--------------------------------------|                   |
|  src       |  1 | # -*- coding: utf-8 -*-        |   [Chat History]  |
|    main    |  2 | """                             |                   |
|    utils   |  3 | DevCenter - Main                |   ---------------  |
|    gui     |  4 | """                             |                   |
|            |  5 |                                 |   [Input Field]    |
|            |  6 | import sys                      |   [Send] [Search] [Attach]  |
|            |--------------------------------------|                   |
|            |  Terminal  |  Problems   |           |                   |
|            |  $ python main.py                    |                   |
|            |  Hello, World!                       |                   |
|            |  Process finished (Code: 0)          |                   |
+------------+------------------------------------+-------------------+
|  DevCenter                              Ln 5, Col 1  | UTF-8 |
+------------------------------------------------------------------+
```

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+N | New file |
| Ctrl+O | Open file |
| Ctrl+S | Save |
| Ctrl+Shift+N | New project |
| Ctrl+Shift+O | Open project |
| Ctrl+Shift+S | Save as |
| F5 | Run |
| F6 | Build |
| Ctrl+/ | Toggle comment |
| Ctrl+Shift+A | Toggle AI assistant |
| Ctrl+, | Settings |

## Configuration

Settings are stored in:
- **Windows:** `%APPDATA%\DevCenter\settings.json`
- **Linux/macOS:** `~/.config/DevCenter/settings.json`

### Key Settings

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

## Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Or with unittest
python tests/test_core.py
```

## Statistics

| Metric | Value |
|--------|-------|
| Python files | 26 |
| Lines of code | ~7,500 |
| Modules | 5 (Core, Editor, Analyzer, Builder, FileManager, AI) |
| GUI panels | 4 |
| GUI dialogs | 3 |
| Unit tests | 20+ |

## Roadmap

### Version 1.1
- [ ] Code folding
- [ ] Extended search & replace
- [ ] Git integration
- [ ] Debugger support

### Version 1.2
- [ ] Plugin system
- [ ] Additional themes
- [ ] MSIX packaging
- [ ] Auto-update

## License

GPL v3 - See [LICENSE](LICENSE)

This project uses PyQt6 (GPL).

## Contributors

Based on the fusion concept of the developer suite.
Created with PyQt6 and Claude AI.

---

**DevCenter v1.0.0** | January 2026

---

Deutsche Version: [README.de.md](README.de.md)
