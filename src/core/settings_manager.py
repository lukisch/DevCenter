# -*- coding: utf-8 -*-
"""
DevCenter - Settings Manager
Zentrale Einstellungsverwaltung
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, asdict, field
from PyQt6.QtCore import QObject, pyqtSignal


@dataclass
class EditorSettings:
    """Editor-Einstellungen"""
    font_family: str = "Consolas"
    font_size: int = 11
    tab_size: int = 4
    use_spaces: bool = True
    show_line_numbers: bool = True
    show_whitespace: bool = False
    word_wrap: bool = False
    auto_indent: bool = True
    highlight_current_line: bool = True
    auto_complete: bool = True
    auto_save: bool = False
    auto_save_interval: int = 60  # Sekunden


@dataclass  
class BuildSettings:
    """Build-Einstellungen"""
    pyinstaller_path: str = ""
    default_output_dir: str = "dist"
    one_file: bool = True
    console_mode: bool = True
    upx_enabled: bool = False
    upx_path: str = ""
    clean_build: bool = True
    include_licenses: bool = True


@dataclass
class AISettings:
    """AI-Einstellungen"""
    api_key: str = ""  # Wird verschlüsselt gespeichert
    model: str = "claude-sonnet-4-20250514"
    max_tokens: int = 4096
    temperature: float = 0.7
    enabled: bool = True


@dataclass
class SyncSettings:
    """Sync-Einstellungen"""
    enabled: bool = False
    backup_path: str = ""
    auto_backup: bool = False
    backup_interval: int = 300  # Sekunden
    excludes: list = field(default_factory=lambda: [
        "__pycache__", ".git", "dist", "build", "*.pyc", "*.pyo"
    ])


@dataclass
class AppearanceSettings:
    """Erscheinungsbild-Einstellungen"""
    theme: str = "dark"  # dark, light, system
    accent_color: str = "#3498db"
    editor_theme: str = "monokai"
    show_toolbar: bool = True
    show_statusbar: bool = True
    compact_mode: bool = False


@dataclass
class AppSettings:
    """Gesamte Anwendungseinstellungen"""
    editor: EditorSettings = field(default_factory=EditorSettings)
    build: BuildSettings = field(default_factory=BuildSettings)
    ai: AISettings = field(default_factory=AISettings)
    sync: SyncSettings = field(default_factory=SyncSettings)
    appearance: AppearanceSettings = field(default_factory=AppearanceSettings)
    
    # Allgemeine Einstellungen
    language: str = "de"
    check_updates: bool = True
    telemetry_enabled: bool = False
    window_state: Dict[str, Any] = field(default_factory=dict)


class SettingsManager(QObject):
    """
    Zentrale Einstellungsverwaltung für DevCenter
    
    Signals:
        settings_changed: Eine Einstellung hat sich geändert (key, value)
        theme_changed: Theme wurde geändert (theme_name)
    """
    
    settings_changed = pyqtSignal(str, object)
    theme_changed = pyqtSignal(str)
    
    def __init__(self, settings_path: str = None):
        super().__init__()
        self.settings_path = settings_path or self._default_settings_path()
        self.settings = AppSettings()
        self._load()
    
    def _default_settings_path(self) -> str:
        """Standardpfad für Einstellungen"""
        app_data = os.environ.get('APPDATA', os.path.expanduser('~'))
        settings_dir = Path(app_data) / 'DevCenter'
        settings_dir.mkdir(exist_ok=True)
        return str(settings_dir / 'settings.json')
    
    def _load(self):
        """Lädt Einstellungen aus Datei"""
        settings_file = Path(self.settings_path)
        
        if not settings_file.exists():
            self._save()  # Standardeinstellungen speichern
            return
        
        try:
            with open(settings_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Einstellungen rekonstruieren
            if 'editor' in data:
                self.settings.editor = EditorSettings(**data['editor'])
            if 'build' in data:
                self.settings.build = BuildSettings(**data['build'])
            if 'ai' in data:
                self.settings.ai = AISettings(**data['ai'])
            if 'sync' in data:
                self.settings.sync = SyncSettings(**data['sync'])
            if 'appearance' in data:
                self.settings.appearance = AppearanceSettings(**data['appearance'])
            
            # Allgemeine Einstellungen
            self.settings.language = data.get('language', 'de')
            self.settings.check_updates = data.get('check_updates', True)
            self.settings.telemetry_enabled = data.get('telemetry_enabled', False)
            self.settings.window_state = data.get('window_state', {})
            
        except Exception as e:
            print(f"Fehler beim Laden der Einstellungen: {e}")
            self.settings = AppSettings()
    
    def _save(self):
        """Speichert Einstellungen in Datei"""
        settings_file = Path(self.settings_path)
        settings_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            data = {
                'editor': asdict(self.settings.editor),
                'build': asdict(self.settings.build),
                'ai': asdict(self.settings.ai),
                'sync': asdict(self.settings.sync),
                'appearance': asdict(self.settings.appearance),
                'language': self.settings.language,
                'check_updates': self.settings.check_updates,
                'telemetry_enabled': self.settings.telemetry_enabled,
                'window_state': self.settings.window_state
            }
            
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Fehler beim Speichern der Einstellungen: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Holt einen Einstellungswert
        
        Args:
            key: Punktnotation z.B. "editor.font_size"
            default: Standardwert wenn nicht gefunden
            
        Returns:
            Einstellungswert oder default
        """
        parts = key.split('.')
        obj = self.settings
        
        try:
            for part in parts:
                if hasattr(obj, part):
                    obj = getattr(obj, part)
                elif isinstance(obj, dict):
                    obj = obj.get(part, default)
                else:
                    return default
            return obj
        except:
            return default
    
    def set(self, key: str, value: Any, save: bool = True):
        """
        Setzt einen Einstellungswert
        
        Args:
            key: Punktnotation z.B. "editor.font_size"
            value: Neuer Wert
            save: Sofort speichern
        """
        parts = key.split('.')
        obj = self.settings
        
        try:
            # Navigiere zum Elternobjekt
            for part in parts[:-1]:
                if hasattr(obj, part):
                    obj = getattr(obj, part)
                else:
                    return
            
            # Wert setzen
            final_key = parts[-1]
            if hasattr(obj, final_key):
                setattr(obj, final_key, value)
                
                if save:
                    self._save()
                
                self.settings_changed.emit(key, value)
                
                # Spezielle Signale
                if key.startswith('appearance.theme'):
                    self.theme_changed.emit(value)
                    
        except Exception as e:
            print(f"Fehler beim Setzen von {key}: {e}")
    
    def reset_to_defaults(self, category: str = None):
        """
        Setzt Einstellungen auf Standard zurück
        
        Args:
            category: Optional - nur diese Kategorie zurücksetzen
        """
        if category is None:
            self.settings = AppSettings()
        elif category == 'editor':
            self.settings.editor = EditorSettings()
        elif category == 'build':
            self.settings.build = BuildSettings()
        elif category == 'ai':
            self.settings.ai = AISettings()
        elif category == 'sync':
            self.settings.sync = SyncSettings()
        elif category == 'appearance':
            self.settings.appearance = AppearanceSettings()
        
        self._save()
        self.settings_changed.emit('*', None)
    
    def export_settings(self, path: str) -> bool:
        """Exportiert Einstellungen in eine Datei"""
        try:
            data = {
                'editor': asdict(self.settings.editor),
                'build': asdict(self.settings.build),
                'ai': asdict(self.settings.ai),
                'sync': asdict(self.settings.sync),
                'appearance': asdict(self.settings.appearance),
                'language': self.settings.language,
                'check_updates': self.settings.check_updates
            }
            
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Export-Fehler: {e}")
            return False
    
    def import_settings(self, path: str) -> bool:
        """Importiert Einstellungen aus einer Datei"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Einstellungen übernehmen
            if 'editor' in data:
                self.settings.editor = EditorSettings(**data['editor'])
            if 'build' in data:
                self.settings.build = BuildSettings(**data['build'])
            if 'ai' in data:
                self.settings.ai = AISettings(**data['ai'])
            if 'sync' in data:
                self.settings.sync = SyncSettings(**data['sync'])
            if 'appearance' in data:
                self.settings.appearance = AppearanceSettings(**data['appearance'])
            
            self._save()
            self.settings_changed.emit('*', None)
            return True
        except Exception as e:
            print(f"Import-Fehler: {e}")
            return False
    
    def save_window_state(self, geometry: bytes, state: bytes):
        """Speichert Fensterzustand"""
        self.settings.window_state = {
            'geometry': geometry.hex() if geometry else '',
            'state': state.hex() if state else ''
        }
        self._save()
    
    def restore_window_state(self) -> tuple:
        """Stellt Fensterzustand wieder her"""
        ws = self.settings.window_state
        geometry = bytes.fromhex(ws.get('geometry', '')) if ws.get('geometry') else None
        state = bytes.fromhex(ws.get('state', '')) if ws.get('state') else None
        return geometry, state


# Singleton-Instance
_instance: Optional[SettingsManager] = None

def get_settings() -> SettingsManager:
    """Gibt die globale Settings-Instanz zurück"""
    global _instance
    if _instance is None:
        _instance = SettingsManager()
    return _instance


if __name__ == "__main__":
    # Test
    sm = SettingsManager()
    print(f"Font Size: {sm.get('editor.font_size')}")
    print(f"Theme: {sm.get('appearance.theme')}")
