# -*- coding: utf-8 -*-
"""
DevCenter - Project Manager
Verwaltung von Python-Projekten
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict
from PyQt6.QtCore import QObject, pyqtSignal


@dataclass
class ProjectConfig:
    """Projekt-Konfigurationsdaten"""
    name: str
    path: str
    created: str
    last_opened: str
    main_file: str = ""
    python_version: str = "3.12"
    description: str = ""
    author: str = ""
    version: str = "1.0.0"
    build_config: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.build_config is None:
            self.build_config = {
                "output_dir": "dist",
                "one_file": True,
                "console": True,
                "icon": ""
            }


class ProjectManager(QObject):
    """
    Zentrale Projektverwaltung für DevCenter
    
    Signals:
        project_opened: Projekt wurde geöffnet (ProjectConfig)
        project_closed: Projekt wurde geschlossen
        project_created: Neues Projekt erstellt (ProjectConfig)
        recent_projects_changed: Liste der Recent Projects hat sich geändert
    """
    
    project_opened = pyqtSignal(object)  # ProjectConfig
    project_closed = pyqtSignal()
    project_created = pyqtSignal(object)  # ProjectConfig
    recent_projects_changed = pyqtSignal(list)
    
    PROJECT_FILE = "devcenter.json"
    MAX_RECENT = 10
    
    def __init__(self, settings_path: str = None):
        super().__init__()
        self.current_project: Optional[ProjectConfig] = None
        self.settings_path = settings_path or self._default_settings_path()
        self.recent_projects: List[Dict[str, str]] = []
        self._load_recent_projects()
    
    def _default_settings_path(self) -> str:
        """Standardpfad für Einstellungen"""
        app_data = os.environ.get('APPDATA', os.path.expanduser('~'))
        settings_dir = Path(app_data) / 'DevCenter'
        settings_dir.mkdir(exist_ok=True)
        return str(settings_dir / 'settings.json')
    
    def _load_recent_projects(self):
        """Lädt die Liste der zuletzt geöffneten Projekte"""
        settings_file = Path(self.settings_path)
        if settings_file.exists():
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.recent_projects = data.get('recent_projects', [])
            except (json.JSONDecodeError, IOError):
                self.recent_projects = []
    
    def _save_recent_projects(self):
        """Speichert die Liste der zuletzt geöffneten Projekte"""
        settings_file = Path(self.settings_path)
        settings_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Bestehende Einstellungen laden
            data = {}
            if settings_file.exists():
                with open(settings_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            
            data['recent_projects'] = self.recent_projects
            
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Fehler beim Speichern der Recent Projects: {e}")
    
    def _add_to_recent(self, project_path: str, project_name: str):
        """Fügt ein Projekt zur Recent-Liste hinzu"""
        entry = {"path": project_path, "name": project_name}
        
        # Existierenden Eintrag entfernen
        self.recent_projects = [
            p for p in self.recent_projects 
            if p.get('path') != project_path
        ]
        
        # Am Anfang einfügen
        self.recent_projects.insert(0, entry)
        
        # Liste kürzen
        self.recent_projects = self.recent_projects[:self.MAX_RECENT]
        
        self._save_recent_projects()
        self.recent_projects_changed.emit(self.recent_projects)
    
    def create_project(self, name: str, path: str, 
                       description: str = "", 
                       author: str = "") -> Optional[ProjectConfig]:
        """
        Erstellt ein neues Projekt
        
        Args:
            name: Projektname
            path: Projektverzeichnis
            description: Beschreibung
            author: Autor
            
        Returns:
            ProjectConfig bei Erfolg, None bei Fehler
        """
        project_dir = Path(path)
        
        try:
            # Verzeichnis erstellen
            project_dir.mkdir(parents=True, exist_ok=True)
            
            # Standard-Unterverzeichnisse
            (project_dir / "src").mkdir(exist_ok=True)
            (project_dir / "tests").mkdir(exist_ok=True)
            (project_dir / "resources").mkdir(exist_ok=True)
            
            # Projekt-Konfiguration
            now = datetime.now().isoformat()
            config = ProjectConfig(
                name=name,
                path=str(project_dir),
                created=now,
                last_opened=now,
                main_file="src/main.py",
                description=description,
                author=author
            )
            
            # Projektdatei speichern
            project_file = project_dir / self.PROJECT_FILE
            with open(project_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(config), f, indent=2, ensure_ascii=False)
            
            # Template-Dateien erstellen
            self._create_template_files(project_dir, name)
            
            # Als aktuelles Projekt setzen
            self.current_project = config
            self._add_to_recent(str(project_dir), name)
            
            self.project_created.emit(config)
            self.project_opened.emit(config)
            
            return config
            
        except Exception as e:
            print(f"Fehler beim Erstellen des Projekts: {e}")
            return None
    
    def _create_template_files(self, project_dir: Path, project_name: str):
        """Erstellt Template-Dateien für ein neues Projekt"""
        
        # main.py
        main_content = f'''# -*- coding: utf-8 -*-
"""
{project_name}
Erstellt mit DevCenter
"""

def main():
    print("Hello from {project_name}!")

if __name__ == "__main__":
    main()
'''
        (project_dir / "src" / "main.py").write_text(main_content, encoding='utf-8')
        
        # __init__.py
        (project_dir / "src" / "__init__.py").write_text(
            f'"""{project_name} Package"""\\n',
            encoding='utf-8'
        )
        
        # README.md
        readme_content = f'''# {project_name}

## Beschreibung

[Projektbeschreibung hier einfügen]

## Installation

```bash
pip install -r requirements.txt
```

## Verwendung

```bash
python src/main.py
```

## Lizenz

[Lizenz hier einfügen]
'''
        (project_dir / "README.md").write_text(readme_content, encoding='utf-8')
        
        # requirements.txt
        (project_dir / "requirements.txt").write_text(
            "# Projektabhängigkeiten\\n",
            encoding='utf-8'
        )
    
    def open_project(self, path: str) -> Optional[ProjectConfig]:
        """
        Öffnet ein bestehendes Projekt
        
        Args:
            path: Pfad zum Projektverzeichnis oder zur devcenter.json
            
        Returns:
            ProjectConfig bei Erfolg, None bei Fehler
        """
        project_path = Path(path)
        
        # Wenn Datei übergeben wurde, Verzeichnis verwenden
        if project_path.is_file():
            project_path = project_path.parent
        
        project_file = project_path / self.PROJECT_FILE
        
        if not project_file.exists():
            print(f"Keine Projektdatei gefunden: {project_file}")
            return None
        
        try:
            with open(project_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            config = ProjectConfig(**data)
            config.path = str(project_path)  # Pfad aktualisieren
            config.last_opened = datetime.now().isoformat()
            
            # Aktualisierte Konfiguration speichern
            with open(project_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(config), f, indent=2, ensure_ascii=False)
            
            self.current_project = config
            self._add_to_recent(str(project_path), config.name)
            
            self.project_opened.emit(config)
            
            return config
            
        except Exception as e:
            print(f"Fehler beim Öffnen des Projekts: {e}")
            return None
    
    def close_project(self):
        """Schließt das aktuelle Projekt"""
        if self.current_project:
            self.current_project = None
            self.project_closed.emit()
    
    def save_project(self) -> bool:
        """
        Speichert die aktuelle Projektkonfiguration
        
        Returns:
            True bei Erfolg, False bei Fehler
        """
        if not self.current_project:
            return False
        
        try:
            project_file = Path(self.current_project.path) / self.PROJECT_FILE
            with open(project_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.current_project), f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Fehler beim Speichern: {e}")
            return False
    
    def get_recent_projects(self) -> List[Dict[str, str]]:
        """Gibt die Liste der zuletzt geöffneten Projekte zurück"""
        # Prüfen, ob Projekte noch existieren
        valid_projects = []
        for project in self.recent_projects:
            if Path(project.get('path', '')).exists():
                valid_projects.append(project)
        
        if len(valid_projects) != len(self.recent_projects):
            self.recent_projects = valid_projects
            self._save_recent_projects()
        
        return self.recent_projects
    
    def clear_recent_projects(self):
        """Löscht die Liste der zuletzt geöffneten Projekte"""
        self.recent_projects = []
        self._save_recent_projects()
        self.recent_projects_changed.emit([])


if __name__ == "__main__":
    # Test
    pm = ProjectManager()
    print("Recent Projects:", pm.get_recent_projects())
