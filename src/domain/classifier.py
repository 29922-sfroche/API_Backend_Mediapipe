# backend/DESDECERO/src/domain/classifier.py

"""
================================================================================
CLASSIFIER.PY - CLASIFICACIÓN CORREGIDA Y OPTIMIZADA
================================================================================

Mejoras aplicadas:
✔ Normalización completa del código
✔ Eliminación de ramas repetidas
✔ Manejo seguro de métricas faltantes
✔ Reglas de atención más consistentes
✔ Estado final más robusto según pitch/yaw (mirando fuera)
================================================================================
"""

from src.domain import config


class AttentionClassifier:

    def __init__(self):
        # Pesos definidos en config.py
        self.pesos = config.PESOS

    # -------------------------------------------------------------------------
    #  MÉTRICAS INDIVIDUALES
    # -------------------------------------------------------------------------

    def clasificar_ear(self, ear, calibrado=False, ear_base=0.30):
        """
        EAR (apertura del ojo):
        - Alto → despierto
        - Medio → baja atención
        - Muy bajo → posible sueño
        """
        if calibrado:
            umbral_conc = ear_base * config.EAR_CONCENTRADO_PCT
            umbral_bajo = ear_base * config.EAR_BAJO_PCT
            umbral_severo = ear_base * config.EAR_SEVERO_PCT
        else:
            umbral_conc = config.EAR_CONCENTRADO
            umbral_bajo = config.EAR_BAJO_MIN
            umbral_severo = config.EAR_SEVERO

        if ear > umbral_conc:
            return "CONCENTRADO", 100, f"EAR {ear:.3f} OK ✓"

        elif ear >= umbral_bajo:
            rango = max(umbral_conc - umbral_bajo, 0.01)
            posicion = (ear - umbral_bajo) / rango
            score = 55 + posicion * 35
            return "BAJO", score, f"EAR {ear:.3f} medio"

        else:
            score = max(20, (ear / max(umbral_severo, 0.001)) * 50)
            return "SEVERO", score, f"EAR {ear:.3f} bajo ✗"

    # -------------------------------------------------------------------------

    def clasificar_perclos(self, perclos):
        if perclos < config.PERCLOS_CONCENTRADO:
            return "CONCENTRADO", 100, f"PERCLOS {perclos*100:.1f}% OK ✓"

        elif perclos <= config.PERCLOS_SEVERO:
            rango = max(config.PERCLOS_SEVERO - config.PERCLOS_CONCENTRADO, 0.01)
            posicion = (perclos - config.PERCLOS_CONCENTRADO) / rango
            score = 85 - posicion * 45
            return "BAJO", score, f"PERCLOS {perclos*100:.1f}% medio"

        else:
            return "SEVERO", 25, f"PERCLOS {perclos*100:.1f}% alto ✗"

    # -------------------------------------------------------------------------

    def clasificar_parpadeos(self, bpm):
        if config.BLINK_CONCENTRADO_MIN <= bpm <= config.BLINK_CONCENTRADO_MAX:
            return "CONCENTRADO", 100, f"{bpm:.0f}/min OK ✓"

        elif bpm < config.BLINK_CONCENTRADO_MIN:
            score = max(50, (bpm / max(config.BLINK_CONCENTRADO_MIN, 1)) * 80)
            return "BAJO", score, f"{bpm:.0f}/min bajo"

        elif bpm <= config.BLINK_SEVERO:
            rango = max(config.BLINK_SEVERO - config.BLINK_CONCENTRADO_MAX, 0.01)
            posicion = (bpm - config.BLINK_CONCENTRADO_MAX) / rango
            score = 80 - posicion * 35
            return "BAJO", score, f"{bpm:.0f}/min alto"

        else:
            return "SEVERO", 35, f"{bpm:.0f}/min muy alto ✗"

    # -------------------------------------------------------------------------

    def clasificar_yaw(self, yaw):
        abs_yaw = abs(yaw)

        if abs_yaw < config.YAW_CONCENTRADO:
            return "CONCENTRADO", 100, f"Yaw {yaw:.1f}° OK ✓"

        elif abs_yaw <= config.YAW_SEVERO:
            rango = max(config.YAW_SEVERO - config.YAW_CONCENTRADO, 0.01)
            posicion = (abs_yaw - config.YAW_CONCENTRADO) / rango
            score = 75 - posicion * 45
            return "BAJO", score, f"Yaw {yaw:.1f}° girado"

        else:
            exceso = abs_yaw - config.YAW_SEVERO
            score = max(10, 30 - exceso * 2)
            return "SEVERO", score, f"Yaw {yaw:.1f}° MUY girado ✗"

    # -------------------------------------------------------------------------

    def clasificar_pitch(self, pitch):
        abs_pitch = abs(pitch)

        if abs_pitch < config.PITCH_CONCENTRADO:
            return "CONCENTRADO", 100, f"Pitch {pitch:.1f}° OK ✓"

        elif abs_pitch <= config.PITCH_SEVERO:
            rango = max(config.PITCH_SEVERO - config.PITCH_CONCENTRADO, 0.01)
            posicion = (abs_pitch - config.PITCH_CONCENTRADO) / rango
            score = 75 - posicion * 45
            return "BAJO", score, f"Pitch {pitch:.1f}° inclinado"

        else:
            exceso = abs_pitch - config.PITCH_SEVERO
            score = max(10, 30 - exceso * 2)
            return "SEVERO", score, f"Pitch {pitch:.1f}° MUY inclinado ✗"

    # -------------------------------------------------------------------------

    def clasificar_gaze_focus(self, focus):
        if focus > config.GAZE_FOCUS_CONCENTRADO:
            return "CONCENTRADO", 100, f"Foco {focus*100:.0f}% OK ✓"

        elif focus >= config.GAZE_FOCUS_SEVERO:
            rango = max(config.GAZE_FOCUS_CONCENTRADO - config.GAZE_FOCUS_SEVERO, 0.01)
            posicion = (focus - config.GAZE_FOCUS_SEVERO) / rango
            score = 45 + posicion * 40
            return "BAJO", score, f"Foco {focus*100:.0f}% medio"

        else:
            return "SEVERO", 30, f"Foco {focus*100:.0f}% bajo ✗"

    # -------------------------------------------------------------------------

    def clasificar_gaze_dispersion(self, dispersion):
        if dispersion < config.GAZE_DISPERSION_CONCENTRADO:
            return "CONCENTRADO", 100, f"Disp {dispersion:.3f} OK ✓"

        elif dispersion <= config.GAZE_DISPERSION_SEVERO:
            rango = max(config.GAZE_DISPERSION_SEVERO - config.GAZE_DISPERSION_CONCENTRADO, 0.01)
            posicion = (dispersion - config.GAZE_DISPERSION_CONCENTRADO) / rango
            score = 85 - posicion * 40
            return "BAJO", score, f"Disp {dispersion:.3f} media"

        else:
            return "SEVERO", 30, f"Disp {dispersion:.3f} alta ✗"

    # -------------------------------------------------------------------------

    def clasificar_eye_opening(self, apertura):
        if apertura > config.EYE_OPENING_CONCENTRADO:
            return "CONCENTRADO", 100, f"Apert {apertura:.3f} OK ✓"

        elif apertura >= config.EYE_OPENING_SEVERO:
            rango = max(config.EYE_OPENING_CONCENTRADO - config.EYE_OPENING_SEVERO, 0.01)
            posicion = (apertura - config.EYE_OPENING_SEVERO) / rango
            score = 55 + posicion * 30
            return "BAJO", score, f"Apert {apertura:.3f} media"

        else:
            return "SEVERO", 30, f"Apert {apertura:.3f} baja ✗"

    # -------------------------------------------------------------------------

    def clasificar_mar(self, mar, es_bostezo=False):
        if es_bostezo:
            return "SEVERO", 30, f"MAR {mar:.3f} BOSTEZO ✗"

        elif mar > config.MAR_NORMAL:
            return "CONCENTRADO", 90, f"MAR {mar:.3f} (hablando)"

        else:
            return "CONCENTRADO", 100, f"MAR {mar:.3f} OK ✓"

    # =========================================================================
    #  CLASIFICACIÓN FINAL
    # =========================================================================

    def clasificar(self, m):
        """
        Recibe las métricas crudas y devuelve una clasificación general
        por frame.
        """
        # Accesos seguros
        ear = m.get("ear", 0.30)
        ear_base = m.get("ear_base", 0.30)
        calibrado = m.get("calibrado", False)
        perclos = m.get("perclos", 0.0)
        bpm = m.get("parpadeos_min", 0.0)
        yaw = m.get("yaw", 0.0)
        pitch = m.get("pitch", 0.0)
        gaze_focus = m.get("gaze_focus", 0.0)
        gaze_dispersion = m.get("gaze_dispersion", 0.0)
        apertura = m.get("apertura", 0.30)
        mar = m.get("mar", 0.30)
        es_bostezo = m.get("es_bostezo", False)

        detalles = {}

        # Ejecutar cada clasificación
        estado_ear, score_ear, desc = self.clasificar_ear(ear, calibrado, ear_base)
        detalles["ear"] = {"estado": estado_ear, "score": score_ear, "desc": desc}

        estado_p, score_p, desc = self.clasificar_perclos(perclos)
        detalles["perclos"] = {"estado": estado_p, "score": score_p, "desc": desc}

        estado_b, score_b, desc = self.clasificar_parpadeos(bpm)
        detalles["parpadeos"] = {"estado": estado_b, "score": score_b, "desc": desc}

        estado_y, score_y, desc = self.clasificar_yaw(yaw)
        detalles["yaw"] = {"estado": estado_y, "score": score_y, "desc": desc}

        estado_pitch, score_pitch, desc = self.clasificar_pitch(pitch)
        detalles["pitch"] = {"estado": estado_pitch, "score": score_pitch, "desc": desc}

        estado_focus, score_focus, desc = self.clasificar_gaze_focus(gaze_focus)
        detalles["gaze_focus"] = {"estado": estado_focus, "score": score_focus, "desc": desc}

        estado_disp, score_disp, desc = self.clasificar_gaze_dispersion(gaze_dispersion)
        detalles["gaze_dispersion"] = {"estado": estado_disp, "score": score_disp, "desc": desc}

        estado_ap, score_ap, desc = self.clasificar_eye_opening(apertura)
        detalles["eye_opening"] = {"estado": estado_ap, "score": score_ap, "desc": desc}

        estado_mar, score_mar, desc = self.clasificar_mar(mar, es_bostezo)
        detalles["mar"] = {"estado": estado_mar, "score": score_mar, "desc": desc}

        # Score final ponderado
        score_final = (
            score_ear * self.pesos["ear"] +
            score_p * self.pesos["perclos"] +
            score_b * self.pesos["parpadeos_min"] +
            score_y * self.pesos["pose"] +
            score_pitch * self.pesos["pose"] +
            score_focus * self.pesos["gaze_focus"] +
            score_disp * self.pesos["gaze_dispersion"] +
            score_ap * self.pesos["eye_opening"] +
            score_mar * self.pesos["mar"]
        )

        # Evaluación final
        estados = [d["estado"] for d in detalles.values()]
        severos = estados.count("SEVERO")
        bajos = estados.count("BAJO")

        mirando_fuera = (
            detalles["yaw"]["estado"] == "SEVERO" or
            detalles["pitch"]["estado"] == "SEVERO"
        )

        if mirando_fuera:
            estado_final = "NO_CONCENTRADO"
            score_final = min(score_final, 55)

        elif severos >= 3 or score_final < 45:
            estado_final = "NO_CONCENTRADO"

        elif severos >= 1 or bajos >= 4 or score_final < 70:
            estado_final = "BAJA_ATENCION"

        else:
            estado_final = "CONCENTRADO"

        return {
            "estado": estado_final,
            "concentrado": estado_final == "CONCENTRADO",
            "score": score_final,
            "detalles": detalles,
            "metricas_severas": severos,
            "metricas_bajas": bajos,
            "mirando_fuera": mirando_fuera,
        }
