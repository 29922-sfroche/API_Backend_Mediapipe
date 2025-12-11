"""
CONFIG.PY – Configuración científica del Sistema de Monitoreo de Atención
===============================================================================
Incluye:
✔ Thresholds (umbrales científicos)
✔ ProcessingConfig (ventanas temporales)
✔ AttentionLevel (enum estados)
✔ MediaPipeLandmarks (índices faciales)
✔ Alias completos para MetricsCalculator y AttentionClassifier
✔ Pesos del clasificador totalmente corregidos
===============================================================================
"""

from dataclasses import dataclass
from enum import Enum


# ==============================================================================
# ENUM – Niveles de atención
# ==============================================================================

class AttentionLevel(str, Enum):
    CONCENTRADO = "concentrado"
    BAJA_ATENCION = "baja_atencion"
    DESCONCENTRACION_SEVERA = "desconcentracion_severa"


# ==============================================================================
# LANDMARKS – Puntos faciales estandarizados para MediaPipe
# ==============================================================================

@dataclass(frozen=True)
class MediaPipeLandmarks:
    left_eye: list
    right_eye: list
    iris_left: int
    iris_right: int
    mouth_top: int
    mouth_bottom: int
    mouth_left: int
    mouth_right: int
    nose: int
    chin: int
    pose_eye_left: int
    pose_eye_right: int
    pose_mouth_left: int
    pose_mouth_right: int


# ==============================================================================
# UMBRALES – Thresholds fisiológicos principales
# ==============================================================================

@dataclass(frozen=True)
class Thresholds:
    # EAR – Apertura del ojo
    ear_concentrado: float = 0.24
    ear_bajo_min: float = 0.19
    ear_severo: float = 0.16

    # PERCLOS
    perclos_concentrado: float = 0.20
    perclos_bajo_min: float = 0.20
    perclos_bajo_max: float = 0.40
    perclos_severo: float = 0.40

    # Parpadeos/min
    blink_concentrado_min: int = 5
    blink_concentrado_max: int = 22
    blink_bajo_min: int = 23
    blink_bajo_max: int = 32
    blink_severo: int = 32

    # Cabeza – Yaw
    yaw_concentrado: float = 12.0
    yaw_bajo_min: float = 12.0
    yaw_bajo_max: float = 22.0
    yaw_severo: float = 22.0

    # Cabeza – Pitch
    pitch_concentrado: float = 12.0
    pitch_bajo_min: float = 12.0
    pitch_bajo_max: float = 20.0
    pitch_severo: float = 20.0

    # Gaze Focus
    gaze_focus_concentrado: float = 0.55
    gaze_focus_bajo_min: float = 0.35
    gaze_focus_bajo_max: float = 0.55
    gaze_focus_severo: float = 0.35

    # Dispersión mirada
    gaze_disp_concentrado: float = 30.0
    gaze_disp_bajo_min: float = 30.0
    gaze_disp_bajo_max: float = 60.0
    gaze_disp_severo: float = 60.0

    # Apertura Ocular (Eye Opening)
    eye_opening_concentrado: float = 0.26
    eye_opening_bajo_min: float = 0.20
    eye_opening_bajo_max: float = 0.26
    eye_opening_severo: float = 0.20

    # MAR – Apertura de boca
    mar_normal: float = 0.55
    mar_bostezo: float = 0.75


# ==============================================================================
# CONFIGURACIÓN DE PROCESAMIENTO TEMPORAL
# ==============================================================================

@dataclass(frozen=True)
class ProcessingConfig:
    ventana_perclos: float = 60.0
    ventana_blinks: float = 60.0
    ventana_gaze: int = 30
    frames_parpadeo: int = 2
    fps_objetivo: int = 30
    buffer_size: int = 1800


# ==============================================================================
# OBJETOS PRINCIPALES
# ==============================================================================

LANDMARKS = MediaPipeLandmarks(
    left_eye=[362, 385, 387, 263, 373, 380],
    right_eye=[33, 160, 158, 133, 153, 144],
    iris_left=468,
    iris_right=473,
    mouth_top=13,
    mouth_bottom=14,
    mouth_left=78,
    mouth_right=308,
    nose=1,
    chin=199,
    pose_eye_left=263,
    pose_eye_right=33,
    pose_mouth_left=291,
    pose_mouth_right=61
)

THRESHOLDS = Thresholds()
PROCESSING_CONFIG = ProcessingConfig()


# ==============================================================================
# ALIAS COMPLETOS – COMPATIBILIDAD TOTAL
# ==============================================================================

BUFFER_SIZE = PROCESSING_CONFIG.buffer_size

# EAR
EAR_CONCENTRADO = THRESHOLDS.ear_concentrado
EAR_BAJO_MIN = THRESHOLDS.ear_bajo_min
EAR_SEVERO = THRESHOLDS.ear_severo

# Calibración
EAR_CALIBRACION_FRAMES = 60
EAR_CONCENTRADO_PCT = 0.85
EAR_BAJO_PCT = 0.70
EAR_SEVERO_PCT = 0.55

# Boca (MAR) – índices
BOCA_SUPERIOR = LANDMARKS.mouth_top
BOCA_INFERIOR = LANDMARKS.mouth_bottom
BOCA_IZQUIERDA = LANDMARKS.mouth_left
BOCA_DERECHA = LANDMARKS.mouth_right

# MAR thresholds
MAR_NORMAL = THRESHOLDS.mar_normal
MAR_BOSTEZO = THRESHOLDS.mar_bostezo
MAR_BOSTEZO_UMBRAL = THRESHOLDS.mar_bostezo
MAR_BOSTEZO_DURACION = 1.5

# PERCLOS
PERCLOS_CONCENTRADO = THRESHOLDS.perclos_concentrado
PERCLOS_BAJO_MIN = THRESHOLDS.perclos_bajo_min
PERCLOS_BAJO_MAX = THRESHOLDS.perclos_bajo_max
PERCLOS_SEVERO = THRESHOLDS.perclos_severo

# Blinks
BLINK_CONCENTRADO_MIN = THRESHOLDS.blink_concentrado_min
BLINK_CONCENTRADO_MAX = THRESHOLDS.blink_concentrado_max
BLINK_BAJO_MIN = THRESHOLDS.blink_bajo_min
BLINK_BAJO_MAX = THRESHOLDS.blink_bajo_max
BLINK_SEVERO = THRESHOLDS.blink_severo

# Pose – índices
POSE_NARIZ = LANDMARKS.nose
POSE_OJO_DER = LANDMARKS.pose_eye_right
POSE_OJO_IZQ = LANDMARKS.pose_eye_left
POSE_BOCA_DER = LANDMARKS.pose_mouth_right
POSE_BOCA_IZQ = LANDMARKS.pose_mouth_left
POSE_MENTON = LANDMARKS.chin

# Pose – umbrales
YAW_CONCENTRADO = THRESHOLDS.yaw_concentrado
YAW_SEVERO = THRESHOLDS.yaw_severo
PITCH_CONCENTRADO = THRESHOLDS.pitch_concentrado
PITCH_SEVERO = THRESHOLDS.pitch_severo

# Ojos
OJO_IZQUIERDO = LANDMARKS.left_eye
OJO_DERECHO = LANDMARKS.right_eye
IRIS_IZQUIERDO_CENTRO = LANDMARKS.iris_left
IRIS_DERECHO_CENTRO = LANDMARKS.iris_right

# Ventanas
VENTANA_PERCLOS = PROCESSING_CONFIG.ventana_perclos
FRAMES_PARPADEO = PROCESSING_CONFIG.frames_parpadeo

# Gaze focus dispersion
GAZE_FOCUS_CONCENTRADO = THRESHOLDS.gaze_focus_concentrado
GAZE_FOCUS_BAJO_MIN = THRESHOLDS.gaze_focus_bajo_min
GAZE_FOCUS_BAJO_MAX = THRESHOLDS.gaze_focus_bajo_max
GAZE_FOCUS_SEVERO = THRESHOLDS.gaze_focus_severo

GAZE_DISPERSION_CONCENTRADO = THRESHOLDS.gaze_disp_concentrado
GAZE_DISPERSION_BAJO_MIN = THRESHOLDS.gaze_disp_bajo_min
GAZE_DISPERSION_BAJO_MAX = THRESHOLDS.gaze_disp_bajo_max
GAZE_DISPERSION_SEVERO = THRESHOLDS.gaze_disp_severo

# Eye Opening
EYE_OPENING_CONCENTRADO = THRESHOLDS.eye_opening_concentrado
EYE_OPENING_BAJO_MIN = THRESHOLDS.eye_opening_bajo_min
EYE_OPENING_BAJO_MAX = THRESHOLDS.eye_opening_bajo_max
EYE_OPENING_SEVERO = THRESHOLDS.eye_opening_severo


# ==============================================================================
# PESOS DEL CLASIFICADOR (TODAS las métricas requeridas)
# ==============================================================================

PESOS = {
    "ear": 0.20,
    "perclos": 0.20,
    "parpadeos_min": 0.15,
    "pose": 0.15,               # yaw + pitch usan este mismo peso
    "gaze_focus": 0.15,
    "gaze_dispersion": 0.05,
    "eye_opening": 0.05,        # ← FALTABA, NECESARIO
    "mar": 0.05,                # ← FALTABA, NECESARIO
}
