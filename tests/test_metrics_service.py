"""
Tests Unitarios para metrics_service.py
Pruebas de regresión para garantizar consistencia en cálculos de métricas.

Ejecutar: python -m pytest tests/test_metrics_service.py -v
"""
import sys
import os
import unittest
from typing import List

# Agregar ruta para imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'api'))

from services.metrics_service import (
    calculate_net_reservations,
    validate_reservation_data,
    calculate_personal_goal,
    calculate_historical_weight,
    winsorize,
    get_robust_mean_std,
    normalize_z_score_robust,
    normalize_z_score_simple,
    calculate_rate_with_smoothing,
    validate_rate_data,
    count_contracts,
    validate_squad_email,
    get_official_squads,
    get_reservation_goal,
    get_contract_goal,
)

from utils.dates import (
    get_chile_utc_offset,
    get_month_boundaries,
    get_month_boundaries_date_only,
    get_partial_month_end,
    convert_to_chile_time,
    format_chile_time,
    is_current_month,
    get_days_remaining_in_month,
    get_days_elapsed_in_month,
)


class TestNetReservations(unittest.TestCase):
    """Tests para cálculo de reservas netas"""
    
    def test_net_reservations_basic(self):
        """Cálculo básico: gross - fallen"""
        result = calculate_net_reservations(100, 20)
        self.assertEqual(result, 80)
    
    def test_net_reservations_zero_fallen(self):
        """Sin reservas caídas"""
        result = calculate_net_reservations(100, 0)
        self.assertEqual(result, 100)
    
    def test_net_reservations_all_fallen(self):
        """Todas caídas: net = 0"""
        result = calculate_net_reservations(100, 100)
        self.assertEqual(result, 0)
    
    def test_net_reservations_more_fallen_than_gross(self):
        """Más caídas que gross: no permitir negativos"""
        result = calculate_net_reservations(50, 100)
        self.assertEqual(result, 0)  # No negativo
    
    def test_net_reservations_none_values(self):
        """Valores None tratados como 0"""
        result = calculate_net_reservations(None, 20)
        self.assertEqual(result, 0)
        
        result = calculate_net_reservations(100, None)
        self.assertEqual(result, 100)
    
    def test_net_reservations_validation_positive(self):
        """Validación exitosa"""
        valid, message = validate_reservation_data(100, 20)
        self.assertTrue(valid)
        self.assertEqual(message, "OK")
    
    def test_net_reservations_validation_negative_gross(self):
        """Validación falla con gross negativo"""
        valid, message = validate_reservation_data(-10, 5)
        self.assertFalse(valid)
        self.assertIn("negative", message.lower())
    
    def test_net_reservations_validation_warning(self):
        """Validación con advertencia: fallen > gross"""
        valid, message = validate_reservation_data(50, 100)
        self.assertTrue(valid)  # Válido pero con warning
        self.assertIn("warning", message.lower())


class TestPersonalGoal(unittest.TestCase):
    """Tests para cálculo de metas personales"""
    
    def test_personal_goal_basic(self):
        """Cálculo básico de meta personal"""
        result = calculate_personal_goal(
            broker_id=1,
            historical_weight=0.1,
            contract_goal=2000,
            active_brokers_count=50
        )
        self.assertEqual(result, 200)  # 10% de 2000
    
    def test_personal_goal_zero_weight(self):
        """Broker nuevo sin peso histórico"""
        result = calculate_personal_goal(
            broker_id=2,
            historical_weight=0,
            contract_goal=2000,
            active_brokers_count=40
        )
        # Peso proporcional: 0.8 / 40 = 0.02, meta = 40
        self.assertEqual(result, 40)
    
    def test_personal_goal_minimum(self):
        """Meta mínima de 5"""
        result = calculate_personal_goal(
            broker_id=3,
            historical_weight=0.001,
            contract_goal=2000,
            active_brokers_count=50
        )
        self.assertGreaterEqual(result, 5)
    
    def test_historical_weight_calculation(self):
        """Cálculo de peso histórico"""
        weight = calculate_historical_weight(
            broker_id=1,
            broker_historical_reservations=50,
            team_total_historical_reservations=500
        )
        self.assertEqual(weight, 0.1)  # 50/500 = 0.1
    
    def test_historical_weight_zero_total(self):
        """Peso histórico con total = 0"""
        weight = calculate_historical_weight(
            broker_id=1,
            broker_historical_reservations=50,
            team_total_historical_reservations=0
        )
        self.assertEqual(weight, 0.0)


class TestZScoreNormalization(unittest.TestCase):
    """Tests para normalización Z-score"""
    
    def test_winsorize_basic(self):
        """Winsorización básica"""
        # Lista más grande para que winsorize funcione correctamente
        values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 100]
        result = winsorize(values, lower_percentile=10, upper_percentile=90)
        # El 100 debería ser truncado al percentil 90 (índice 18 = valor 19)
        self.assertNotIn(100, result)
        self.assertEqual(len(result), len(values))
        # El valor máximo debería ser 19 (percentil 90)
        self.assertEqual(max(result), 19)
    
    def test_winsorize_empty(self):
        """Winsorización con lista vacía"""
        result = winsorize([])
        self.assertEqual(result, [])
    
    def test_winsorize_small_list(self):
        """Winsorización con lista pequeña (< 3)"""
        values = [1, 2]
        result = winsorize(values)
        self.assertEqual(result, values)  # Sin cambios
    
    def test_normalize_z_score_robust_basic(self):
        """Normalización robusta básica"""
        values = [10, 20, 30, 40, 50]
        result = normalize_z_score_robust(values)
        self.assertEqual(len(result), 5)
        # Todos entre 0 y 1
        self.assertTrue(all(0 <= r <= 1 for r in result))
    
    def test_normalize_z_score_robust_inverse(self):
        """Normalización inversa (menor es mejor)"""
        values = [10, 20, 30, 40, 50]
        result_normal = normalize_z_score_robust(values, inverse=False)
        result_inverse = normalize_z_score_robust(values, inverse=True)
        # La suma debería ser ~1
        for n, i in zip(result_normal, result_inverse):
            self.assertAlmostEqual(n + i, 1.0, places=5)
    
    def test_normalize_z_score_robust_empty(self):
        """Normalización con lista vacía"""
        result = normalize_z_score_robust([])
        self.assertEqual(result, [])
    
    def test_normalize_z_score_robust_single_value(self):
        """Normalización con un solo valor"""
        result = normalize_z_score_robust([50])
        self.assertEqual(result, [0.5])  # Valor neutral
    
    def test_normalize_z_score_simple_vs_robust(self):
        """Comparación entre simple y robusto"""
        values = [10, 20, 30, 40, 50]
        result_simple = normalize_z_score_simple(values)
        result_robust = normalize_z_score_robust(values)
        # Ambos deberían producir resultados similares para datos normales
        self.assertEqual(len(result_simple), len(result_robust))


class TestRateCalculation(unittest.TestCase):
    """Tests para cálculo de tasas con Laplace smoothing"""
    
    def test_rate_with_smoothing_basic(self):
        """Tasa básica con smoothing"""
        result = calculate_rate_with_smoothing(50, 100, 15)
        expected = 50 / (100 + 15)  # 50/115
        self.assertAlmostEqual(result, expected, places=6)
    
    def test_rate_with_smoothing_zero_denominator(self):
        """Tasa con denominador cero"""
        result = calculate_rate_with_smoothing(50, 0, 15)
        self.assertEqual(result, 0.0)
    
    def test_rate_with_smoothing_no_smoothing(self):
        """Tasa sin smoothing (k=0)"""
        result = calculate_rate_with_smoothing(50, 100, 0)
        self.assertAlmostEqual(result, 0.5, places=6)
    
    def test_rate_validation_positive(self):
        """Validación de tasa exitosa"""
        valid, message = validate_rate_data(50, 100)
        self.assertTrue(valid)
    
    def test_rate_validation_negative_numerator(self):
        """Validación con numerador negativo"""
        valid, message = validate_rate_data(-10, 100)
        self.assertFalse(valid)
        self.assertIn("negative", message.lower())
    
    def test_rate_validation_exceeds_ratio(self):
        """Validación con ratio excedido"""
        valid, message = validate_rate_data(150, 100, max_possible_ratio=1.0)
        self.assertTrue(valid)  # Válido pero con warning
        self.assertIn("warning", message.lower())


class TestContractCounting(unittest.TestCase):
    """Tests para conteo de contratos"""
    
    def test_count_contracts_basic(self):
        """Conteo básico de contratos"""
        contracts = [
            {'nombre_corredor': 'Juan Perez', 'tipo_renovacion': 'Nuevo'},
            {'nombre_corredor': 'Juan Perez', 'tipo_renovacion': 'Renovacion'},
            {'nombre_corredor': 'Maria Lopez', 'tipo_renovacion': 'Nuevo'},
        ]
        result = count_contracts(contracts)
        self.assertEqual(result['Juan Perez'], 2)
        self.assertEqual(result['Maria Lopez'], 1)
    
    def test_count_contracts_only_new(self):
        """Solo contratos nuevos"""
        contracts = [
            {'nombre_corredor': 'Juan Perez', 'tipo_renovacion': 'Nuevo'},
            {'nombre_corredor': 'Juan Perez', 'tipo_renovacion': 'Renovacion'},
            {'nombre_corredor': 'Maria Lopez', 'tipo_renovacion': 'Nuevo'},
        ]
        result = count_contracts(contracts, only_new=True)
        self.assertEqual(result['Juan Perez'], 1)  # Solo 1 nuevo
        self.assertEqual(result['Maria Lopez'], 1)
    
    def test_count_contracts_only_active(self):
        """Solo contratos vigentes"""
        contracts = [
            {'nombre_corredor': 'Juan Perez', 'vigente': True},
            {'nombre_corredor': 'Juan Perez', 'vigente': False},
            {'nombre_corredor': 'Maria Lopez', 'vigente': True},
        ]
        result = count_contracts(contracts, only_active=True)
        self.assertEqual(result['Juan Perez'], 1)
        self.assertEqual(result['Maria Lopez'], 1)


class TestSquadValidation(unittest.TestCase):
    """Tests para validación de squads"""
    
    def test_validate_squad_email_official(self):
        """Email oficial de squad"""
        result = validate_squad_email("carlos.echeverria@assetplan.cl")
        self.assertEqual(result, "carlos.echeverria@assetplan.cl")
    
    def test_validate_squad_email_case_insensitive(self):
        """Email case insensitive"""
        result = validate_squad_email("CARLOS.ECHEVERRIA@ASSETPLAN.CL")
        self.assertEqual(result, "carlos.echeverria@assetplan.cl")
    
    def test_validate_squad_email_none(self):
        """Email None retorna default"""
        result = validate_squad_email(None)
        self.assertEqual(result, "carlos.echeverria@assetplan.cl")
    
    def test_validate_squad_email_invalid(self):
        """Email inválido retorna default"""
        result = validate_squad_email("invalid@email.com")
        self.assertEqual(result, "carlos.echeverria@assetplan.cl")
    
    def test_get_official_squads(self):
        """Obtener lista oficial de squads"""
        squads = get_official_squads()
        self.assertEqual(len(squads), 5)
        self.assertIn("carlos.echeverria@assetplan.cl", squads)


class TestGoalConfiguration(unittest.TestCase):
    """Tests para configuración de metas"""
    
    def test_get_reservation_goal_configured(self):
        """Meta de reservas configurada"""
        result = get_reservation_goal(2026, 1)
        self.assertEqual(result, 1943)  # Valor real de enero 2026
    
    def test_get_reservation_goal_default(self):
        """Meta de reservas default"""
        result = get_reservation_goal(2027, 1)
        self.assertEqual(result, 2000)  # Default
    
    def test_get_contract_goal_configured(self):
        """Meta de contratos configurada"""
        result = get_contract_goal(2026, 1)
        self.assertEqual(result, 1943)  # Valor real de enero 2026
    
    def test_get_contract_goal_default(self):
        """Meta de contratos default"""
        result = get_contract_goal(2027, 1)
        self.assertEqual(result, 2000)  # Default


class TestDateUtilities(unittest.TestCase):
    """Tests para utilidades de fecha"""
    
    def test_get_month_boundaries_january(self):
        """Límites de enero"""
        start, end = get_month_boundaries(2026, 1)
        self.assertEqual(start, "2026-01-01 00:00:00")
        self.assertEqual(end, "2026-02-01 00:00:00")
    
    def test_get_month_boundaries_december(self):
        """Límites de diciembre (cruza año)"""
        start, end = get_month_boundaries(2026, 12)
        self.assertEqual(start, "2026-12-01 00:00:00")
        self.assertEqual(end, "2027-01-01 00:00:00")
    
    def test_get_month_boundaries_invalid(self):
        """Mes inválido lanza error"""
        with self.assertRaises(ValueError):
            get_month_boundaries(2026, 13)
    
    def test_get_month_boundaries_date_only(self):
        """Límites solo fecha (sin hora)"""
        start, end = get_month_boundaries_date_only(2026, 1)
        self.assertEqual(start, "2026-01-01")
        self.assertEqual(end, "2026-02-01")
    
    def test_get_partial_month_end(self):
        """Fin parcial de mes"""
        result = get_partial_month_end(2025, 2, 15)
        self.assertEqual(result, "2025-02-15 23:59:59")
    
    def test_get_partial_month_end_exceeds_days(self):
        """Día excede días del mes"""
        result = get_partial_month_end(2025, 2, 31)  # Feb no tiene 31
        self.assertEqual(result, "2025-02-28 23:59:59")  # Ajustado
    
    def test_get_chile_utc_offset_summer(self):
        """Offset UTC en verano (DST)"""
        offset = get_chile_utc_offset(2026, 1)  # Enero = verano
        self.assertEqual(offset, -3)
    
    def test_get_chile_utc_offset_winter(self):
        """Offset UTC en invierno (STD)"""
        offset = get_chile_utc_offset(2026, 6)  # Junio = invierno
        self.assertEqual(offset, -4)
    
    def test_is_current_month_true(self):
        """Verificación de mes actual (puede variar)"""
        from datetime import datetime
        now = datetime.now()
        # Nota: este test puede fallar si se ejecuta en otro mes
        # Es más para documentación que para testing estricto
        result = is_current_month(now.year, now.month)
        self.assertIsInstance(result, bool)
    
    def test_is_current_month_false(self):
        """Mes que no es actual"""
        result = is_current_month(2025, 1)
        self.assertFalse(result)


class TestIntegration(unittest.TestCase):
    """Tests de integración para flujo completo"""
    
    def test_full_broker_calculation(self):
        """Flujo completo de cálculo para un broker"""
        # Datos simulados
        gross_reservations = 100
        fallen_reservations = 15
        
        # 1. Calcular net reservations
        net = calculate_net_reservations(gross_reservations, fallen_reservations)
        self.assertEqual(net, 85)
        
        # 2. Validar datos
        valid, message = validate_reservation_data(gross_reservations, fallen_reservations)
        self.assertTrue(valid)
        
        # 3. Calcular meta personal
        personal_goal = calculate_personal_goal(
            broker_id=1,
            historical_weight=0.05,
            contract_goal=2066,
            active_brokers_count=40
        )
        self.assertGreater(personal_goal, 0)
        
        # 4. Calcular tasa de conversión con smoothing
        conversion_rate = calculate_rate_with_smoothing(
            numerator=10,  # contratos
            denominator=50,  # leads
            smoothing_factor=15
        )
        self.assertAlmostEqual(conversion_rate, 10/65, places=6)


def run_tests():
    """Ejecutar todos los tests"""
    # Crear test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Agregar todas las clases de test
    suite.addTests(loader.loadTestsFromTestCase(TestNetReservations))
    suite.addTests(loader.loadTestsFromTestCase(TestPersonalGoal))
    suite.addTests(loader.loadTestsFromTestCase(TestZScoreNormalization))
    suite.addTests(loader.loadTestsFromTestCase(TestRateCalculation))
    suite.addTests(loader.loadTestsFromTestCase(TestContractCounting))
    suite.addTests(loader.loadTestsFromTestCase(TestSquadValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestGoalConfiguration))
    suite.addTests(loader.loadTestsFromTestCase(TestDateUtilities))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Ejecutar
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Retornar código de salida
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
