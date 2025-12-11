# backend/DESDECERO/src/domain/attention_processor.py

import base64
import time
from typing import Optional, Dict, Any

import cv2
import numpy as np
import mediapipe as mp

from src.domain.metrics import MetricsCalculator
from src.domain.classifier import AttentionClassifier


class AttentionProcessor:
    """
    Procesa un frame individual enviado por el frontend:
    - Decodifica base64
    - Detecta rostro con MediaPipe FaceMesh
    - Calcula métricas faciales (EAR, MAR, PERCLOS, etc.)
    - Clasifica nivel de atención según métricas
    """

    def __init__(self):
        self.metrics_calculator = MetricsCalculator()
        self.classifier = AttentionClassifier()

        # MediaPipe FaceMesh (instancia única para todo el servidor)
        self.mp_face = mp.solutions.face_mesh
        self.face_mesh = self.mp_face.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )

    # ---------------------------------------------------------
    # Decodificar imagen base64 a frame OpenCV
    # ---------------------------------------------------------
    def _decode_base64_image(self, image_base64: str) -> Optional[np.ndarray]:
        """
        Recibe un string Base64 (con o sin prefijo data:image/...) y
        devuelve un frame en formato BGR.
        """
        try:
            # Eliminar prefijo si viene como data:image/jpeg;base64,...
            if "," in image_base64:
                image_base64 = image_base64.split(",", 1)[1]

            img_bytes = base64.b64decode(image_base64)
            np_buffer = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(np_buffer, cv2.IMREAD_COLOR)
            return img
        except Exception:
            return None

    # ---------------------------------------------------------
    # Procesar frame completo
    # ---------------------------------------------------------
    def process_base64_frame(self, image_base64: str) -> Optional[Dict[str, Any]]:
        """
        Procesa un frame individual y devuelve:
        {
            "metrics": {...},
            "attention_result": {...}
        }

        Si NO se detecta rostro → devuelve None.
        """

        frame = self._decode_base64_image(image_base64)
        if frame is None:
            return None

        h, w = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Procesar landmarks
        results = self.face_mesh.process(rgb)
        if not results.multi_face_landmarks:
            return None

        landmarks = results.multi_face_landmarks[0].landmark
        puntos = [(lm.x * w, lm.y * h, lm.z * w) for lm in landmarks]
        timestamp = time.time()  # único propósito: PERCLOS y parpadeos

        # 1) Calcular métricas crudas
        #    ⚠️ IMPORTANTE: usar argumentos POSICIONALES para coincidir con MetricsCalculator
        metrics = self.metrics_calculator.procesar_frame(
            puntos,  # lm
            w,       # ancho
            h,       # alto
            timestamp=timestamp,
        )

        # 2) Clasificar nivel de atención mediante reglas/ML
        attention_result = self.classifier.clasificar(metrics)

        return {
            "metrics": metrics,
            "attention_result": attention_result,
        }


# Instancia global para todo el backend
attention_processor = AttentionProcessor()
