# -*- coding: utf-8 -*-
"""
DevCenter - Encoding Fixer
Repariert Encoding-Probleme in Dateien
Basierend auf EncodingFixer mit ftfy
"""

import os
from pathlib import Path
from typing import Optional, Tuple, List
import chardet


class EncodingFixer:
    """
    Erkennt und repariert Encoding-Probleme
    
    Verwendet:
    - chardet für Encoding-Erkennung
    - ftfy für Text-Reparatur (optional)
    """
    
    COMMON_ENCODINGS = [
        'utf-8',
        'utf-8-sig',
        'latin-1',
        'iso-8859-1',
        'cp1252',
        'ascii'
    ]
    
    def __init__(self):
        self._ftfy_available = False
        try:
            import ftfy
            self._ftfy_available = True
        except ImportError:
            pass
    
    def detect_encoding(self, file_path: str) -> Tuple[str, float]:
        """
        Erkennt das Encoding einer Datei
        
        Args:
            file_path: Pfad zur Datei
            
        Returns:
            Tuple (encoding, confidence)
        """
        with open(file_path, 'rb') as f:
            raw_data = f.read()
        
        result = chardet.detect(raw_data)
        return result.get('encoding', 'utf-8'), result.get('confidence', 0.0)
    
    def fix_file(self, file_path: str, 
                 target_encoding: str = 'utf-8',
                 backup: bool = True) -> Tuple[bool, str]:
        """
        Repariert das Encoding einer Datei
        
        Args:
            file_path: Pfad zur Datei
            target_encoding: Ziel-Encoding
            backup: Backup erstellen
            
        Returns:
            Tuple (success, message)
        """
        try:
            # Encoding erkennen
            source_encoding, confidence = self.detect_encoding(file_path)
            
            if not source_encoding:
                return False, "Encoding konnte nicht erkannt werden"
            
            # Datei lesen
            with open(file_path, 'r', encoding=source_encoding, errors='replace') as f:
                content = f.read()
            
            # Mit ftfy reparieren wenn verfügbar
            if self._ftfy_available:
                import ftfy
                content = ftfy.fix_text(content)
            
            # Backup erstellen
            if backup:
                backup_path = file_path + '.bak'
                with open(file_path, 'rb') as f:
                    original = f.read()
                with open(backup_path, 'wb') as f:
                    f.write(original)
            
            # Mit neuem Encoding speichern
            with open(file_path, 'w', encoding=target_encoding) as f:
                f.write(content)
            
            return True, f"Konvertiert: {source_encoding} → {target_encoding}"
            
        except Exception as e:
            return False, f"Fehler: {str(e)}"
    
    def check_file(self, file_path: str) -> dict:
        """
        Prüft eine Datei auf Encoding-Probleme
        
        Args:
            file_path: Pfad zur Datei
            
        Returns:
            Dict mit Analyseergebnis
        """
        result = {
            'path': file_path,
            'encoding': None,
            'confidence': 0.0,
            'is_valid_utf8': False,
            'has_bom': False,
            'issues': []
        }
        
        try:
            # Encoding erkennen
            encoding, confidence = self.detect_encoding(file_path)
            result['encoding'] = encoding
            result['confidence'] = confidence
            
            # Als UTF-8 prüfen
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    f.read()
                result['is_valid_utf8'] = True
            except UnicodeDecodeError:
                result['issues'].append("Datei ist nicht valides UTF-8")
            
            # BOM prüfen
            with open(file_path, 'rb') as f:
                header = f.read(3)
            if header.startswith(b'\xef\xbb\xbf'):
                result['has_bom'] = True
                result['issues'].append("Datei hat UTF-8 BOM")
            
            # Niedrige Confidence
            if confidence < 0.8:
                result['issues'].append(f"Niedrige Encoding-Confidence: {confidence:.0%}")
            
        except Exception as e:
            result['issues'].append(f"Fehler: {str(e)}")
        
        return result
    
    def check_directory(self, dir_path: str, 
                        extensions: List[str] = None) -> List[dict]:
        """
        Prüft alle Dateien in einem Verzeichnis
        
        Args:
            dir_path: Pfad zum Verzeichnis
            extensions: Zu prüfende Dateiendungen
            
        Returns:
            Liste von Prüfergebnissen
        """
        if extensions is None:
            extensions = ['.py', '.txt', '.md', '.json', '.xml', '.html']
        
        results = []
        path = Path(dir_path)
        
        for file_path in path.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in extensions:
                results.append(self.check_file(str(file_path)))
        
        return results


if __name__ == "__main__":
    import sys
    
    fixer = EncodingFixer()
    
    if len(sys.argv) > 1:
        result = fixer.check_file(sys.argv[1])
        print(f"Datei: {result['path']}")
        print(f"Encoding: {result['encoding']} ({result['confidence']:.0%})")
        print(f"Valid UTF-8: {result['is_valid_utf8']}")
        if result['issues']:
            print("Issues:")
            for issue in result['issues']:
                print(f"  - {issue}")
