"""
analyze_data.py  
Procesador de análisis de frames EN TIEMPO REAL.
Este módulo NO usa sesiones, NO usa base de datos y NO exporta CSV.
La API enviará los frames y este archivo devolverá el análisis.

Requiere:
    - pandas
    - numpy
"""

import pandas as pd
import numpy as np
from datetime import timedelta


# ============================================================
# 1. Analizar un lote de frames enviados por el frontend
# ============================================================

def analyze_frames(frames: list) -> dict:
    """
    Recibe una lista de diccionarios donde cada uno representa un frame.

    EJEMPLO DEL FRAME ESPERADO:
    {
        "frame_number": 1,
        "timestamp": 0.033,
        "elapsed_seconds": 0.033,
        "attention_score": 0.82,
        "attention_level": "concentrado",
        "ear_avg": 0.29,
        "perclos": 0.12,
        "blinks_per_minute": 18,
        "head_yaw": -5.2,
        "head_pitch": 3.1,
        "gaze_focus_ratio": 0.90,
        "gaze_dispersion": 0.08,
        "mar": 0.21,
        "is_blink": False,
        "is_yawn": False
    }
    """

    if not frames or len(frames) == 0:
        raise ValueError("No se recibieron frames para analizar.")

    df = pd.DataFrame(frames)

    duration = df["elapsed_seconds"].max()
    total_frames = len(df)

    attention_dist = df["attention_level"].value_counts(normalize=True) * 100

    score_stats = {
        "mean": df["attention_score"].mean(),
        "std": df["attention_score"].std(),
        "min": df["attention_score"].min(),
        "max": df["attention_score"].max(),
        "median": df["attention_score"].median(),
    }

    blinks = df["is_blink"].sum()
    yawns = df["is_yawn"].sum()

    severe_periods = find_distraction_periods(df)

    metric_means = {
        "ear_avg": df["ear_avg"].mean(),
        "perclos": df["perclos"].mean(),
        "blinks_per_minute": df["blinks_per_minute"].mean(),
        "head_yaw": df["head_yaw"].abs().mean(),
        "head_pitch": df["head_pitch"].abs().mean(),
        "gaze_focus_ratio": df["gaze_focus_ratio"].mean(),
        "gaze_dispersion": df["gaze_dispersion"].mean(),
        "mar": df["mar"].mean(),
    }

    return {
        "duration_seconds": float(duration),
        "duration_formatted": str(timedelta(seconds=int(duration))),
        "total_frames": total_frames,
        "fps_average": total_frames / duration if duration > 0 else 0,
        "attention_distribution": attention_dist.to_dict(),
        "score_statistics": score_stats,
        "total_blinks": int(blinks),
        "total_yawns": int(yawns),
        "distraction_periods": severe_periods,
        "metric_averages": metric_means,
    }


# ============================================================
# 2. Detectar períodos severos de desconcentración
# ============================================================

def find_distraction_periods(df: pd.DataFrame, min_duration_frames: int = 30) -> list:

    periods = []
    in_period = False
    start_idx = 0

    for idx, row in df.iterrows():
        severe = row["attention_level"] == "desconcentracion_severa"

        if severe and not in_period:
            in_period = True
            start_idx = idx

        elif not severe and in_period:
            in_period = False
            duration = idx - start_idx

            if duration >= min_duration_frames:
                periods.append({
                    "start_frame": int(df.loc[start_idx, "frame_number"]),
                    "end_frame": int(df.loc[idx - 1, "frame_number"]),
                    "duration_frames": int(duration),
                    "start_time": float(df.loc[start_idx, "elapsed_seconds"]),
                    "end_time": float(df.loc[idx - 1, "elapsed_seconds"]),
                })

    # Caso final si termina en severo
    if in_period:
        duration = len(df) - start_idx
        if duration >= min_duration_frames:
            periods.append({
                "start_frame": int(df.loc[start_idx, "frame_number"]),
                "end_frame": int(df.loc[len(df) - 1, "frame_number"]),
                "duration_frames": int(duration),
                "start_time": float(df.loc[start_idx, "elapsed_seconds"]),
                "end_time": float(df["elapsed_seconds"].max()),
            })

    return periods


# ============================================================
# (Opcional) Generar texto de reporte si se necesita
# ============================================================

def generate_report(analysis: dict) -> str:
    report = []
    report.append("=" * 60)
    report.append(f"📊 REPORTE DE ATENCIÓN — Análisis en tiempo real")
    report.append("=" * 60)
    report.append("")

    report.append("Duración:")
    report.append(f"  {analysis['duration_formatted']}")
    report.append(f"Frames totales: {analysis['total_frames']}")
    report.append(f"FPS promedio: {analysis['fps_average']:.1f}")
    report.append("")

    report.append("Distribución de atención:")
    for level, pct in analysis["attention_distribution"].items():
        report.append(f"  {level}: {pct:.1f}%")
    report.append("")

    return "\n".join(report)
