# backend/DESDECERO/src/infrastructure/attention_repo.py

"""
attention_repo.py
===========================================================
Este módulo queda deshabilitado porque el nuevo backend 
NO usa sesiones, NO guarda frames, NO interactúa con Supabase 
ni con ninguna base de datos.

Se mantiene únicamente para evitar errores de importación.
===========================================================
"""


def create_attention_session(*args, **kwargs):
    """
    Stub: No crea sesiones.
    """
    raise NotImplementedError("Las sesiones ya no son utilizadas en este backend.")


def insert_attention_frame(*args, **kwargs):
    """
    Stub: No guarda frames.
    """
    raise NotImplementedError("No se almacenan frames en el nuevo backend.")


def finish_attention_session(*args, **kwargs):
    """
    Stub: No resume sesiones.
    """
    raise NotImplementedError("Las sesiones fueron eliminadas del sistema.")
