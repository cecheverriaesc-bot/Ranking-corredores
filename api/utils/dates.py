"""
Utilidades de Fecha para el Sistema de Ranking
Manejo consistente de boundaries de meses y timezone de Chile.
"""
from datetime import datetime, timedelta
from typing import Tuple
import calendar

# Timezone de Chile (considera DST automáticamente)
# Chile usa UTC-4 en verano (DST) y UTC-3 en invierno
CHILE_UTC_OFFSET_SUMMER = -3  # Noviembre - Marzo (DST)
CHILE_UTC_OFFSET_WINTER = -4  # Abril - Octubre (STD)


def get_chile_utc_offset(year: int, month: int) -> int:
    """
    Retorna el offset UTC para Chile según la fecha.
    
    Chile usa horario de verano (DST) desde aproximadamente
    el segundo sábado de septiembre hasta el segundo sábado de abril.
    
    Args:
        year: Año
        month: Mes (1-12)
    
    Returns:
        Offset en horas (-3 o -4)
    """
    # Simplificación: Mayo-Agosto = invierno (-4), resto = verano (-3)
    # Esta es una aproximación; para precisión completa usar pytz
    if 5 <= month <= 8:
        return CHILE_UTC_OFFSET_WINTER
    else:
        return CHILE_UTC_OFFSET_SUMMER


def get_month_boundaries(year: int, month: int) -> Tuple[str, str]:
    """
    Obtiene las fechas de inicio y fin de un mes para consultas SQL.
    
    Args:
        year: Año
        month: Mes (1-12)
    
    Returns:
        Tupla (start_date, end_date) en formato 'YYYY-MM-DD HH:MM:SS'
        - start_date: Primer día del mes 00:00:00
        - end_date: Primer día del mes siguiente 00:00:00 (exclusive)
    """
    if month < 1 or month > 12:
        raise ValueError(f"Month must be between 1 and 12, got {month}")
    
    # Inicio del mes
    start_date = f"{year}-{month:02d}-01 00:00:00"
    
    # Fin del mes (primer día del mes siguiente)
    if month == 12:
        next_year = year + 1
        next_month = 1
    else:
        next_year = year
        next_month = month + 1
    
    end_date = f"{next_year}-{next_month:02d}-01 00:00:00"
    
    return start_date, end_date


def get_month_boundaries_date_only(year: int, month: int) -> Tuple[str, str]:
    """
    Obtiene las fechas de inicio y fin de un mes (solo fecha, sin hora).
    
    Args:
        year: Año
        month: Mes (1-12)
    
    Returns:
        Tupla (start_date, end_date) en formato 'YYYY-MM-DD'
    """
    if month < 1 or month > 12:
        raise ValueError(f"Month must be between 1 and 12, got {month}")
    
    start_date = f"{year}-{month:02d}-01"
    
    if month == 12:
        next_year = year + 1
        next_month = 1
    else:
        next_year = year
        next_month = month + 1
    
    end_date = f"{next_year}-{next_month:02d}-01"
    
    return start_date, end_date


def get_partial_month_end(year: int, month: int, day: int) -> str:
    """
    Obtiene una fecha parcial dentro del mes para comparaciones year-over-year.
    
    Args:
        year: Año
        month: Mes (1-12)
        day: Día (1-31)
    
    Returns:
        Fecha en formato 'YYYY-MM-DD 23:59:59'
    """
    # Validar día máximo del mes
    max_day = calendar.monthrange(year, month)[1]
    actual_day = min(day, max_day)
    
    return f"{year}-{month:02d}-{actual_day:02d} 23:59:59"


def convert_to_chile_time(dt: datetime) -> datetime:
    """
    Convierte un datetime de UTC a hora de Chile.
    
    Args:
        dt: datetime en UTC
    
    Returns:
        datetime en hora de Chile
    """
    offset = get_chile_utc_offset(dt.year, dt.month)
    return dt + timedelta(hours=offset)


def format_chile_time(dt: datetime, format_str: str = "%d/%m/%Y %H:%M") -> str:
    """
    Formatea un datetime UTC como hora de Chile.
    
    Args:
        dt: datetime en UTC
        format_str: Formato de salida (default: "%d/%m/%Y %H:%M")
    
    Returns:
        String formateado en hora de Chile
    """
    chile_time = convert_to_chile_time(dt)
    return chile_time.strftime(format_str)


def get_current_chile_datetime() -> datetime:
    """
    Obtiene la fecha y hora actual en Chile.
    
    Returns:
        datetime en hora de Chile
    """
    now_utc = datetime.now()
    offset = get_chile_utc_offset(now_utc.year, now_utc.month)
    return now_utc + timedelta(hours=offset)


def is_current_month(year: int, month: int) -> bool:
    """
    Verifica si el año y mes corresponden al mes actual.
    
    Args:
        year: Año a verificar
        month: Mes a verificar (1-12)
    
    Returns:
        True si es el mes actual, False en caso contrario
    """
    now = get_current_chile_datetime()
    return year == now.year and month == now.month


def get_days_remaining_in_month(year: int, month: int) -> int:
    """
    Calcula los días restantes en el mes desde la fecha actual.
    
    Args:
        year: Año
        month: Mes (1-12)
    
    Returns:
        Número de días restantes
    """
    if not is_current_month(year, month):
        return 0
    
    now = get_current_chile_datetime()
    max_day = calendar.monthrange(year, month)[1]
    return max_day - now.day


def get_days_elapsed_in_month(year: int, month: int) -> int:
    """
    Calcula los días transcurridos en el mes hasta la fecha actual.
    
    Args:
        year: Año
        month: Mes (1-12)
    
    Returns:
        Número de días transcurridos
    """
    if not is_current_month(year, month):
        # Si es un mes pasado, retornar total de días
        return calendar.monthrange(year, month)[1]
    
    now = get_current_chile_datetime()
    return now.day
