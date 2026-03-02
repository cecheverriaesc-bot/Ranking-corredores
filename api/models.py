"""
Modelos Pydantic para Validación de Datos del Sistema de Ranking
Proporciona validación de entrada/salida para todas las APIs.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime


class BaseValidator:
    """Clase base para validadores simples sin dependencias externas"""
    
    @staticmethod
    def validate_int(value: Any, allow_none: bool = False) -> Optional[int]:
        """Valida y convierte un valor a entero"""
        if value is None:
            return None if allow_none else 0
        try:
            return int(value)
        except (ValueError, TypeError):
            return 0 if not allow_none else None
    
    @staticmethod
    def validate_float(value: Any, allow_none: bool = False) -> Optional[float]:
        """Valida y convierte un valor a float"""
        if value is None:
            return None if allow_none else 0.0
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0.0 if not allow_none else None
    
    @staticmethod
    def validate_string(value: Any, allow_none: bool = False, default: str = "") -> Optional[str]:
        """Valida y convierte un valor a string"""
        if value is None:
            return None if allow_none else default
        return str(value)
    
    @staticmethod
    def validate_positive_int(value: Any, min_val: int = 0, max_val: int = None) -> int:
        """Valida que sea un entero positivo dentro de rango"""
        int_val = BaseValidator.validate_int(value)
        if int_val < min_val:
            return min_val
        if max_val is not None and int_val > max_val:
            return max_val
        return int_val
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validación simple de email"""
        if not email:
            return False
        return '@' in email and '.' in email.split('@')[-1]
    
    @staticmethod
    def validate_date_range(year: int, month: int) -> tuple:
        """Valida rango de fechas"""
        year = BaseValidator.validate_positive_int(year, min_val=2020, max_val=2030)
        month = BaseValidator.validate_positive_int(month, min_val=1, max_val=12)
        return year, month


class ReservationDataValidator(BaseValidator):
    """Validador para datos de reservas"""
    
    @staticmethod
    def validate(gross: Any, fallen: Any) -> dict:
        """
        Valida datos de reservas y retorna valores validados
        
        Returns:
            dict con:
                - valid: bool
                - gross: int validado
                - fallen: int validado
                - net: int calculado
                - errors: lista de errores
                - warnings: lista de advertencias
        """
        result = {
            'valid': True,
            'gross': 0,
            'fallen': 0,
            'net': 0,
            'errors': [],
            'warnings': []
        }
        
        # Validar gross
        gross_val = BaseValidator.validate_int(gross, allow_none=True)
        if gross_val is None:
            result['errors'].append("Gross reservations cannot be null")
            result['valid'] = False
            return result
        
        if gross_val < 0:
            result['errors'].append("Gross reservations cannot be negative")
            result['valid'] = False
            return result
        
        # Validar fallen
        fallen_val = BaseValidator.validate_int(fallen, allow_none=True)
        if fallen_val is None:
            result['errors'].append("Fallen reservations cannot be null")
            result['valid'] = False
            return result
        
        if fallen_val < 0:
            result['errors'].append("Fallen reservations cannot be negative")
            result['valid'] = False
            return result
        
        # Calcular net
        net_val = gross_val - fallen_val
        
        # Advertencia si fallen > gross
        if fallen_val > gross_val:
            result['warnings'].append(
                f"Warning: fallen ({fallen_val}) > gross ({gross_val})"
            )
            net_val = 0  # No permitir negativos
        
        result['gross'] = gross_val
        result['fallen'] = fallen_val
        result['net'] = net_val
        
        return result


class BrokerDataValidator(BaseValidator):
    """Validador para datos de corredores"""
    
    @staticmethod
    def validate_broker_profile(data: dict) -> dict:
        """Valida perfil completo de corredor"""
        result = {
            'valid': True,
            'data': {},
            'errors': [],
            'warnings': []
        }
        
        # Campos requeridos
        required_fields = ['name', 'val']
        for field in required_fields:
            if field not in data or data[field] is None:
                result['errors'].append(f"Missing required field: {field}")
                result['valid'] = False
        
        if not result['valid']:
            return result
        
        # Validar campos
        result['data'] = {
            'name': BaseValidator.validate_string(data.get('name')),
            'val': BaseValidator.validate_positive_int(data.get('val'), min_val=0),
            'fallen': BaseValidator.validate_positive_int(data.get('fallen', 0), min_val=0),
            'leads': BaseValidator.validate_positive_int(data.get('leads', 0), min_val=0),
            'agendas': BaseValidator.validate_positive_int(data.get('agendas', 0), min_val=0),
            'contracts': BaseValidator.validate_positive_int(data.get('contracts', 0), min_val=0),
            'personalMeta': BaseValidator.validate_positive_int(data.get('personalMeta', 0), min_val=0),
        }
        
        # Validar email de coordinador si existe
        if 'coord' in data and data['coord']:
            if not BaseValidator.validate_email(data['coord']):
                result['warnings'].append(f"Invalid coordinator email: {data['coord']}")
            result['data']['coord'] = data['coord']
        
        # Validar consistencia de reservas
        reservation_check = ReservationDataValidator.validate(
            result['data']['val'] + result['data']['fallen'],
            result['data']['fallen']
        )
        if not reservation_check['valid']:
            result['errors'].extend(reservation_check['errors'])
            result['valid'] = False
        result['warnings'].extend(reservation_check['warnings'])
        
        return result


class GoalValidator(BaseValidator):
    """Validador para metas y objetivos"""
    
    # Metas configuradas oficiales
    RESERVATION_GOALS = {
        (2026, 1): 1928,
        (2026, 2): 2174,
    }
    
    CONTRACT_GOALS = {
        (2026, 1): 1928,
        (2026, 2): 2066,
    }
    
    @staticmethod
    def validate_goal_params(year: int, month: int, goal_type: str = 'reservation') -> dict:
        """Valida parámetros de metas"""
        result = {
            'valid': True,
            'year': 0,
            'month': 0,
            'goal': 0,
            'errors': []
        }
        
        # Validar año y mes
        year, month = BaseValidator.validate_date_range(year, month)
        result['year'] = year
        result['month'] = month
        
        # Obtener meta según tipo
        if goal_type == 'reservation':
            goal = GoalValidator.RESERVATION_GOALS.get((year, month), 2000)
        elif goal_type == 'contract':
            goal = GoalValidator.CONTRACT_GOALS.get((year, month), 2000)
        else:
            result['errors'].append(f"Invalid goal type: {goal_type}")
            result['valid'] = False
            return result
        
        result['goal'] = goal
        return result
    
    @staticmethod
    def validate_personal_goal(
        broker_weight: float,
        team_goal: int,
        active_brokers: int
    ) -> dict:
        """Valida cálculo de meta personal"""
        result = {
            'valid': True,
            'goal': 0,
            'errors': [],
            'warnings': []
        }
        
        # Validar peso
        weight = BaseValidator.validate_float(broker_weight)
        if weight < 0 or weight > 1:
            result['warnings'].append(
                f"Broker weight ({weight}) outside normal range [0, 1]"
            )
            weight = max(0, min(1, weight))  # Clamp
        
        # Si no tiene peso, asignar mínimo proporcional
        if weight == 0:
            weight = 0.8 / max(active_brokers, 1)
            result['warnings'].append(
                f"New broker: assigned proportional weight {weight:.4f}"
            )
        
        # Calcular meta
        goal = int(team_goal * weight)
        
        # Aplicar mínimo saludable
        if goal < 5:
            result['warnings'].append(
                f"Goal ({goal}) below minimum, setting to 5"
            )
            goal = 5
        
        result['goal'] = goal
        return result


class RateValidator(BaseValidator):
    """Validador para tasas y conversiones"""
    
    @staticmethod
    def validate_rate(numerator: Any, denominator: Any, max_ratio: float = 1.0) -> dict:
        """
        Valida cálculo de tasa con Laplace smoothing
        
        Returns:
            dict con:
                - valid: bool
                - rate: float calculado con smoothing
                - raw_rate: float sin smoothing
                - errors: lista de errores
                - warnings: lista de advertencias
        """
        result = {
            'valid': True,
            'rate': 0.0,
            'raw_rate': 0.0,
            'errors': [],
            'warnings': []
        }
        
        num = BaseValidator.validate_int(numerator)
        denom = BaseValidator.validate_int(denominator)
        
        if num < 0:
            result['errors'].append("Numerator cannot be negative")
            result['valid'] = False
            return result
        
        if denom < 0:
            result['errors'].append("Denominator cannot be negative")
            result['valid'] = False
            return result
        
        # Calcular tasa raw (sin smoothing)
        raw_rate = num / denom if denom > 0 else 0.0
        result['raw_rate'] = raw_rate
        
        # Calcular tasa con Laplace smoothing (k=15)
        smoothing_k = 15
        rate = num / (denom + smoothing_k) if denom > 0 else 0.0
        result['rate'] = rate
        
        # Advertencias
        if denom > 0 and num > denom * max_ratio:
            result['warnings'].append(
                f"Rate ({raw_rate:.2f}) exceeds expected maximum ({max_ratio})"
            )
        
        return result


class APIResponseValidator(BaseValidator):
    """Validador para respuestas de API"""
    
    @staticmethod
    def validate_ranking_response(data: dict) -> dict:
        """Valida respuesta de API de ranking"""
        result = {
            'valid': True,
            'data': {},
            'errors': [],
            'warnings': []
        }
        
        # Campos requeridos
        required_fields = ['ranking', 'last_update']
        for field in required_fields:
            if field not in data:
                result['errors'].append(f"Missing required field: {field}")
                result['valid'] = False
        
        if not result['valid']:
            return result
        
        # Validar ranking
        if not isinstance(data.get('ranking'), list):
            result['errors'].append("Field 'ranking' must be a list")
            result['valid'] = False
            return result
        
        # Validar cada broker en el ranking
        validated_brokers = []
        for i, broker in enumerate(data['ranking']):
            broker_validation = BrokerDataValidator.validate_broker_profile(broker)
            if broker_validation['valid']:
                validated_brokers.append(broker_validation['data'])
            else:
                result['warnings'].append(
                    f"Invalid broker at index {i}: {broker_validation['errors']}"
                )
        
        result['data'] = {
            **data,
            'ranking': validated_brokers
        }
        result['warnings'].extend([
            w for bv in data['ranking']
            if hasattr(bv, 'warnings')
            for w in bv.warnings
        ])
        
        return result
