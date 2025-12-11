# backend/DESDECERO/src/api/schemas.py

from typing import Optional
from pydantic import BaseModel, Field


# =========================
#   Frames — Entrada
# =========================

class ProcessFrameRequest(BaseModel):
    frame_number: int = Field(..., description="Número de frame enviado por el frontend")
    image_base64: str = Field(..., description="Imagen enviada en base64 desde la cámara")


# =========================
#   Frames — Salida
# =========================

class ProcessFrameResponse(BaseModel):
    frame_number: int
    face_detected: bool

    # Nivel de atención
    attention_level: Optional[str] = None
    attention_score: Optional[float] = None  # 0 - 1
    is_concentrated: Optional[bool] = None

    # Métricas faciales
    ear: Optional[float] = None
    perclos: Optional[float] = None
    blinks_per_minute: Optional[float] = None
    head_yaw: Optional[float] = None
    head_pitch: Optional[float] = None
    gaze_focus: Optional[float] = None
    gaze_dispersion: Optional[float] = None
    mar: Optional[float] = None
    is_blink: Optional[bool] = None
    is_yawn: Optional[bool] = None
