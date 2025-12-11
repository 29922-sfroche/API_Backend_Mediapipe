# backend/DESDECERO/src/api/router_frames.py

from fastapi import APIRouter, HTTPException

from ..domain.attention_processor import attention_processor
from .schemas import ProcessFrameRequest, ProcessFrameResponse

router = APIRouter()


@router.post("/process", response_model=ProcessFrameResponse)
def process_frame(payload: ProcessFrameRequest):
    """
    Recibe un frame en base64 desde el frontend,
    calcula métricas de atención y devuelve resultados.

    NOTA:
    - No guarda en BD
    - No usa session_id
    - Solo funciona como API de procesamiento de frames en tiempo real
    """
    try:
        # Procesar imagen base64 con MediaPipe
        result = attention_processor.process_base64_frame(payload.image_base64)

        # No se detectó rostro
        if result is None:
            return ProcessFrameResponse(
                frame_number=payload.frame_number,
                face_detected=False,
            )

        metrics = result["metrics"]
        attention_result = result["attention_result"]

        # Convertir estado interno → niveles textuales
        estado = attention_result.get("estado", "NO_CONCENTRADO")

        if estado == "CONCENTRADO":
            attention_level = "concentrado"
        elif estado == "BAJA_ATENCION":
            attention_level = "baja_atencion"
        else:
            attention_level = "desconcentracion_severa"

        # Respuesta directa sin base de datos
        return ProcessFrameResponse(
            frame_number=payload.frame_number,
            face_detected=True,
            attention_level=attention_level,
            attention_score=float(attention_result.get("score", 0.0)),
            is_concentrated=bool(attention_result.get("concentrado", False)),

            # Métricas faciales procesadas
            ear=float(metrics.get("ear", 0.0)),
            perclos=float(metrics.get("perclos", 0.0)),
            blinks_per_minute=float(metrics.get("parpadeos_min", 0.0)),
            head_yaw=float(metrics.get("yaw", 0.0)),
            head_pitch=float(metrics.get("pitch", 0.0)),
            gaze_focus=float(metrics.get("gaze_focus", 0.0)),
            gaze_dispersion=float(metrics.get("gaze_dispersion", 0.0)),
            mar=float(metrics.get("mar", 0.0)),
            is_blink=bool(metrics.get("es_parpadeo", False)),
            is_yawn=bool(metrics.get("es_bostezo", False)),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
