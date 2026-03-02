"""
Utilidades de Normalización para Sistema de Scoring Robusto
Implementa z-score winsorizado y normalización inversa para métricas.

DEPRECATED: Este archivo mantiene compatibilidad con código legacy.
NUEVO CÓDIGO debe usar: api.services.metrics_service
"""
import statistics
import math
from typing import List, Dict

# Importar desde servicios centralizados para compatibilidad
from services.metrics_service import (
    winsorize,
    normalize_z_score_robust,
    normalize_z_score_simple,
)


def normalize_z_score(values: List[float], winsorize_outliers: bool = True) -> List[float]:
    """
    Normaliza valores usando z-score, opcionalmente con winsorización.
    Convierte a escala ~0-1 usando CDF aproximada (sigmoid).
    
    DEPRECATED: Usar normalize_z_score_robust desde services.metrics_service
    
    Args:
        values: Lista de valores a normalizar
        winsorize_outliers: Si True, aplica winsorización antes de z-score

    Returns:
        Lista de valores normalizados entre ~0 y 1
    """
    # Usar implementación simple para compatibilidad
    return normalize_z_score_simple(values, inverse=False, winsorize_outliers=winsorize_outliers)


def normalize_inverse(values: List[float], winsorize_outliers: bool = True) -> List[float]:
    """
    Normaliza valores donde MENOR ES MEJOR (tiempos, errores, cancelaciones).

    Args:
        values: Lista de valores a normalizar
        winsorize_outliers: Si True, aplica winsorización

    Returns:
        Lista de valores normalizados e invertidos
    """
    normalized = normalize_z_score(values, winsorize_outliers)
    return [1 - n for n in normalized]


def calculate_weighted_score(metrics: Dict[str, float], weights: Dict[str, float]) -> float:
    """
    Calcula score ponderado a partir de métricas normalizadas.

    Args:
        metrics: Dict con {nombre_metrica: valor_normalizado}
        weights: Dict con {nombre_metrica: peso_en_puntos}

    Returns:
        Score total ponderado
    """
    total = 0.0
    for metric_name, weight in weights.items():
        metric_value = metrics.get(metric_name, 0.0)
        total += metric_value * weight

    return total


# ===================================================================
# FUNCIONES DELEGADAS A SERVICIOS CENTRALIZADOS
# ===================================================================

def calculate_net_reservations(gross, fallen):
    """
    Calcula reservas netas = gross - fallen.
    Delegado a services.metrics_service.calculate_net_reservations
    """
    from services.metrics_service import calculate_net_reservations as calc
    return calc(gross, fallen)


def validate_reservation_data(gross, fallen):
    """
    Valida datos de reservas.
    Delegado a services.metrics_service.validate_reservation_data
    """
    from services.metrics_service import validate_reservation_data as val
    return val(gross, fallen)
