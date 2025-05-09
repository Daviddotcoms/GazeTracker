import sys
import os

def resource_path(relative_path):
    """Obtiene la ruta absoluta al recurso, compatible con cx_Freeze."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path) 