# -*- coding: utf-8 -*-
"""
DevCenter - Unit Tests
Testet die Kernkomponenten
"""

import unittest
import sys
import os
import tempfile
import shutil
from pathlib import Path

# Pfad für Imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


class TestProjectManager(unittest.TestCase):
    """Tests für ProjectManager"""
    
    def setUp(self):
        """Erstellt temporäres Verzeichnis"""
        self.temp_dir = tempfile.mkdtemp()
        from core.project_manager import ProjectManager
        self.pm = ProjectManager()
    
    def tearDown(self):
        """Räumt auf"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_create_project(self):
        """Testet Projekt-Erstellung"""
        project = self.pm.create_project(
            name="TestProject",
            path=self.temp_dir
        )
        
        self.assertIsNotNone(project)
        self.assertEqual(project.name, "TestProject")
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, "devcenter.json")))
    
    def test_open_project(self):
        """Testet Projekt-Öffnen"""
        # Erst erstellen
        self.pm.create_project("Test", self.temp_dir)
        
        # Dann öffnen
        project = self.pm.open_project(self.temp_dir)
        
        self.assertIsNotNone(project)
        self.assertEqual(project.name, "Test")
    
    def test_recent_projects(self):
        """Testet Recent-Projects-Liste"""
        self.pm.create_project("Test1", self.temp_dir)
        
        recent = self.pm.get_recent_projects()
        self.assertTrue(len(recent) >= 1)


class TestSettingsManager(unittest.TestCase):
    """Tests für SettingsManager"""
    
    def setUp(self):
        from core.settings_manager import SettingsManager
        self.sm = SettingsManager()
    
    def test_get_default(self):
        """Testet Default-Wert"""
        value = self.sm.get('nonexistent.key', 'default')
        self.assertEqual(value, 'default')
    
    def test_set_and_get(self):
        """Testet Setzen und Lesen"""
        self.sm.set('test.key', 'test_value')
        value = self.sm.get('test.key')
        self.assertEqual(value, 'test_value')
    
    def test_nested_keys(self):
        """Testet verschachtelte Schlüssel"""
        self.sm.set('level1.level2.level3', 42)
        value = self.sm.get('level1.level2.level3')
        self.assertEqual(value, 42)


class TestEventBus(unittest.TestCase):
    """Tests für EventBus"""
    
    def setUp(self):
        from core.event_bus import EventBus, EventType
        self.eb = EventBus()
        self.EventType = EventType
        self.received_events = []
    
    def test_subscribe_and_emit(self):
        """Testet Subscribe und Emit"""
        def handler(event):
            self.received_events.append(event)
        
        self.eb.subscribe(self.EventType.FILE_OPENED, handler)
        self.eb.emit(self.EventType.FILE_OPENED, {'path': 'test.py'})
        
        self.assertEqual(len(self.received_events), 1)
        self.assertEqual(self.received_events[0].data['path'], 'test.py')
    
    def test_unsubscribe(self):
        """Testet Unsubscribe"""
        def handler(event):
            self.received_events.append(event)
        
        self.eb.subscribe(self.EventType.FILE_SAVED, handler)
        self.eb.unsubscribe(self.EventType.FILE_SAVED, handler)
        self.eb.emit(self.EventType.FILE_SAVED, {})
        
        self.assertEqual(len(self.received_events), 0)


class TestMethodAnalyzer(unittest.TestCase):
    """Tests für MethodAnalyzer"""
    
    def setUp(self):
        from modules.analyzer import MethodAnalyzer
        self.analyzer = MethodAnalyzer()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_analyze_simple_file(self):
        """Testet Analyse einer einfachen Datei"""
        code = '''
def hello():
    """Says hello"""
    print("Hello, World!")

class Greeter:
    def greet(self, name):
        return f"Hello, {name}!"
'''
        
        file_path = os.path.join(self.temp_dir, "test.py")
        with open(file_path, 'w') as f:
            f.write(code)
        
        result = self.analyzer.analyze_file(file_path)
        
        self.assertEqual(len(result.functions), 1)
        self.assertEqual(result.functions[0].name, 'hello')
        self.assertEqual(len(result.classes), 1)
        self.assertEqual(result.classes[0].name, 'Greeter')
    
    def test_syntax_error_detection(self):
        """Testet Erkennung von Syntax-Fehlern"""
        code = '''
def broken(:
    pass
'''
        
        file_path = os.path.join(self.temp_dir, "broken.py")
        with open(file_path, 'w') as f:
            f.write(code)
        
        result = self.analyzer.analyze_file(file_path)
        
        self.assertTrue(len(result.errors) > 0)
        self.assertEqual(result.errors[0]['type'], 'SyntaxError')
    
    def test_complexity_calculation(self):
        """Testet Komplexitäts-Berechnung"""
        code = '''
def complex_function(x):
    if x > 0:
        for i in range(x):
            if i % 2 == 0:
                print(i)
            else:
                print(-i)
    else:
        while x < 0:
            x += 1
    return x
'''
        
        file_path = os.path.join(self.temp_dir, "complex.py")
        with open(file_path, 'w') as f:
            f.write(code)
        
        result = self.analyzer.analyze_file(file_path)
        
        self.assertTrue(result.functions[0].complexity > 1)


class TestKompilator(unittest.TestCase):
    """Tests für Kompilator"""
    
    def test_pyinstaller_check(self):
        """Testet PyInstaller-Verfügbarkeit"""
        from modules.builder import Kompilator
        
        kompilator = Kompilator()
        # Sollte nicht abstürzen
        available = kompilator.check_pyinstaller()
        self.assertIsInstance(available, bool)


class TestSyncManager(unittest.TestCase):
    """Tests für SyncManager"""
    
    def setUp(self):
        from modules.filemanager import SyncManager, SyncConfig
        self.sm = SyncManager()
        self.SyncConfig = SyncConfig
        self.source_dir = tempfile.mkdtemp()
        self.target_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        shutil.rmtree(self.source_dir, ignore_errors=True)
        shutil.rmtree(self.target_dir, ignore_errors=True)
    
    def test_sync_files(self):
        """Testet Datei-Synchronisation"""
        # Dateien erstellen
        with open(os.path.join(self.source_dir, "test.txt"), 'w') as f:
            f.write("Hello")
        
        config = self.SyncConfig(
            source_path=self.source_dir,
            target_path=self.target_dir
        )
        
        result = self.sm.sync(config)
        
        self.assertTrue(result.success)
        self.assertEqual(result.files_copied, 1)
        self.assertTrue(os.path.exists(os.path.join(self.target_dir, "test.txt")))
    
    def test_exclude_patterns(self):
        """Testet Ausschluss-Muster"""
        # Dateien erstellen
        with open(os.path.join(self.source_dir, "include.txt"), 'w') as f:
            f.write("Include")
        
        os.makedirs(os.path.join(self.source_dir, "__pycache__"))
        with open(os.path.join(self.source_dir, "__pycache__", "cache.pyc"), 'w') as f:
            f.write("Cache")
        
        config = self.SyncConfig(
            source_path=self.source_dir,
            target_path=self.target_dir,
            excludes=['__pycache__']
        )
        
        result = self.sm.sync(config)
        
        self.assertTrue(result.success)
        self.assertFalse(os.path.exists(os.path.join(self.target_dir, "__pycache__")))


class TestEncodingFixer(unittest.TestCase):
    """Tests für EncodingFixer"""
    
    def setUp(self):
        from modules.analyzer import EncodingFixer
        self.fixer = EncodingFixer()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_detect_utf8(self):
        """Testet UTF-8 Erkennung"""
        file_path = os.path.join(self.temp_dir, "utf8.txt")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("Hello Wörld! 你好")
        
        encoding, confidence = self.fixer.detect_encoding(file_path)
        
        self.assertIn('utf', encoding.lower())
    
    def test_check_file(self):
        """Testet Datei-Prüfung"""
        file_path = os.path.join(self.temp_dir, "test.txt")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("Test content")
        
        result = self.fixer.check_file(file_path)
        
        self.assertTrue(result['is_valid_utf8'])


class TestAIService(unittest.TestCase):
    """Tests für AIService"""
    
    def test_service_without_key(self):
        """Testet Service ohne API-Key"""
        from modules.ai_assistant import AIService
        
        service = AIService(api_key="")
        
        self.assertFalse(service.is_available())
    
    def test_model_setting(self):
        """Testet Modell-Einstellung"""
        from modules.ai_assistant import AIService, AIModel
        
        service = AIService()
        service.set_model(AIModel.CLAUDE_OPUS)
        
        self.assertEqual(service.model, AIModel.CLAUDE_OPUS.value)


class TestProfilerBridge(unittest.TestCase):
    """Tests für ProfilerBridge"""
    
    def setUp(self):
        from modules.filemanager import ProfilerBridge
        self.temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(self.temp_dir, "test_index.db")
        self.bridge = ProfilerBridge(db_path)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_index_file(self):
        """Testet Datei-Indizierung"""
        file_path = os.path.join(self.temp_dir, "test.py")
        with open(file_path, 'w') as f:
            f.write("print('Hello')")
        
        success = self.bridge.index_file(file_path)
        
        self.assertTrue(success)
    
    def test_search(self):
        """Testet Suche"""
        file_path = os.path.join(self.temp_dir, "searchable.py")
        with open(file_path, 'w') as f:
            f.write("def unique_function_name():\n    pass")
        
        self.bridge.index_file(file_path)
        results = self.bridge.search("unique_function_name")
        
        self.assertTrue(len(results) > 0)


if __name__ == "__main__":
    # Verbose Output
    unittest.main(verbosity=2)
