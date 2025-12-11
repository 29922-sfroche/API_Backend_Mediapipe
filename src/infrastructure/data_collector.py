"""
data_collector.py
===========================================================
Este módulo ha sido deshabilitado completamente porque
el nuevo backend SOLO procesa frames en tiempo real y
NO almacena datos, NO usa sesiones, NO guarda CSV, JSON
ni SQLite, y NO recolecta landmarks.

Se mantiene únicamente como stub para evitar errores
en caso de que algún módulo legacy aún intente importarlo.
===========================================================
"""

class DataCollector:
    """
    Stub vacío. Ninguna función realiza acciones.
    Se conserva la firma mínima para compatibilidad.
    """
    def __init__(self, *args, **kwargs):
        pass

    def start(self):
        pass

    def collect(self, *args, **kwargs):
        pass

    def stop(self):
        return {
            "message": "DataCollector está deshabilitado en esta versión del backend."
        }

    def get_realtime_stats(self):
        return {
            "frames": 0,
            "elapsed": 0,
            "fps": 0,
            "avg_score": 0,
            "concentrated_pct": 0,
            "blinks": 0,
            "yawns": 0
        }


class LandmarkRecorder:
    """
    Stub vacío. Ninguna función realiza acciones.
    """
    def __init__(self, *args, **kwargs):
        pass

    def record(self, *args, **kwargs):
        pass

    def save(self):
        return None
