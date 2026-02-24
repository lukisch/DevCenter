# -*- coding: utf-8 -*-
"""
DevCenter - ProFiler Bridge
Datei-Indexierung und Suche
Basierend auf ProFiler V14
"""

import os
import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Generator
from dataclasses import dataclass
import threading


@dataclass
class FileInfo:
    """Informationen über eine indizierte Datei"""
    path: str
    name: str
    extension: str
    size: int
    modified: datetime
    hash: Optional[str] = None
    content_preview: Optional[str] = None


@dataclass
class SearchResult:
    """Suchergebnis"""
    file: FileInfo
    match_type: str  # 'name', 'content', 'path'
    match_context: str = ""
    score: float = 1.0


class ProfilerBridge:
    """
    Verbindung zu ProFiler-artiger Datei-Indexierung
    
    Features:
    - SQLite-basierter Datei-Index
    - Volltext-Suche im Inhalt
    - Hash-basierte Duplikat-Erkennung
    - Inkrementelle Updates
    """
    
    def __init__(self, db_path: str = None):
        """
        Args:
            db_path: Pfad zur Index-Datenbank
        """
        if db_path is None:
            app_data = os.environ.get('APPDATA', os.path.expanduser('~'))
            db_dir = Path(app_data) / 'DevCenter'
            db_dir.mkdir(exist_ok=True)
            db_path = str(db_dir / 'file_index.db')
        
        self.db_path = db_path
        self._lock = threading.Lock()
        self._init_database()
    
    def _init_database(self):
        """Initialisiert die Datenbank"""
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    path TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    extension TEXT,
                    size INTEGER,
                    modified REAL,
                    hash TEXT,
                    content TEXT,
                    indexed_at REAL,
                    project_path TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_name ON files(name)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_extension ON files(extension)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_hash ON files(hash)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_project ON files(project_path)
            ''')
            
            # Volltext-Index
            cursor.execute('''
                CREATE VIRTUAL TABLE IF NOT EXISTS files_fts USING fts5(
                    path, name, content,
                    content='files',
                    content_rowid='id'
                )
            ''')
            
            conn.commit()
            conn.close()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Gibt eine Thread-sichere Verbindung zurück"""
        return sqlite3.connect(self.db_path)
    
    def _calculate_hash(self, file_path: str) -> str:
        """Berechnet MD5-Hash einer Datei"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except:
            return ""
    
    def _read_content_preview(self, file_path: str, max_chars: int = 10000) -> str:
        """Liest Vorschau des Dateiinhalts"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read(max_chars)
        except:
            return ""
    
    def index_file(self, file_path: str, project_path: str = None) -> bool:
        """
        Indiziert eine einzelne Datei
        
        Args:
            file_path: Pfad zur Datei
            project_path: Zugehöriges Projekt
            
        Returns:
            True bei Erfolg
        """
        try:
            path = Path(file_path)
            if not path.exists() or not path.is_file():
                return False
            
            stat = path.stat()
            
            # Nur Text-Dateien indizieren
            text_extensions = {
                '.py', '.txt', '.md', '.json', '.xml', '.html', '.css', '.js',
                '.yml', '.yaml', '.ini', '.cfg', '.conf', '.toml', '.rst',
                '.csv', '.sql', '.sh', '.bat', '.ps1'
            }
            
            content = ""
            file_hash = ""
            
            if path.suffix.lower() in text_extensions:
                content = self._read_content_preview(file_path)
                file_hash = self._calculate_hash(file_path)
            
            with self._lock:
                conn = self._get_connection()
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO files 
                    (path, name, extension, size, modified, hash, content, indexed_at, project_path)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    str(path),
                    path.name,
                    path.suffix.lower(),
                    stat.st_size,
                    stat.st_mtime,
                    file_hash,
                    content,
                    datetime.now().timestamp(),
                    project_path
                ))
                
                # FTS aktualisieren
                cursor.execute('''
                    INSERT OR REPLACE INTO files_fts (rowid, path, name, content)
                    SELECT id, path, name, content FROM files WHERE path = ?
                ''', (str(path),))
                
                conn.commit()
                conn.close()
            
            return True
            
        except Exception as e:
            print(f"Index-Fehler für {file_path}: {e}")
            return False
    
    def index_directory(self, 
                        dir_path: str, 
                        project_path: str = None,
                        recursive: bool = True,
                        progress_callback = None) -> int:
        """
        Indiziert alle Dateien in einem Verzeichnis
        
        Args:
            dir_path: Pfad zum Verzeichnis
            project_path: Zugehöriges Projekt
            recursive: Auch Unterverzeichnisse
            progress_callback: Callback(current, total, file)
            
        Returns:
            Anzahl indizierter Dateien
        """
        path = Path(dir_path)
        if not path.exists():
            return 0
        
        if project_path is None:
            project_path = str(path)
        
        # Dateien sammeln
        if recursive:
            files = list(path.rglob('*'))
        else:
            files = list(path.glob('*'))
        
        files = [f for f in files if f.is_file()]
        
        # Ausschlüsse
        excludes = {'__pycache__', '.git', 'node_modules', 'venv', '.venv', 'dist', 'build'}
        files = [f for f in files if not any(e in str(f) for e in excludes)]
        
        total = len(files)
        indexed = 0
        
        for i, file in enumerate(files):
            if progress_callback:
                progress_callback(i + 1, total, str(file))
            
            if self.index_file(str(file), project_path):
                indexed += 1
        
        return indexed
    
    def search(self, 
               query: str, 
               project_path: str = None,
               search_content: bool = True,
               limit: int = 50) -> List[SearchResult]:
        """
        Sucht im Index
        
        Args:
            query: Suchbegriff
            project_path: Nur in diesem Projekt suchen
            search_content: Auch im Inhalt suchen
            limit: Maximale Ergebnisse
            
        Returns:
            Liste von SearchResults
        """
        results = []
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Name/Pfad-Suche
            sql = '''
                SELECT path, name, extension, size, modified, hash
                FROM files
                WHERE (name LIKE ? OR path LIKE ?)
            '''
            params = [f'%{query}%', f'%{query}%']
            
            if project_path:
                sql += ' AND project_path = ?'
                params.append(project_path)
            
            sql += f' LIMIT {limit}'
            
            cursor.execute(sql, params)
            
            for row in cursor.fetchall():
                file_info = FileInfo(
                    path=row[0],
                    name=row[1],
                    extension=row[2],
                    size=row[3],
                    modified=datetime.fromtimestamp(row[4]) if row[4] else None,
                    hash=row[5]
                )
                results.append(SearchResult(
                    file=file_info,
                    match_type='name' if query.lower() in row[1].lower() else 'path'
                ))
            
            # Volltext-Suche
            if search_content and len(results) < limit:
                remaining = limit - len(results)
                found_paths = {r.file.path for r in results}
                
                cursor.execute(f'''
                    SELECT f.path, f.name, f.extension, f.size, f.modified, f.hash,
                           snippet(files_fts, 2, '>>>', '<<<', '...', 32) as context
                    FROM files_fts fts
                    JOIN files f ON f.id = fts.rowid
                    WHERE files_fts MATCH ?
                    LIMIT {remaining}
                ''', (query,))
                
                for row in cursor.fetchall():
                    if row[0] not in found_paths:
                        file_info = FileInfo(
                            path=row[0],
                            name=row[1],
                            extension=row[2],
                            size=row[3],
                            modified=datetime.fromtimestamp(row[4]) if row[4] else None,
                            hash=row[5]
                        )
                        results.append(SearchResult(
                            file=file_info,
                            match_type='content',
                            match_context=row[6] if row[6] else ""
                        ))
            
            conn.close()
            
        except Exception as e:
            print(f"Such-Fehler: {e}")
        
        return results
    
    def find_duplicates(self, project_path: str = None) -> Dict[str, List[str]]:
        """
        Findet Duplikate basierend auf Hash
        
        Args:
            project_path: Nur in diesem Projekt
            
        Returns:
            Dict mit Hash -> Liste von Pfaden
        """
        duplicates = {}
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            sql = '''
                SELECT hash, GROUP_CONCAT(path, '|||') as paths
                FROM files
                WHERE hash IS NOT NULL AND hash != ''
            '''
            
            if project_path:
                sql += f" AND project_path = '{project_path}'"
            
            sql += ' GROUP BY hash HAVING COUNT(*) > 1'
            
            cursor.execute(sql)
            
            for row in cursor.fetchall():
                duplicates[row[0]] = row[1].split('|||')
            
            conn.close()
            
        except Exception as e:
            print(f"Duplikat-Suche Fehler: {e}")
        
        return duplicates
    
    def get_statistics(self, project_path: str = None) -> Dict:
        """
        Gibt Index-Statistiken zurück
        
        Args:
            project_path: Nur für dieses Projekt
            
        Returns:
            Dict mit Statistiken
        """
        stats = {
            'total_files': 0,
            'total_size': 0,
            'by_extension': {},
            'last_indexed': None
        }
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            where = f"WHERE project_path = '{project_path}'" if project_path else ""
            
            # Gesamt
            cursor.execute(f'SELECT COUNT(*), SUM(size) FROM files {where}')
            row = cursor.fetchone()
            stats['total_files'] = row[0] or 0
            stats['total_size'] = row[1] or 0
            
            # Nach Extension
            cursor.execute(f'''
                SELECT extension, COUNT(*), SUM(size)
                FROM files {where}
                GROUP BY extension
                ORDER BY COUNT(*) DESC
            ''')
            
            for row in cursor.fetchall():
                stats['by_extension'][row[0] or '(keine)'] = {
                    'count': row[1],
                    'size': row[2] or 0
                }
            
            # Letzter Index
            cursor.execute(f'SELECT MAX(indexed_at) FROM files {where}')
            row = cursor.fetchone()
            if row[0]:
                stats['last_indexed'] = datetime.fromtimestamp(row[0])
            
            conn.close()
            
        except Exception as e:
            print(f"Statistik-Fehler: {e}")
        
        return stats
    
    def clear_index(self, project_path: str = None):
        """
        Löscht den Index
        
        Args:
            project_path: Nur für dieses Projekt (sonst alles)
        """
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            if project_path:
                cursor.execute('DELETE FROM files WHERE project_path = ?', (project_path,))
            else:
                cursor.execute('DELETE FROM files')
            
            # FTS rebuilden
            cursor.execute('INSERT INTO files_fts(files_fts) VALUES("rebuild")')
            
            conn.commit()
            conn.close()


if __name__ == "__main__":
    # Test
    bridge = ProfilerBridge()
    
    # Index testen
    indexed = bridge.index_directory(".", recursive=False)
    print(f"Indiziert: {indexed} Dateien")
    
    # Suche testen
    results = bridge.search("def ")
    print(f"Gefunden: {len(results)} Ergebnisse")
    for r in results[:5]:
        print(f"  - {r.file.name} ({r.match_type})")
    
    # Statistiken
    stats = bridge.get_statistics()
    print(f"Statistiken: {stats['total_files']} Dateien, {stats['total_size']} Bytes")
