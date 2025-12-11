# backend/DESDECERO/src/api/router_sessions.py

from fastapi import APIRouter

router = APIRouter()

"""
Este router ya NO maneja sesiones.
Se mantiene vacío únicamente para evitar errores
si aún está referenciado en main.py.

Si lo deseas, puedes eliminarlo completamente.
"""


@router.get("/info")
def session_info():
    return {
        "message": "El sistema ya no utiliza sesiones. Todas las operaciones se hacen en tiempo real por frame."
    }
