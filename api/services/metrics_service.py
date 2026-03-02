"""
Servicios Centralizados para el Sistema de Ranking
Todos los cálculos de métricas deben usar estas funciones para garantizar consistencia.
"""
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import statistics
import math


# ===================================================================
# PILAR 1: NET RESERVATIONS CALCULATION
# ===================================================================

def calculate_net_reservations(gross: Optional[int], fallen: Optional[int]) -> int:
    """
    Calcula reservas netas = gross - fallen de manera consistente.
    
    Args:
        gross: Reservas brutas
        fallen: Reservas caídas
    
    Returns:
        Reservas netas (nunca negativo)
    """
    val_gross = int(gross or 0)
    val_fallen = int(fallen or 0)
    net = val_gross - val_fallen
    return max(0, net)  # Nunca permitir negativos


def validate_reservation_data(gross: Optional[int], fallen: Optional[int]) -> Tuple[bool, str]:
    """
    Valida datos de reservas para detectar inconsistencias.
    
    Args:
        gross: Reservas brutas
        fallen: Reservas caídas
    
    Returns:
        Tupla (es_valido, mensaje_error)
    """
    val_gross = int(gross or 0)
    val_fallen = int(fallen or 0)
    
    if val_gross < 0:
        return False, "Gross reservations cannot be negative"
    
    if val_fallen < 0:
        return False, "Fallen reservations cannot be negative"
    
    if val_fallen > val_gross:
        # Advertencia, no error - puede pasar en casos edge
        return True, f"Warning: fallen ({val_fallen}) > gross ({val_gross})"
    
    return True, "OK"


# ===================================================================
# PILAR 2: PERSONAL GOAL CALCULATION
# ===================================================================

def calculate_personal_goal(
    broker_id: int,
    historical_weight: float,
    contract_goal: int,
    active_brokers_count: int,
    minimum_goal: int = 5
) -> int:
    """
    Calcula la meta personal de un corredor basada en su peso histórico.
    
    Método unificado: Usa peso histórico global del broker.
    
    Args:
        broker_id: ID del corredor
        historical_weight: Peso histórico del broker (0-1)
        contract_goal: Meta total de contratos del mes
        active_brokers_count: Número de corredores activos
        minimum_goal: Meta mínima saludable (default: 5)
    
    Returns:
        Meta personal del corredor
    """
    # Si no tiene peso histórico, asignar mínimo proporcional
    if historical_weight == 0:
        historical_weight = 0.8 / max(active_brokers_count, 1)
    
    personal_meta = int(contract_goal * historical_weight)
    
    # Aplicar mínimo saludable
    return max(personal_meta, minimum_goal)


def calculate_historical_weight(
    broker_id: int,
    broker_historical_reservations: int,
    team_total_historical_reservations: int
) -> float:
    """
    Calcula el peso histórico de un broker basado en su contribución histórica.
    
    Args:
        broker_id: ID del corredor
        broker_historical_reservations: Reservas históricas del broker (últimos 6 meses)
        team_total_historical_reservations: Total histórico del equipo
    
    Returns:
        Peso histórico (0-1)
    """
    if team_total_historical_reservations == 0:
        return 0.0
    
    return broker_historical_reservations / team_total_historical_reservations


# ===================================================================
# PILAR 3: Z-SCORE NORMALIZATION (ROBUST)
# ===================================================================

def winsorize(
    values: List[float],
    lower_percentile: float = 5,
    upper_percentile: float = 95
) -> List[float]:
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
        return list(values)
    
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    
    lower_idx = int(n * lower_percentile / 100)
    upper_idx = int(n * upper_percentile / 100)
    
    # Prevenir índices fuera de rango
    lower_idx = max(0, min(lower_idx, n - 1))
    upper_idx = max(0, min(upper_idx, n - 1))
    
    lower_bound = sorted_vals[lower_idx]
    upper_bound = sorted_vals[upper_idx]
    
    return [max(lower_bound, min(upper_bound, v)) for v in values]


def get_robust_mean_std(
    values: List[float],
    use_iqr: bool = True
) -> Tuple[float, float]:
    """
    Calcula media y desviación estándar robustas usando IQR para truncar outliers.
    
    Args:
        values: Lista de valores
        use_iqr: Si True, usa IQR para truncar outliers antes de calcular
    
    Returns:
        Tupla (media, stdev)
    """
    if not values or len(values) < 2:
        return 0.0, 1.0
    
    if use_iqr:
        sorted_values = sorted(values)
        n = len(sorted_values)
        
        q1_idx = int(n * 0.25)
        q3_idx = int(n * 0.75)
        
        q1 = sorted_values[q1_idx]
        q3 = sorted_values[q3_idx]
        iqr = q3 - q1
        
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        # Truncar valores
        truncated = [max(lower_bound, min(v, upper_bound)) for v in values]
        mean = statistics.mean(truncated)
        stdev = statistics.stdev(truncated) if len(truncated) > 1 else 1.0
    else:
        mean = statistics.mean(values)
        stdev = statistics.stdev(values) if len(values) > 1 else 1.0
    
    return mean, stdev


def normalize_z_score_robust(
    values: List[float],
    inverse: bool = False,
    winsorize_outliers: bool = True,
    use_iqr: bool = True
) -> List[float]:
    """
    Normaliza valores usando z-score robusto con opción de inversión.
    
    Args:
        values: Lista de valores a normalizar
        inverse: Si True, invierte el score (para métricas donde menor es mejor)
        winsorize_outliers: Si True, aplica winsorización
        use_iqr: Si True, usa IQR para cálculo robusto de mean/std
    
    Returns:
        Lista de valores normalizados entre ~0 y 1
    """
    if not values or len(values) < 2:
        return [0.5] * len(values)
    
    # Winsorizar si se solicita
    if winsorize_outliers:
        values = winsorize(values)
    
    # Calcular media y desviación estándar robustas
    mean, stdev = get_robust_mean_std(values, use_iqr=use_iqr)
    
    if stdev == 0:
        return [0.5] * len(values)
    
    # Calcular z-scores
    z_scores = [(v - mean) / stdev for v in values]
    
    # Convertir a escala ~0-1 usando función sigmoide (tanh)
    normalized = [(math.tanh(z / 2) + 1) / 2 for z in z_scores]
    
    # Invertir si es necesario (para métricas donde menor es mejor)
    if inverse:
        normalized = [1 - n for n in normalized]
    
    return normalized


def normalize_z_score_simple(
    values: List[float],
    inverse: bool = False,
    winsorize_outliers: bool = True
) -> List[float]:
    """
    Normaliza valores usando z-score simple (sin IQR).
    Para compatibilidad con código legacy.
    
    Args:
        values: Lista de valores a normalizar
        inverse: Si True, invierte el score
        winsorize_outliers: Si True, aplica winsorización
    
    Returns:
        Lista de valores normalizados entre ~0 y 1
    """
    if not values or len(values) < 2:
        return [0.5] * len(values)
    
    if winsorize_outliers:
        values = winsorize(values)
    
    mean = statistics.mean(values)
    stdev = statistics.stdev(values) if len(values) > 1 else 1.0
    
    if stdev == 0:
        return [0.5] * len(values)
    
    z_scores = [(v - mean) / stdev for v in values]
    normalized = [(math.tanh(z / 2) + 1) / 2 for z in z_scores]
    
    if inverse:
        normalized = [1 - n for n in normalized]
    
    return normalized


# ===================================================================
# PILAR 4: LAPLACE SMOOTHING PARA TASAS
# ===================================================================

def calculate_rate_with_smoothing(
    numerator: int,
    denominator: int,
    smoothing_factor: int = 15
) -> float:
    """
    Calcula una tasa con suavizado de Laplace para evitar división por cero.
    
    Args:
        numerator: Numerador
        denominator: Denominador
        smoothing_factor: Factor de suavizado (default: 15)
    
    Returns:
        Tasa suavizada
    """
    if denominator <= 0:
        return 0.0
    
    return numerator / (denominator + smoothing_factor)


def validate_rate_data(
    numerator: int,
    denominator: int,
    max_possible_ratio: float = 1.0
) -> Tuple[bool, str]:
    """
    Valida datos para cálculo de tasas.
    
    Args:
        numerator: Numerador
        denominator: Denominador
        max_possible_ratio: Ratio máximo posible (default: 1.0 para 100%)
    
    Returns:
        Tupla (es_valido, mensaje_error)
    """
    if numerator < 0:
        return False, "Numerator cannot be negative"
    
    if denominator < 0:
        return False, "Denominator cannot be negative"
    
    if denominator > 0 and numerator > denominator * max_possible_ratio:
        return True, f"Warning: numerator ({numerator}) exceeds expected ratio"
    
    return True, "OK"


# ===================================================================
# PILAR 5: CONTRACT COUNTING
# ===================================================================

def count_contracts(
    contracts_data: List[Dict],
    only_new: bool = False,
    only_active: bool = False
) -> Dict[str, int]:
    """
    Cuenta contratos por corredor con filtros opcionales.
    
    Args:
        contracts_data: Lista de dicts con datos de contratos
        only_new: Si True, solo cuenta contratos nuevos (no renovaciones)
        only_active: Si True, solo cuenta contratos vigentes
    
    Returns:
        Dict {nombre_corredor: count}
    """
    contracts_by_broker = {}
    
    for contract in contracts_data:
        broker_name = contract.get('nombre_corredor')
        if not broker_name:
            continue
        
        # Filtro de solo nuevos
        if only_new and contract.get('tipo_renovacion') != 'Nuevo':
            continue
        
        # Filtro de solo vigentes
        if only_active and not contract.get('vigente', False):
            continue
        
        contracts_by_broker[broker_name] = contracts_by_broker.get(broker_name, 0) + 1
    
    return contracts_by_broker


# ===================================================================
# PILAR 6: SQUAD EMAIL VALIDATION
# ===================================================================

OFFICIAL_SQUADS = [
    "carlos.echeverria@assetplan.cl",
    "luis.gomez@assetplan.cl",
    "nataly.espinoza@assetplan.cl",
    "angely.rojo@assetplan.cl",
    "maria.chacin@assetplan.cl"
]


def validate_squad_email(email: Optional[str]) -> str:
    """
    Valida y normaliza el email de un squad.
    
    Args:
        email: Email del coordinador
    
    Returns:
        Email validado o default si no es válido
    """
    if not email:
        return OFFICIAL_SQUADS[0]
    
    email_normalized = email.lower().strip()
    
    if email_normalized in OFFICIAL_SQUADS:
        return email_normalized
    
    # Si no es un squad oficial, retornar el primero como default
    return OFFICIAL_SQUADS[0]


def get_official_squads() -> List[str]:
    """
    Retorna la lista oficial de squads.
    
    Returns:
        Lista de emails oficiales
    """
    return list(OFFICIAL_SQUADS)


# ===================================================================
# PILAR 7: GOAL CONFIGURATION
# ===================================================================

# Metas de reservas configuradas por mes
RESERVATION_GOALS = {
    (2026, 1): 1943,
    (2026, 2): 1878,
    (2026, 3): 1762,
    (2026, 4): 1480,
    (2026, 5): 1398,
    (2026, 6): 1403,
    (2026, 7): 1425,
    (2026, 8): 1476,
    (2026, 9): 1498,
    (2026, 10): 1684,
    (2026, 11): 1690,
    (2026, 12): 1689,
}

# Metas de contratos configuradas por mes
CONTRACT_GOALS = {
    (2026, 1): 1943,
    (2026, 2): 1878,
    (2026, 3): 1762,
    (2026, 4): 1480,
    (2026, 5): 1398,
    (2026, 6): 1403,
    (2026, 7): 1425,
    (2026, 8): 1476,
    (2026, 9): 1498,
    (2026, 10): 1684,
    (2026, 11): 1690,
    (2026, 12): 1689,
}


def get_reservation_goal(year: int, month: int) -> int:
    """
    Obtiene la meta de reservas para un mes específico.
    
    Args:
        year: Año
        month: Mes (1-12)
    
    Returns:
        Meta de reservas
    """
    return RESERVATION_GOALS.get((year, month), 2000)


def get_contract_goal(year: int, month: int) -> int:
    """
    Obtiene la meta de contratos para un mes específico.
    
    Args:
        year: Año
        month: Mes (1-12)
    
    Returns:
        Meta de contratos
    """
    return CONTRACT_GOALS.get((year, month), 2000)


def update_goal_config(
    year: int,
    month: int,
    reservation_goal: Optional[int] = None,
    contract_goal: Optional[int] = None
) -> None:
    """
    Actualiza la configuración de metas para un mes.
    
    Args:
        year: Año
        month: Mes
        reservation_goal: Nueva meta de reservas (opcional)
        contract_goal: Nueva meta de contratos (opcional)
    """
    if reservation_goal is not None:
        RESERVATION_GOALS[(year, month)] = reservation_goal
    
    if contract_goal is not None:
        CONTRACT_GOALS[(year, month)] = contract_goal
