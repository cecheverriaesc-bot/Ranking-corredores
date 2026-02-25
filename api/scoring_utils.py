"""
Utilidades de Normalización para Sistema de Scoring Robusto
Implementa z-score winsorizado y normalización inversa para métricas.
"""
import statistics
from typing import List, Dict

def winsorize(values: List[float], lower_percentile: float = 5, upper_percentile: float = 95) -> List[float]:
    """
    Winsoriza una lista de valores reemplazando outliers extremos.
    
    Args:
        values: Lista de valores a winsorizar
        lower_percentile: Percentil inferior (default 5)
        upper_percentile: Percentil superior (default 95)
    
    Returns:
        Lista de valores winsorizada
    """
    if not values or len(values) < 3:
        return values
    
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    
    lower_idx = int(n * lower_percentile / 100)
    upper_idx = int(n * upper_percentile / 100)
    
    lower_bound = sorted_vals[lower_idx]
    upper_bound = sorted_vals[upper_idx]
    
    return [max(lower_bound, min(upper_bound, v)) for v in values]

def normalize_z_score(values: List[float], winsorize_outliers: bool = True) -> List[float]:
    """
    Normaliza valores usando z-score, opcionalmente con winsorización.
    Convierte a escala ~0-1 usando CDF aproximada (sigmoid).
    
    Args:
        values: Lista de valores a normalizar
        winsorize_outliers: Si True, aplica winsorización antes de z-score
    
    Returns:
        Lista de valores normalizados entre ~0 y 1
    """
    if not values or len(values) < 2:
        return [0.5] * len(values)  # Valor neutral si no hay suficientes datos
    
    # Winsorizar si se solicita
    if winsorize_outliers:
        values = winsorize(values)
    
    # Calcular media y desviación estándar
    mean = statistics.mean(values)
    stdev = statistics.stdev(values) if len(values) > 1 else 1.0
    
    if stdev == 0:
        return [0.5] * len(values)  # Todos iguales = neutral
    
    # Calcular z-scores
    z_scores = [(v - mean) / stdev for v in values]
    
    # Convertir a escala ~0-1 usando función sigmoide
    # sigmoid(z) = 1 / (1 + e^(-z))
    # Aproximación rápida: (tanh(z/2) + 1) / 2
    import math
    normalized = [(math.tanh(z / 2) + 1) / 2 for z in z_scores]
    
    return normalized

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
