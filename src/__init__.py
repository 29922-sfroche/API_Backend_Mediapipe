"""
_initi.py -
Sistema de Monitoreo de Atención
================================

Módulos:
- config: Configuración y umbrales científicos
- metrics: Cálculo de métricas de atención
- classifier: Clasificación de niveles de atención
- main: Aplicación principal

Referencias científicas:
- Soukupová & Čech (2016): Real-Time Eye Blink Detection using Facial Landmarks
- U.S. DOT (1998): PERCLOS Drowsiness Monitoring Standard
- Bentivoglio et al. (1997): Normal Blink Rate Analysis
- Yang et al. (2018): Head Pose Estimation for Attention Detection
- Krejtz et al. (2019): Gaze Behavior Analysis
- Abtahi et al. (2014): Yawn Detection via MAR
"""

from .domain.config import (
    THRESHOLDS,
    PROCESSING_CONFIG,
    AttentionLevel,
    MediaPipeLandmarks,
    LANDMARKS
)

from .domain.metrics import MetricsCalculator
from .domain.classifier import AttentionClassifier

__version__ = '1.0.0'
__author__ = 'Attention Monitor System'

__all__ = [
    'THRESHOLDS',
    'PROCESSING_CONFIG',
    'AttentionLevel',
    'MediaPipeLandmarks',
    'LANDMARKS',
    'MetricsCalculator',
    'AttentionClassifier',
    'AttentionScore',
]