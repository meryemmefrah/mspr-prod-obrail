"""
Configuration partagée des tests (pytest).

Ce fichier est chargé automatiquement par pytest avant les tests. Il garantit
que la racine du backend est dans le PYTHONPATH, afin que les imports de type
"from api.main import app" fonctionnent quel que soit l'endroit d'où pytest
est lancé.
"""

from pathlib import Path
import sys


BACKEND_ROOT = Path(__file__).resolve().parents[1]

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))
