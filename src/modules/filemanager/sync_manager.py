# -*- coding: utf-8 -*-
"""
DevCenter - Sync Manager
Automatische Backups mit DB-sicherer Synchronisation
Basierend auf ProSync V3.1
"""

import os
import shutil
import sqlite3
import hashlib
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Callable, Set
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor
import fnmatch


@dataclass
class SyncConfig:
    """Sync-Konfiguration"""
    source_path: str
    target_path: str
    
    # Ausschlüsse
    excludes: List[str] = field(default_factory=lambda: [
        '__pycache__',
        '.git',
        '.svn',
        'dist',
        'build',
        '*.pyc',
        '*.pyo',
        '*.egg-info',
        '.eggs',
        'venv',
        '.venv',
        'env',
        '.env',
        'node_modules',
        '.idea',
        '.vscode',
        '*.log',
        '*.tmp',
        '*.bak',
        'Thumbs.db',
        '.DS_Store'
    ])
    
    # Optionen
    delete_orphans: bool = False  # Dateien im Ziel löschen die nicht in Quelle
    preserve_newer: bool = True   # Neuere Ziel-Dateien nicht überschreiben
    verify_copy: bool = True      # Hash nach Kopieren prüfen
    
    # SQLite-Spezial
    checkpoint_sqlite: bool = True  # WAL Checkpoint vor Sync


@dataclass
class SyncResult:
    """Ergebnis eines Sync-Vorgangs"""
    success: bool
    files_copied: int = 0
    files_skipped: int = 0
    files_deleted: int = 0
    bytes_copied: int = 0
    errors: List[str] = field(default_factory=list)
    duration: float = 0.0


class SyncManager:
    """
    Intelligente Datei-Synchronisation
    
    Features:
    - WAL Checkpoint für SQLite-Datenbanken
    - Musterbasierte Ausschlüsse
    - Verifizierung nach Kopieren
    - Fortschritts-Callbacks
    """
    
    def __init__(self):
        self.progress_callback: Optional[Callable[[int, str], None]] = None
        self._cancelled = False
    
    def set_progress_callback(self, callback: Callable[[int, str], None]):
        """Setzt Callback für Fortschrittsupdates (progress%, message)"""
        self.progress_callback = callback
    
    def cancel(self):
        """Bricht den aktuellen Sync ab"""
        self._cancelled = True
    
    def _emit_progress(self, progress: int, message: str):
        if self.progress_callback:
            self.progress_callback(progress, message)
    
    def _should_exclude(self, path: str, excludes: List[str]) -> bool:
        """Prüft ob ein Pfad ausgeschlossen werden soll"""
        name = os.path.basename(path)
        
        for pattern in excludes:
            # Direkter Match
            if fnmatch.fnmatch(name, pattern):
                return True
            # Pfad-Match
            if fnmatch.fnmatch(path, pattern):
                return True
            # Verzeichnis im Pfad
            if pattern in path.split(os.sep):
                return True
        
        return False
    
    def _get_file_hash(self, file_path: str) -> str:
        """Berechnet MD5-Hash einer Datei"""
        hash_md5 = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def _checkpoint_sqlite_db(self, db_path: str) -> bool:
        """
        Führt WAL Checkpoint für SQLite-Datenbank durch
        
        Wichtig für konsistente Backups von SQLite-DBs!
        """
        try:
            conn = sqlite3.connect(db_path)
            conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
            conn.close()
            return True
        except Exception as e:
            print(f"SQLite Checkpoint fehlgeschlagen für {db_path}: {e}")
            return False
    
    def _find_sqlite_databases(self, directory: str) -> List[str]:
        """Findet alle SQLite-Datenbanken in einem Verzeichnis"""
        db_files = []
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(('.db', '.sqlite', '.sqlite3')):
                    db_files.append(os.path.join(root, file))
        
        return db_files
    
    def sync(self, config: SyncConfig) -> SyncResult:
        """
        Führt die Synchronisation durch
        
        Args:
            config: Sync-Konfiguration
            
        Returns:
            SyncResult mit Statistiken
        """
        start_time = datetime.now()
        self._cancelled = False
        
        result = SyncResult(success=True)
        
        source = Path(config.source_path)
        target = Path(config.target_path)
        
        # Prüfungen
        if not source.exists():
            result.success = False
            result.errors.append(f"Quellverzeichnis existiert nicht: {source}")
            return result
        
        # Zielverzeichnis erstellen
        target.mkdir(parents=True, exist_ok=True)
        
        # SQLite Checkpoint
        if config.checkpoint_sqlite:
            self._emit_progress(5, "SQLite-Datenbanken werden vorbereitet...")
            db_files = self._find_sqlite_databases(str(source))
            for db_file in db_files:
                self._checkpoint_sqlite_db(db_file)
        
        # Dateien sammeln
        self._emit_progress(10, "Dateien werden analysiert...")
        
        source_files: Set[str] = set()
        
        for root, dirs, files in os.walk(source):
            # Ausgeschlossene Verzeichnisse überspringen
            dirs[:] = [d for d in dirs if not self._should_exclude(
                os.path.join(root, d), config.excludes
            )]
            
            for file in files:
                if self._cancelled:
                    result.success = False
                    result.errors.append("Sync abgebrochen")
                    return result
                
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, source)
                
                if self._should_exclude(full_path, config.excludes):
                    result.files_skipped += 1
                    continue
                
                source_files.add(rel_path)
        
        total_files = len(source_files)
        processed = 0
        
        # Dateien kopieren
        for rel_path in source_files:
            if self._cancelled:
                break
            
            processed += 1
            progress = 10 + int((processed / total_files) * 80)
            
            source_file = source / rel_path
            target_file = target / rel_path
            
            self._emit_progress(progress, f"Kopiere: {rel_path}")
            
            try:
                # Zielverzeichnis erstellen
                target_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Prüfen ob Kopieren nötig
                should_copy = True
                
                if target_file.exists():
                    source_mtime = source_file.stat().st_mtime
                    target_mtime = target_file.stat().st_mtime
                    source_size = source_file.stat().st_size
                    target_size = target_file.stat().st_size
                    
                    # Gleiche Größe und Änderungszeit
                    if source_size == target_size and abs(source_mtime - target_mtime) < 1:
                        should_copy = False
                        result.files_skipped += 1
                    
                    # Neuere Zieldatei erhalten
                    elif config.preserve_newer and target_mtime > source_mtime:
                        should_copy = False
                        result.files_skipped += 1
                
                if should_copy:
                    shutil.copy2(str(source_file), str(target_file))
                    result.files_copied += 1
                    result.bytes_copied += source_file.stat().st_size
                    
                    # Verifizieren
                    if config.verify_copy:
                        source_hash = self._get_file_hash(str(source_file))
                        target_hash = self._get_file_hash(str(target_file))
                        
                        if source_hash != target_hash:
                            result.errors.append(f"Verifikation fehlgeschlagen: {rel_path}")
                
            except Exception as e:
                result.errors.append(f"Fehler bei {rel_path}: {e}")
        
        # Verwaiste Dateien löschen
        if config.delete_orphans and not self._cancelled:
            self._emit_progress(95, "Verwaiste Dateien werden entfernt...")
            
            for root, dirs, files in os.walk(target):
                for file in files:
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, target)
                    
                    if rel_path not in source_files:
                        try:
                            os.remove(full_path)
                            result.files_deleted += 1
                        except Exception as e:
                            result.errors.append(f"Löschen fehlgeschlagen: {rel_path}")
        
        # Abschluss
        result.duration = (datetime.now() - start_time).total_seconds()
        result.success = len(result.errors) == 0
        
        self._emit_progress(100, f"Sync abgeschlossen: {result.files_copied} Dateien kopiert")
        
        return result
    
    def backup_project(self, 
                       project_path: str, 
                       backup_base: str,
                       project_name: str = None) -> SyncResult:
        """
        Erstellt ein Projekt-Backup
        
        Args:
            project_path: Pfad zum Projekt
            backup_base: Basis-Verzeichnis für Backups
            project_name: Name für Backup-Ordner
            
        Returns:
            SyncResult
        """
        if project_name is None:
            project_name = os.path.basename(project_path)
        
        # Zeitstempel für Backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_base, f"{project_name}_{timestamp}")
        
        config = SyncConfig(
            source_path=project_path,
            target_path=backup_path,
            checkpoint_sqlite=True,
            verify_copy=True
        )
        
        return self.sync(config)
    
    def restore_backup(self, 
                       backup_path: str, 
                       target_path: str,
                       overwrite: bool = False) -> SyncResult:
        """
        Stellt ein Backup wieder her
        
        Args:
            backup_path: Pfad zum Backup
            target_path: Ziel für Wiederherstellung
            overwrite: Existierende Dateien überschreiben
            
        Returns:
            SyncResult
        """
        config = SyncConfig(
            source_path=backup_path,
            target_path=target_path,
            preserve_newer=not overwrite,
            delete_orphans=False
        )
        
        return self.sync(config)


class BackupScheduler:
    """
    Automatische Backup-Planung
    """
    
    def __init__(self, sync_manager: SyncManager):
        self.sync_manager = sync_manager
        self.backup_configs: List[Dict] = []
        self._timer = None
    
    def add_backup(self, 
                   project_path: str, 
                   backup_path: str,
                   interval_minutes: int = 60):
        """Fügt ein automatisches Backup hinzu"""
        self.backup_configs.append({
            'project': project_path,
            'backup': backup_path,
            'interval': interval_minutes,
            'last_run': None
        })
    
    def remove_backup(self, project_path: str):
        """Entfernt ein automatisches Backup"""
        self.backup_configs = [
            c for c in self.backup_configs 
            if c['project'] != project_path
        ]
    
    def check_and_run(self):
        """Prüft und führt fällige Backups aus"""
        now = datetime.now()
        
        for config in self.backup_configs:
            if config['last_run'] is None:
                should_run = True
            else:
                elapsed = (now - config['last_run']).total_seconds() / 60
                should_run = elapsed >= config['interval']
            
            if should_run:
                result = self.sync_manager.backup_project(
                    config['project'],
                    config['backup']
                )
                config['last_run'] = now
                
                if not result.success:
                    print(f"Backup-Fehler für {config['project']}: {result.errors}")


if __name__ == "__main__":
    # Test
    manager = SyncManager()
    
    def progress(p, msg):
        print(f"[{p}%] {msg}")
    
    manager.set_progress_callback(progress)
    
    # Test-Sync
    config = SyncConfig(
        source_path=".",
        target_path="./test_backup"
    )
    
    # result = manager.sync(config)
    # print(f"Erfolg: {result.success}")
    # print(f"Kopiert: {result.files_copied}")
    # print(f"Übersprungen: {result.files_skipped}")
