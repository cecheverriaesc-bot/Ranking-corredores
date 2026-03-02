#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Verificación de Regresión - Sistema de Métricas

Compara los resultados de los cálculos antes y después de la migración
a servicios centralizados para garantizar consistencia.

Ejecución:
    python scripts/verify_regression.py

Salida:
    - Reporte detallado de diferencias
    - Código de salida: 0 (éxito) / 1 (diferencias encontradas)
"""
import sys
import os
import json
from datetime import datetime
from typing import Dict, List, Any, Tuple

# Configurar UTF-8 para salida en Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Agregar rutas para imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'api'))

from services.metrics_service import (
    calculate_net_reservations,
    calculate_personal_goal,
    normalize_z_score_robust,
    calculate_rate_with_smoothing,
    get_reservation_goal,
    get_contract_goal,
)

from utils.dates import (
    get_month_boundaries,
    format_chile_time,
)


class RegressionVerifier:
    """Verificador de regresión para métricas"""
    
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'tests': [],
            'passed': 0,
            'failed': 0,
            'warnings': 0
        }
    
    def add_result(self, name: str, passed: bool, details: str = "", warning: bool = False):
        """Agregar resultado de test"""
        self.results['tests'].append({
            'name': name,
            'passed': passed,
            'details': details,
            'warning': warning
        })
        
        if passed:
            if warning:
                self.results['warnings'] += 1
            else:
                self.results['passed'] += 1
        else:
            self.results['failed'] += 1
    
    def verify_net_reservations(self):
        """Verificar cálculo de reservas netas"""
        print("\n" + "="*60)
        print("VERIFICANDO: Net Reservations")
        print("="*60)
        
        test_cases = [
            # (gross, fallen, expected_net, description)
            (100, 20, 80, "Caso normal"),
            (50, 0, 50, "Sin caídas"),
            (100, 100, 0, "Todas caídas"),
            (50, 100, 0, "Caídas > Gross (no negativo)"),
            (0, 0, 0, "Ambos cero"),
        ]
        
        for gross, fallen, expected, description in test_cases:
            result = calculate_net_reservations(gross, fallen)
            passed = result == expected
            self.add_result(
                name=f"Net: {description}",
                passed=passed,
                details=f"gross={gross}, fallen={fallen}, expected={expected}, got={result}"
            )
            status = "PASS" if passed else "FAIL"
            print(f"  [{status}] {description}: {result} (expected {expected})")
    
    def verify_personal_goals(self):
        """Verificar cálculo de metas personales"""
        print("\n" + "="*60)
        print("VERIFICANDO: Metas Personales")
        print("="*60)
        
        test_cases = [
            # (weight, goal, brokers, expected_min, expected_max, description)
            (0.1, 2000, 50, 195, 205, "Peso 10%"),
            (0.05, 2066, 40, 100, 110, "Peso 5%"),
            (0, 2000, 40, 40, 50, "Peso cero (nuevo)"),
            (0.001, 2000, 50, 5, 10, "Peso mínimo"),
        ]
        
        for weight, goal, brokers, exp_min, exp_max, description in test_cases:
            result = calculate_personal_goal(
                broker_id=1,
                historical_weight=weight,
                contract_goal=goal,
                active_brokers_count=brokers
            )
            passed = exp_min <= result <= exp_max
            self.add_result(
                name=f"Goal: {description}",
                passed=passed,
                details=f"weight={weight}, goal={goal}, expected=[{exp_min},{exp_max}], got={result}"
            )
            status = "PASS" if passed else "FAIL"
            print(f"  [{status}] {description}: {result} (expected {exp_min}-{exp_max})")
    
    def verify_rate_calculations(self):
        """Verificar cálculo de tasas con Laplace smoothing"""
        print("\n" + "="*60)
        print("VERIFICANDO: Tasas con Laplace Smoothing")
        print("="*60)
        
        test_cases = [
            # (num, denom, k, expected, description)
            (50, 100, 15, 50/115, "Tasa 50/100 con k=15"),
            (10, 50, 15, 10/65, "Tasa 10/50 con k=15"),
            (0, 100, 15, 0, "Numerador cero"),
            (50, 0, 15, 0, "Denominador cero"),
            (100, 100, 0, 1.0, "Sin smoothing"),
        ]
        
        for num, denom, k, expected, description in test_cases:
            result = calculate_rate_with_smoothing(num, denom, k)
            passed = abs(result - expected) < 0.0001
            self.add_result(
                name=f"Rate: {description}",
                passed=passed,
                details=f"num={num}, denom={denom}, k={k}, expected={expected:.4f}, got={result:.4f}"
            )
            status = "PASS" if passed else "FAIL"
            print(f"  [{status}] {description}: {result:.4f} (expected {expected:.4f})")
    
    def verify_zscore_normalization(self):
        """Verificar normalización Z-score"""
        print("\n" + "="*60)
        print("VERIFICANDO: Normalización Z-Score")
        print("="*60)
        
        # Datos de prueba
        values = [10, 20, 30, 40, 50]
        
        # Test 1: Longitud de resultado
        result = normalize_z_score_robust(values)
        passed = len(result) == len(values)
        self.add_result(
            name="Z-Score: Longitud correcta",
            passed=passed,
            details=f"input={len(values)}, output={len(result)}"
        )
        print(f"  [{'PASS' if passed else 'FAIL'}] Longitud: {len(result)} (expected {len(values)})")
        
        # Test 2: Rango [0, 1]
        in_range = all(0 <= r <= 1 for r in result)
        self.add_result(
            name="Z-Score: Rango [0, 1]",
            passed=in_range,
            details=f"min={min(result):.4f}, max={max(result):.4f}"
        )
        print(f"  [{'PASS' if in_range else 'FAIL'}] Rango: [{min(result):.4f}, {max(result):.4f}]")
        
        # Test 3: Inversión
        result_inv = normalize_z_score_robust(values, inverse=True)
        inverse_correct = all(abs(r + ri - 1.0) < 0.001 for r, ri in zip(result, result_inv))
        self.add_result(
            name="Z-Score: Inversión correcta",
            passed=inverse_correct,
            details=f"sum normal+inverse ≈ 1.0"
        )
        print(f"  [{'PASS' if inverse_correct else 'FAIL'}] Inversion: suma ~= 1.0")
        
        # Test 4: Valores extremos
        extreme_values = [1, 2, 3, 1000]  # 1000 es outlier
        result_extreme = normalize_z_score_robust(extreme_values)
        outlier_handled = result_extreme[-1] > 0.7  # Outlier debería tener score alto (>0.7)
        self.add_result(
            name="Z-Score: Manejo de outliers",
            passed=outlier_handled,
            details=f"outlier score={result_extreme[-1]:.4f} (esperado > 0.7)"
        )
        print(f"  [{'PASS' if outlier_handled else 'FAIL'}] Outlier: score={result_extreme[-1]:.4f} (esperado > 0.7)")
    
    def verify_date_utilities(self):
        """Verificar utilidades de fecha"""
        print("\n" + "="*60)
        print("VERIFICANDO: Utilidades de Fecha")
        print("="*60)
        
        # Test 1: Límites de enero
        start, end = get_month_boundaries(2026, 1)
        passed = start == "2026-01-01 00:00:00" and end == "2026-02-01 00:00:00"
        self.add_result(
            name="Date: Límites enero",
            passed=passed,
            details=f"start={start}, end={end}"
        )
        print(f"  [{'PASS' if passed else 'FAIL'}] Enero: {start} a {end}")
        
        # Test 2: Límites de diciembre (cruza año)
        start, end = get_month_boundaries(2026, 12)
        passed = start == "2026-12-01 00:00:00" and end == "2027-01-01 00:00:00"
        self.add_result(
            name="Date: Límites diciembre",
            passed=passed,
            details=f"start={start}, end={end}"
        )
        print(f"  [{'PASS' if passed else 'FAIL'}] Diciembre: {start} a {end}")
        
        # Test 3: Mes inválido
        try:
            get_month_boundaries(2026, 13)
            passed = False
        except ValueError:
            passed = True
        self.add_result(
            name="Date: Error en mes inválido",
            passed=passed,
            details="ValueError lanzado correctamente"
        )
        print(f"  [{'PASS' if passed else 'FAIL'}] Mes inválido: lanza ValueError")
    
    def verify_goal_configuration(self):
        """Verificar configuración de metas"""
        print("\n" + "="*60)
        print("VERIFICANDO: Configuración de Metas")
        print("="*60)
        
        # Test 1: Meta enero 2026
        result = get_reservation_goal(2026, 1)
        passed = result == 1943
        self.add_result(
            name="Goal: Enero 2026",
            passed=passed,
            details=f"expected=1943, got={result}"
        )
        print(f"  [{'PASS' if passed else 'FAIL'}] Enero 2026: {result}")
        
        # Test 2: Meta febrero 2026
        result = get_reservation_goal(2026, 2)
        passed = result == 1878
        self.add_result(
            name="Goal: Febrero 2026",
            passed=passed,
            details=f"expected=1878, got={result}"
        )
        print(f"  [{'PASS' if passed else 'FAIL'}] Febrero 2026: {result}")
        
        # Test 3: Meta default
        result = get_reservation_goal(2027, 1)
        passed = result == 2000
        self.add_result(
            name="Goal: Default",
            passed=passed,
            details=f"expected=2000, got={result}"
        )
        print(f"  [{'PASS' if passed else 'FAIL'}] Default: {result}")
        
        # Test 4: Meta de contratos
        result = get_contract_goal(2026, 1)
        passed = result == 1943
        self.add_result(
            name="Goal: Contratos Ene 2026",
            passed=passed,
            details=f"expected=1943, got={result}"
        )
        print(f"  [{'PASS' if passed else 'FAIL'}] Contratos Ene 2026: {result}")
    
    def generate_report(self, output_path: str = None):
        """Generar reporte de resultados"""
        total = self.results['passed'] + self.results['failed']
        success_rate = (self.results['passed'] / total * 100) if total > 0 else 0
        
        report = []
        report.append("=" * 60)
        report.append("REPORTE DE VERIFICACIÓN DE REGRESIÓN")
        report.append("=" * 60)
        report.append(f"Timestamp: {self.results['timestamp']}")
        report.append("")
        report.append("RESUMEN:")
        report.append(f"  Total tests: {total}")
        report.append(f"  Pasados:     {self.results['passed']}")
        report.append(f"  Fallidos:    {self.results['failed']}")
        report.append(f"  Advertencias: {self.results['warnings']}")
        report.append(f"  Éxito:       {success_rate:.1f}%")
        report.append("")
        
        if self.results['failed'] > 0:
            report.append("TESTS FALLIDOS:")
            for test in self.results['tests']:
                if not test['passed']:
                    report.append(f"  [FAIL] {test['name']}")
                    report.append(f"    {test['details']}")
            report.append("")
        
        if self.results['warnings'] > 0:
            report.append("ADVERTENCIAS:")
            for test in self.results['tests']:
                if test.get('warning'):
                    report.append(f"  [WARN] {test['name']}")
                    report.append(f"    {test['details']}")
            report.append("")
        
        report.append("=" * 60)
        if self.results['failed'] == 0:
            report.append("RESULTADO: PASS - TODOS LOS TESTS PASARON")
        else:
            report.append(f"RESULTADO: FAIL - {self.results['failed']} TESTS FALLARON")
        report.append("=" * 60)
        
        report_text = "\n".join(report)
        print("\n" + report_text)
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report_text)
            print(f"\nReporte guardado en: {output_path}")
        
        return self.results['failed'] == 0


def main():
    """Función principal"""
    print("=" * 60)
    print("VERIFICACIÓN DE REGRESIÓN - SISTEMA DE MÉTRICAS")
    print("=" * 60)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    verifier = RegressionVerifier()
    
    # Ejecutar todas las verificaciones
    verifier.verify_net_reservations()
    verifier.verify_personal_goals()
    verifier.verify_rate_calculations()
    verifier.verify_zscore_normalization()
    verifier.verify_date_utilities()
    verifier.verify_goal_configuration()
    
    # Generar reporte
    output_path = os.path.join(
        os.path.dirname(__file__),
        '..',
        'reports',
        f'regression_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
    )
    
    # Crear directorio de reports si no existe
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    success = verifier.generate_report(output_path)
    
    # Código de salida
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
