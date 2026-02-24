# -*- coding: utf-8 -*-
"""
DevCenter - Icon Builder
Konvertiert Bilder zu Windows ICO-Dateien
Basierend auf IcoBuilder
"""

import os
from pathlib import Path
from typing import Optional, List, Tuple


class IcoBuilder:
    """
    Konvertiert Bilder in Windows ICO-Format
    
    Unterstützt: PNG, JPG, BMP, GIF
    """
    
    # Standard ICO-Größen
    DEFAULT_SIZES = [16, 24, 32, 48, 64, 128, 256]
    
    def __init__(self):
        self._pillow_available = False
        try:
            from PIL import Image
            self._pillow_available = True
        except ImportError:
            pass
    
    def is_available(self) -> bool:
        """Prüft ob Pillow installiert ist"""
        return self._pillow_available
    
    def convert(self, 
                input_path: str, 
                output_path: str = None,
                sizes: List[int] = None) -> Tuple[bool, str]:
        """
        Konvertiert ein Bild zu ICO
        
        Args:
            input_path: Pfad zum Quellbild
            output_path: Pfad für ICO (optional)
            sizes: Liste der Icon-Größen
            
        Returns:
            Tuple (success, message_or_path)
        """
        if not self._pillow_available:
            return False, "Pillow nicht installiert. Installieren mit: pip install Pillow"
        
        if not os.path.exists(input_path):
            return False, f"Datei nicht gefunden: {input_path}"
        
        if sizes is None:
            sizes = self.DEFAULT_SIZES
        
        if output_path is None:
            output_path = str(Path(input_path).with_suffix('.ico'))
        
        try:
            from PIL import Image
            
            # Bild laden
            img = Image.open(input_path)
            
            # RGBA konvertieren wenn nötig
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # Icons in verschiedenen Größen erstellen
            icon_images = []
            for size in sorted(sizes, reverse=True):
                resized = img.resize((size, size), Image.Resampling.LANCZOS)
                icon_images.append(resized)
            
            # Als ICO speichern
            icon_images[0].save(
                output_path,
                format='ICO',
                sizes=[(s, s) for s in sizes]
            )
            
            return True, output_path
            
        except Exception as e:
            return False, f"Fehler bei der Konvertierung: {e}"
    
    def create_placeholder(self, 
                          output_path: str, 
                          text: str = "?",
                          bg_color: str = "#3498db",
                          text_color: str = "#ffffff",
                          sizes: List[int] = None) -> Tuple[bool, str]:
        """
        Erstellt ein Platzhalter-Icon mit Text
        
        Args:
            output_path: Pfad für ICO
            text: Text im Icon (1-2 Zeichen)
            bg_color: Hintergrundfarbe
            text_color: Textfarbe
            sizes: Liste der Icon-Größen
            
        Returns:
            Tuple (success, message_or_path)
        """
        if not self._pillow_available:
            return False, "Pillow nicht installiert"
        
        if sizes is None:
            sizes = self.DEFAULT_SIZES
        
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            icon_images = []
            
            for size in sorted(sizes, reverse=True):
                # Bild erstellen
                img = Image.new('RGBA', (size, size), bg_color)
                draw = ImageDraw.Draw(img)
                
                # Font (größe proportional)
                font_size = int(size * 0.6)
                try:
                    font = ImageFont.truetype("arial.ttf", font_size)
                except:
                    font = ImageFont.load_default()
                
                # Text zentrieren
                text_to_draw = text[:2]
                bbox = draw.textbbox((0, 0), text_to_draw, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                x = (size - text_width) // 2
                y = (size - text_height) // 2 - bbox[1]
                
                draw.text((x, y), text_to_draw, fill=text_color, font=font)
                
                icon_images.append(img)
            
            # Als ICO speichern
            icon_images[0].save(
                output_path,
                format='ICO',
                sizes=[(s, s) for s in sizes]
            )
            
            return True, output_path
            
        except Exception as e:
            return False, f"Fehler: {e}"
    
    def extract_from_exe(self, exe_path: str, output_path: str) -> Tuple[bool, str]:
        """
        Extrahiert ein Icon aus einer EXE-Datei
        
        Args:
            exe_path: Pfad zur EXE
            output_path: Pfad für ICO
            
        Returns:
            Tuple (success, message)
        """
        # Windows-spezifisch - verwendet icoextract wenn verfügbar
        try:
            import icoextract
            extractor = icoextract.IconExtractor(exe_path)
            extractor.export_icon(output_path)
            return True, output_path
        except ImportError:
            return False, "icoextract nicht installiert"
        except Exception as e:
            return False, f"Fehler: {e}"


if __name__ == "__main__":
    builder = IcoBuilder()
    print(f"Pillow verfügbar: {builder.is_available()}")
    
    # Test Placeholder
    if builder.is_available():
        success, result = builder.create_placeholder(
            "test_icon.ico",
            text="DC",
            bg_color="#007acc"
        )
        print(f"Placeholder erstellt: {success} - {result}")
