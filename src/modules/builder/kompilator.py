# -*- coding: utf-8 -*-
"""
DevCenter - Kompilator
Python zu EXE Konvertierung mit PyInstaller
Basierend auf UltimateKompilator V3.1
"""

import os
import sys
import subprocess
import shutil
import json
from pathlib import Path
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class BuildConfig:
    """Build-Konfiguration"""
    script_path: str
    output_dir: str = "dist"
    
    # Allgemein
    name: Optional[str] = None
    one_file: bool = True
    console: bool = True
    icon: Optional[str] = None
    
    # Erweitert
    hidden_imports: List[str] = None
    exclude_modules: List[str] = None
    data_files: List[tuple] = None
    binary_files: List[tuple] = None
    
    # Optimierung
    upx: bool = False
    upx_dir: Optional[str] = None
    strip: bool = False
    clean: bool = True
    
    # Metadaten
    version: Optional[str] = None
    company: Optional[str] = None
    copyright: Optional[str] = None
    description: Optional[str] = None
    
    def __post_init__(self):
        """Initialisiert Standardwerte für Listen und optionalen Namen."""
        if self.hidden_imports is None:
            self.hidden_imports = []
        if self.exclude_modules is None:
            self.exclude_modules = []
        if self.data_files is None:
            self.data_files = []
        if self.binary_files is None:
            self.binary_files = []
        if self.name is None:
            self.name = Path(self.script_path).stem


@dataclass
class BuildResult:
    """Ergebnis eines Build-Vorgangs"""
    success: bool
    output_path: Optional[str] = None
    error_message: Optional[str] = None
    duration: float = 0.0
    log: List[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        """Initialisiert leere Listen für Logs und Warnungen."""
        if self.log is None:
            self.log = []
        if self.warnings is None:
            self.warnings = []


class Kompilator:
    """
    Python zu EXE Compiler
    
    Verwendet PyInstaller um Python-Skripte in
    ausführbare Dateien zu konvertieren.
    """
    
    def __init__(self, pyinstaller_path: str = None):
        """
        Args:
            pyinstaller_path: Optionaler Pfad zu PyInstaller
        """
        self.pyinstaller_path = pyinstaller_path
        self._progress_callback: Optional[Callable] = None
        self._log: List[str] = []
    
    def set_progress_callback(self, callback: Callable[[int, str], None]):
        """Setzt eine Callback-Funktion für Fortschrittsupdates"""
        self._progress_callback = callback
    
    def _emit_progress(self, progress: int, message: str):
        """Sendet ein Fortschrittsupdate"""
        self._log.append(message)
        if self._progress_callback:
            self._progress_callback(progress, message)
    
    def check_pyinstaller(self) -> bool:
        """
        Prüft ob PyInstaller im aktuellen Environment verfügbar ist.
        
        Returns:
            bool: True wenn PyInstaller gefunden wurde, sonst False.
        """
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'PyInstaller', '--version'],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def get_pyinstaller_version(self) -> Optional[str]:
        """Gibt die PyInstaller-Version zurück"""
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'PyInstaller', '--version'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None
    
    def build(self, config: BuildConfig) -> BuildResult:
        """
        Führt den Build-Prozess durch
        
        Args:
            config: Build-Konfiguration
            
        Returns:
            BuildResult mit Ergebnis
        """
        start_time = datetime.now()
        self._log = []
        
        # Prüfungen
        if not os.path.exists(config.script_path):
            return BuildResult(
                success=False,
                error_message=f"Skript nicht gefunden: {config.script_path}"
            )
        
        if not self.check_pyinstaller():
            return BuildResult(
                success=False,
                error_message="PyInstaller nicht installiert. Installieren mit: pip install pyinstaller"
            )
        
        self._emit_progress(5, "Build wird vorbereitet...")
        
        # Ausgabeverzeichnis erstellen
        output_dir = Path(config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Clean Build
        if config.clean:
            self._emit_progress(10, "Vorherige Build-Artefakte werden entfernt...")
            self._clean_build(config)
        
        # PyInstaller-Kommando zusammenstellen
        cmd = self._build_command(config)
        self._emit_progress(15, f"Starte PyInstaller...")
        self._log.append(f"Kommando: {' '.join(cmd)}")
        
        # PyInstaller ausführen
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=os.path.dirname(config.script_path) or '.'
            )
            
            progress = 20
            warnings = []
            
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                
                line = line.strip()
                if line:
                    self._log.append(line)
                    
                    # Fortschritt schätzen
                    if "Analyzing" in line:
                        progress = min(progress + 5, 40)
                    elif "Processing" in line:
                        progress = min(progress + 2, 60)
                    elif "Building" in line:
                        progress = min(progress + 10, 80)
                    elif "Copying" in line:
                        progress = min(progress + 5, 90)
                    
                    # Warnungen sammeln
                    if "WARNING" in line:
                        warnings.append(line)
                    
                    self._emit_progress(progress, line[:100])
            
            return_code = process.returncode
            
        except Exception as e:
            return BuildResult(
                success=False,
                error_message=f"Fehler beim Ausführen von PyInstaller: {e}",
                log=self._log
            )
        
        # Ergebnis prüfen
        duration = (datetime.now() - start_time).total_seconds()
        
        if return_code != 0:
            return BuildResult(
                success=False,
                error_message="PyInstaller Build fehlgeschlagen",
                duration=duration,
                log=self._log,
                warnings=warnings
            )
        
        # Output-Pfad ermitteln
        if config.one_file:
            exe_name = f"{config.name}.exe" if sys.platform == 'win32' else config.name
            output_path = str(output_dir / exe_name)
        else:
            output_path = str(output_dir / config.name)
        
        if os.path.exists(output_path):
            self._emit_progress(100, f"Build erfolgreich: {output_path}")
            return BuildResult(
                success=True,
                output_path=output_path,
                duration=duration,
                log=self._log,
                warnings=warnings
            )
        else:
            return BuildResult(
                success=False,
                error_message="Build abgeschlossen, aber Output nicht gefunden",
                duration=duration,
                log=self._log,
                warnings=warnings
            )
    
    def _build_command(self, config: BuildConfig) -> List[str]:
        """Erstellt das PyInstaller-Kommando"""
        cmd = [sys.executable, '-m', 'PyInstaller']
        
        # Basis-Optionen
        cmd.extend(['--name', config.name])
        cmd.extend(['--distpath', config.output_dir])
        
        # One-File oder One-Directory
        if config.one_file:
            cmd.append('--onefile')
        else:
            cmd.append('--onedir')
        
        # Console oder Windowed
        if config.console:
            cmd.append('--console')
        else:
            cmd.append('--windowed')
        
        # Icon
        if config.icon and os.path.exists(config.icon):
            cmd.extend(['--icon', config.icon])
        
        # Hidden Imports
        for imp in config.hidden_imports:
            cmd.extend(['--hidden-import', imp])
        
        # Exclude Modules
        for mod in config.exclude_modules:
            cmd.extend(['--exclude-module', mod])
        
        # Data Files
        for src, dest in config.data_files:
            cmd.extend(['--add-data', f'{src}{os.pathsep}{dest}'])
        
        # Binary Files
        for src, dest in config.binary_files:
            cmd.extend(['--add-binary', f'{src}{os.pathsep}{dest}'])
        
        # UPX
        if config.upx and config.upx_dir:
            cmd.extend(['--upx-dir', config.upx_dir])
        elif not config.upx:
            cmd.append('--noupx')
        
        # Strip
        if config.strip:
            cmd.append('--strip')
        
        # Clean
        cmd.append('--clean')
        cmd.append('--noconfirm')
        
        # Das Skript
        cmd.append(config.script_path)
        
        return cmd
    
    def _clean_build(self, config: BuildConfig):
        """Entfernt vorherige Build-Artefakte"""
        build_dir = Path('build') / config.name
        if build_dir.exists():
            shutil.rmtree(build_dir, ignore_errors=True)
        
        spec_file = Path(f'{config.name}.spec')
        if spec_file.exists():
            spec_file.unlink()
    
    def create_spec_file(self, config: BuildConfig, output_path: str = None) -> str:
        """
        Erstellt eine .spec Datei für erweiterte Konfiguration
        
        Args:
            config: Build-Konfiguration
            output_path: Ausgabepfad für die Spec-Datei
            
        Returns:
            Pfad zur erstellten Spec-Datei
        """
        if output_path is None:
            output_path = f'{config.name}.spec'
        
        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
# Generiert von DevCenter Kompilator

block_cipher = None

a = Analysis(
    ['{config.script_path}'],
    pathex=[],
    binaries={config.binary_files},
    datas={config.data_files},
    hiddenimports={config.hidden_imports},
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes={config.exclude_modules},
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

'''
        
        if config.one_file:
            spec_content += f'''exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{config.name}',
    debug=False,
    bootloader_ignore_signals=False,
    strip={config.strip},
    upx={config.upx},
    upx_exclude=[],
    runtime_tmpdir=None,
    console={config.console},
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
'''
            if config.icon:
                spec_content += f"    icon='{config.icon}',\n"
            spec_content += ')\n'
        else:
            spec_content += f'''exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='{config.name}',
    debug=False,
    bootloader_ignore_signals=False,
    strip={config.strip},
    upx={config.upx},
    console={config.console},
'''
            if config.icon:
                spec_content += f"    icon='{config.icon}',\n"
            spec_content += f''')

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip={config.strip},
    upx={config.upx},
    upx_exclude=[],
    name='{config.name}',
)
'''
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(spec_content)
        
        return output_path


if __name__ == "__main__":
    # Test
    kompilator = Kompilator()
    
    print(f"PyInstaller installiert: {kompilator.check_pyinstaller()}")
    print(f"PyInstaller Version: {kompilator.get_pyinstaller_version()}")
