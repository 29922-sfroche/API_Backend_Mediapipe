"""
================================================================================
METRICS.PY — Cálculo de métricas fisiológicas y comportamentales
Versión optimizada para API en tiempo real (sin sesiones)
================================================================================
"""

import numpy as np
import cv2
from collections import deque
import time

from . import config


class MetricsCalculator:
    """
    Calcula métricas de atención con:
    - Calibración automática EAR
    - Detección de parpadeos
    - Detección de bostezo
    - Estimación de pose de cabeza (yaw / pitch / roll)
    - Métricas de mirada (foco y dispersión)
    """

    def __init__(self):
        # Buffers temporales
        self.buffer_ear = deque(maxlen=config.BUFFER_SIZE)
        self.buffer_parpadeos = deque(maxlen=config.BUFFER_SIZE)
        self.buffer_gaze = deque(maxlen=config.BUFFER_SIZE)
        self.buffer_timestamps = deque(maxlen=config.BUFFER_SIZE)

        # Parpadeos
        self.frames_bajo_umbral = 0
        self.total_parpadeos = 0

        # Bostezo
        self.mar_buffer = deque(maxlen=60)
        self.mar_alto_inicio = None
        self.total_bostezos = 0

        # Calibración EAR
        self.calibracion_completa = False
        self.ear_calibracion = []
        self.ear_base = 0.30

        self.ear_umbral_concentrado = config.EAR_CONCENTRADO
        self.ear_umbral_bajo = config.EAR_BAJO_MIN
        self.ear_umbral_severo = config.EAR_SEVERO

        # Pose suavizada
        self.buffer_yaw = deque(maxlen=7)
        self.buffer_pitch = deque(maxlen=7)
        self.buffer_ear_suave = deque(maxlen=5)

        # Mirada (foco central)
        self.gaze_centro = None
        self.frames_calibracion_gaze = []

    # ----------------------------------------------------------------------
    # UTILIDADES
    # ----------------------------------------------------------------------

    @staticmethod
    def distance(p1, p2):
        """Distancia euclidiana."""
        return np.linalg.norm(np.array(p1) - np.array(p2))

    # ----------------------------------------------------------------------
    # EAR (Eye Aspect Ratio)
    # ----------------------------------------------------------------------

    def calcular_ear(self, landmarks, eye_idx):
        """EAR por Soukupová & Čech, 2016."""
        try:
            p = [landmarks[i][:2] for i in eye_idx]
            vertical_1 = self.distance(p[1], p[5])
            vertical_2 = self.distance(p[2], p[4])
            horizontal = self.distance(p[0], p[3])

            if horizontal < 1e-6:
                return 0.30
            return (vertical_1 + vertical_2) / (2.0 * horizontal)
        except:
            return 0.30

    # ----------------------------------------------------------------------
    # Calibración automática EAR
    # ----------------------------------------------------------------------

    def calibrar_ear(self, ear):
        """Calibra EAR base con los primeros frames."""
        if self.calibracion_completa:
            return

        self.ear_calibracion.append(ear)
        if len(self.ear_calibracion) < config.EAR_CALIBRACION_FRAMES:
            return

        # Promedio de los valores más altos = ojos abiertos
        vals = sorted(self.ear_calibracion, reverse=True)
        top = vals[: int(len(vals) * 0.7)]
        self.ear_base = max(np.mean(top), 0.20)

        # Nuevos umbrales personalizados
        self.ear_umbral_concentrado = self.ear_base * config.EAR_CONCENTRADO_PCT
        self.ear_umbral_bajo = self.ear_base * config.EAR_BAJO_PCT
        self.ear_umbral_severo = self.ear_base * config.EAR_SEVERO_PCT

        self.calibracion_completa = True

    # ----------------------------------------------------------------------
    # MAR (Apertura de boca) y bostezo
    # ----------------------------------------------------------------------

    def calcular_mar(self, lm):
        try:
            top = lm[config.BOCA_SUPERIOR][:2]
            bottom = lm[config.BOCA_INFERIOR][:2]
            left = lm[config.BOCA_IZQUIERDA][:2]
            right = lm[config.BOCA_DERECHA][:2]

            vertical = self.distance(top, bottom)
            horizontal = self.distance(left, right)

            if horizontal < 1e-6:
                return 0.30
            return vertical / horizontal

        except:
            return 0.30

    def detectar_bostezo(self, mar, t):
        es_bostezo = False

        if mar > config.MAR_BOSTEZO:
            if self.mar_alto_inicio is None:
                self.mar_alto_inicio = t
            else:
                if t - self.mar_alto_inicio >= config.MAR_BOSTEZO_DURACION:
                    self.total_bostezos += 1
                    es_bostezo = True
                    self.mar_alto_inicio = None
        else:
            self.mar_alto_inicio = None

        return es_bostezo

    # ----------------------------------------------------------------------
    # Apertura Ocular (Eye Opening)
    # ----------------------------------------------------------------------

    def calcular_apertura_ocular(self, lm, eye_idx):
        """Apertura normalizada del ojo."""
        try:
            pts = [lm[i][:2] for i in eye_idx]
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]

            w = max(xs) - min(xs)
            h = max(ys) - min(ys)

            if w < 1e-6:
                return 0.30
            return h / w
        except:
            return 0.30

    # ----------------------------------------------------------------------
    # Pose de cabeza: yaw / pitch / roll
    # ----------------------------------------------------------------------

    def calcular_pose(self, lm, w, h):

        try:
            pts_2d = np.array([
                lm[config.POSE_NARIZ][:2],
                lm[config.POSE_OJO_DER][:2],
                lm[config.POSE_OJO_IZQ][:2],
                lm[config.POSE_BOCA_DER][:2],
                lm[config.POSE_BOCA_IZQ][:2],
                lm[config.POSE_MENTON][:2]
            ], dtype=np.float64)

            pts_3d = np.array([
                (0, 0, 0),
                (225, 170, -135),
                (-225, 170, -135),
                (150, -150, -125),
                (-150, -150, -125),
                (0, -330, -65)
            ], dtype=np.float64)

            focal = w
            center = (w / 2, h / 2)
            camera = np.array([
                [focal, 0, center[0]],
                [0, focal, center[1]],
                [0, 0, 1]
            ], dtype=np.float64)

            _, rot, trans = cv2.solvePnP(
                pts_3d, pts_2d, camera, np.zeros((4, 1)),
                flags=cv2.SOLVEPNP_ITERATIVE
            )

            rot_mtx, _ = cv2.Rodrigues(rot)
            pose = cv2.hconcat([rot_mtx, trans])
            _, _, _, _, _, _, euler = cv2.decomposeProjectionMatrix(pose)

            pitch = float(euler[0][0])
            yaw = float(euler[1][0])
            roll = float(euler[2][0])

            # Suavizado
            self.buffer_yaw.append(yaw)
            self.buffer_pitch.append(pitch)

            return np.mean(self.buffer_yaw), np.mean(self.buffer_pitch), roll

        except:
            return 0.0, 0.0, 0.0

    # ----------------------------------------------------------------------
    # Mirada (gaze)
    # ----------------------------------------------------------------------

    def calcular_mirada(self, lm, w, h):
        try:
            irisL = lm[config.IRIS_IZQUIERDO_CENTRO][:2]
            irisR = lm[config.IRIS_DERECHO_CENTRO][:2]
            gx = (irisL[0] + irisR[0]) / 2
            gy = (irisL[1] + irisR[1]) / 2

            return gx / w, gy / h
        except:
            return 0.5, 0.5

    # ----------------------------------------------------------------------
    # Detectar parpadeo
    # ----------------------------------------------------------------------

    def detectar_parpadeo(self, ear):
        """Detecta parpadeos a partir del EAR."""
        umbral = self.ear_umbral_bajo if self.calibracion_completa else config.EAR_BAJO_MIN

        es_parpadeo = False

        if ear < umbral:
            self.frames_bajo_umbral += 1
        else:
            if self.frames_bajo_umbral >= config.FRAMES_PARPADEO:
                es_parpadeo = True
                self.total_parpadeos += 1
            self.frames_bajo_umbral = 0

        return es_parpadeo

    # ----------------------------------------------------------------------
    # PROCESO PRINCIPAL: procesar un frame completo
    # ----------------------------------------------------------------------

    def procesar_frame(self, lm, w, h, timestamp=None):
        try:
            t = timestamp or time.time()

            # --- EAR ---
            earL = self.calcular_ear(lm, config.OJO_IZQUIERDO)
            earR = self.calcular_ear(lm, config.OJO_DERECHO)
            ear = (earL + earR) / 2

            # Suavizado
            self.buffer_ear_suave.append(ear)
            ear_suave = np.mean(self.buffer_ear_suave)

            # Calibración
            self.calibrar_ear(ear_suave)

            # MAR
            mar = self.calcular_mar(lm)
            es_bostezo = self.detectar_bostezo(mar, t)

            # Apertura de los ojos
            apL = self.calcular_apertura_ocular(lm, config.OJO_IZQUIERDO)
            apR = self.calcular_apertura_ocular(lm, config.OJO_DERECHO)
            apertura = (apL + apR) / 2

            # Pose
            yaw, pitch, roll = self.calcular_pose(lm, w, h)

            # Mirada
            gaze_x, gaze_y = self.calcular_mirada(lm, w, h)
            es_parpadeo = self.detectar_parpadeo(ear_suave)

            # Buffers temporales
            self.buffer_ear.append((t, ear_suave))
            self.buffer_parpadeos.append((t, es_parpadeo))
            self.buffer_gaze.append((t, gaze_x, gaze_y))
            self.buffer_timestamps.append(t)

            temporales = self.calcular_metricas_temporales(t)

            return {
                "timestamp": t,
                "ear": ear_suave,
                "ear_raw": ear,
                "ear_base": self.ear_base,
                "calibrado": self.calibracion_completa,
                "mar": mar,
                "apertura": apertura,
                "yaw": yaw,
                "pitch": pitch,
                "roll": roll,
                "gaze_x": gaze_x,
                "gaze_y": gaze_y,
                "es_parpadeo": es_parpadeo,
                "es_bostezo": es_bostezo,
                "total_parpadeos": self.total_parpadeos,
                "total_bostezos": self.total_bostezos,
                **temporales
            }

        except Exception as e:
            print("❌ ERROR en procesar_frame:", e)
            return self._fallback()

    # ----------------------------------------------------------------------
    # MÉTRICAS TEMPORALES (PERCLOS, blinks/min, foco, dispersión)
    # ----------------------------------------------------------------------

    def calcular_metricas_temporales(self, t):
        ventana = t - config.VENTANA_PERCLOS

        # PERCLOS
        umbral = self.ear_umbral_bajo if self.calibracion_completa else config.EAR_BAJO_MIN
        recientes = [(ts, e) for ts, e in self.buffer_ear if ts > ventana]

        if recientes:
            cerrados = sum(1 for _, e in recientes if e < umbral)
            perclos = cerrados / len(recientes)
        else:
            perclos = 0.0

        # Parpadeos/min
        blinks = [(ts, p) for ts, p in self.buffer_parpadeos if ts > ventana]
        cantidad = sum(1 for _, p in blinks if p)

        if len(self.buffer_timestamps) > 1:
            dt = t - self.buffer_timestamps[0]
            dt = max(min(dt, 60), 1)  # evitar dividir por 0
            parpadeos_min = (cantidad / dt) * 60
        else:
            parpadeos_min = 0

        # Mirada
        gaze_1s = [(ts, x, y) for ts, x, y in self.buffer_gaze if ts > t - 1]
        if gaze_1s:
            xs = [x for _, x, _ in gaze_1s]
            ys = [y for _, _, y in gaze_1s]
            dispersion = (np.var(xs) + np.var(ys)) * 1000
            gaze_focus = 1 - min(dispersion / 300, 1)
        else:
            gaze_focus = 1.0
            dispersion = 0.0

        return {
            "perclos": perclos,
            "parpadeos_min": parpadeos_min,
            "gaze_focus": gaze_focus,
            "gaze_dispersion": dispersion,
        }

    # ----------------------------------------------------------------------

    def _fallback(self):
        """Valores por defecto seguros si ocurre un error inesperado."""
        return {
            "timestamp": time.time(),
            "ear": 0.3,
            "ear_raw": 0.3,
            "ear_base": self.ear_base,
            "calibrado": False,
            "mar": 0.3,
            "apertura": 0.3,
            "yaw": 0,
            "pitch": 0,
            "roll": 0,
            "gaze_x": 0.5,
            "gaze_y": 0.5,
            "es_parpadeo": False,
            "es_bostezo": False,
            "total_parpadeos": self.total_parpadeos,
            "total_bostezos": self.total_bostezos,
            "perclos": 0,
            "parpadeos_min": 0,
            "gaze_focus": 1,
            "gaze_dispersion": 0
        }
