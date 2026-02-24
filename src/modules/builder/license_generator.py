# -*- coding: utf-8 -*-
"""
DevCenter - License Generator
Sammelt und generiert Third-Party Lizenzen
Basierend auf ThirdPartyLicenses
"""

import subprocess
import sys
import json
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class PackageLicense:
    """Lizenzinformationen eines Packages"""
    name: str
    version: str
    license: str
    license_text: Optional[str] = None
    url: Optional[str] = None
    author: Optional[str] = None


class LicenseGenerator:
    """
    Sammelt Lizenzinformationen aller installierten Packages
    und generiert eine Third-Party-Lizenzdatei
    """
    
    def __init__(self):
        self._pip_licenses_available = False
        try:
            import pip_licenses
            self._pip_licenses_available = True
        except ImportError:
            pass
    
    def is_available(self) -> bool:
        """Prüft ob pip-licenses installiert ist"""
        return self._pip_licenses_available
    
    def get_licenses(self, 
                     requirements_file: str = None,
                     include_dev: bool = False) -> List[PackageLicense]:
        """
        Sammelt alle Lizenzinformationen
        
        Args:
            requirements_file: Optionale requirements.txt
            include_dev: Auch Dev-Dependencies einbeziehen
            
        Returns:
            Liste von PackageLicense
        """
        licenses = []
        
        try:
            # pip-licenses verwenden wenn verfügbar
            if self._pip_licenses_available:
                result = subprocess.run(
                    [sys.executable, '-m', 'pip_licenses', 
                     '--format=json', '--with-license-file', '--with-urls'],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    for pkg in data:
                        licenses.append(PackageLicense(
                            name=pkg.get('Name', ''),
                            version=pkg.get('Version', ''),
                            license=pkg.get('License', 'Unknown'),
                            license_text=pkg.get('LicenseText', None),
                            url=pkg.get('URL', None),
                            author=pkg.get('Author', None)
                        ))
            else:
                # Fallback: pip show
                result = subprocess.run(
                    [sys.executable, '-m', 'pip', 'list', '--format=json'],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    packages = json.loads(result.stdout)
                    for pkg in packages:
                        name = pkg.get('name', '')
                        version = pkg.get('version', '')
                        
                        # Details holen
                        detail = subprocess.run(
                            [sys.executable, '-m', 'pip', 'show', name],
                            capture_output=True,
                            text=True
                        )
                        
                        license_name = "Unknown"
                        author = None
                        url = None
                        
                        if detail.returncode == 0:
                            for line in detail.stdout.split('\n'):
                                if line.startswith('License:'):
                                    license_name = line.split(':', 1)[1].strip()
                                elif line.startswith('Author:'):
                                    author = line.split(':', 1)[1].strip()
                                elif line.startswith('Home-page:'):
                                    url = line.split(':', 1)[1].strip()
                        
                        licenses.append(PackageLicense(
                            name=name,
                            version=version,
                            license=license_name,
                            author=author,
                            url=url
                        ))
        
        except Exception as e:
            print(f"Fehler beim Sammeln der Lizenzen: {e}")
        
        return licenses
    
    def generate_notice_file(self, 
                             output_path: str,
                             app_name: str = "Application",
                             app_version: str = "1.0.0") -> bool:
        """
        Generiert eine THIRD-PARTY-NOTICES Datei
        
        Args:
            output_path: Ausgabepfad
            app_name: Name der Anwendung
            app_version: Version der Anwendung
            
        Returns:
            True bei Erfolg
        """
        licenses = self.get_licenses()
        
        if not licenses:
            return False
        
        try:
            lines = [
                f"THIRD-PARTY SOFTWARE NOTICES AND INFORMATION",
                f"",
                f"This software ({app_name} {app_version}) incorporates components from",
                f"the projects listed below.",
                f"",
                f"=" * 70,
                f""
            ]
            
            for lic in sorted(licenses, key=lambda x: x.name.lower()):
                lines.append(f"{lic.name} {lic.version}")
                lines.append(f"License: {lic.license}")
                if lic.url:
                    lines.append(f"URL: {lic.url}")
                if lic.author:
                    lines.append(f"Author: {lic.author}")
                lines.append("")
                
                if lic.license_text:
                    lines.append("-" * 40)
                    lines.append(lic.license_text[:2000])  # Begrenzen
                    if len(lic.license_text) > 2000:
                        lines.append("... [truncated]")
                    lines.append("-" * 40)
                
                lines.append("")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            
            return True
            
        except Exception as e:
            print(f"Fehler beim Generieren der Notice-Datei: {e}")
            return False
    
    def generate_json(self, output_path: str) -> bool:
        """Exportiert Lizenzen als JSON"""
        licenses = self.get_licenses()
        
        try:
            data = []
            for lic in licenses:
                data.append({
                    'name': lic.name,
                    'version': lic.version,
                    'license': lic.license,
                    'url': lic.url,
                    'author': lic.author
                })
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Fehler: {e}")
            return False
    
    def check_license_compatibility(self, 
                                    allowed_licenses: List[str] = None) -> List[str]:
        """
        Prüft auf inkompatible Lizenzen
        
        Args:
            allowed_licenses: Liste erlaubter Lizenzen
            
        Returns:
            Liste problematischer Packages
        """
        if allowed_licenses is None:
            allowed_licenses = [
                'MIT', 'MIT License',
                'BSD', 'BSD License', 'BSD-2-Clause', 'BSD-3-Clause',
                'Apache', 'Apache 2.0', 'Apache Software License',
                'Apache License 2.0', 'Apache-2.0',
                'ISC', 'ISC License',
                'PSF', 'Python Software Foundation License',
                'LGPL', 'LGPLv2', 'LGPLv3', 'LGPL-2.1', 'LGPL-3.0',
                'MPL', 'MPL 2.0', 'MPL-2.0',
                'Public Domain', 'Unlicense', 'CC0',
                'WTFPL'
            ]
        
        licenses = self.get_licenses()
        problematic = []
        
        for lic in licenses:
            license_ok = False
            for allowed in allowed_licenses:
                if allowed.lower() in lic.license.lower():
                    license_ok = True
                    break
            
            if not license_ok and lic.license != 'Unknown':
                problematic.append(f"{lic.name}: {lic.license}")
        
        return problematic


if __name__ == "__main__":
    gen = LicenseGenerator()
    print(f"pip-licenses verfügbar: {gen.is_available()}")
    
    licenses = gen.get_licenses()
    print(f"\n{len(licenses)} Packages gefunden:")
    for lic in licenses[:10]:
        print(f"  {lic.name} ({lic.version}): {lic.license}")
    
    if len(licenses) > 10:
        print(f"  ... und {len(licenses) - 10} weitere")
