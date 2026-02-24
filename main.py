# -*- coding: utf-8 -*-
"""
DevCenter - Python Development Suite
Haupteinstiegspunkt der Anwendung

Starten mit:
    python main.py
oder:
    python -m src.gui.main_window
"""

import sys
import os

# Pfad zum src-Verzeichnis hinzufügen
src_path = os.path.dirname(os.path.abspath(__file__))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from src.gui.main_window import main

if __name__ == "__main__":
    main()
