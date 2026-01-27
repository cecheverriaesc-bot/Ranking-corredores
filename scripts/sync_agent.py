
import subprocess
import time
import sys
import os
from datetime import datetime

# Configuración
INTERVAL_MINUTES = 15
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ETL_SCRIPT = os.path.join(SCRIPT_DIR, "etl_ranking.py")
DASHBOARD_DIR = os.path.join(SCRIPT_DIR, "..")

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")
    with open("sync_agent_log.txt", "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")

def run_sync():
    try:
        log("Iniciando ciclo de sincronización...")
        
        # 1. Ejecutar ETL
        log("Ejecutando ETL...")
        result_etl = subprocess.run([sys.executable, ETL_SCRIPT], capture_output=True, text=True)
        if result_etl.returncode == 0:
            log("ETL completado exitosamente.")
        else:
            log(f"Error en ETL: {result_etl.stderr}")
            return False
            
        # 2. Desplegar en Vercel
        log("Desplegando en Vercel...")
        # Cambiamos al directorio del dashboard para correr vercel
        result_vercel = subprocess.run(["npx", "vercel", "--prod", "--yes"], 
                                      cwd=DASHBOARD_DIR, 
                                      capture_output=True, 
                                      text=True, 
                                      shell=True)
        
        if result_vercel.returncode == 0:
            log("Despliegue en Vercel exitoso.")
            return True
        else:
            log(f"Error en Vercel: {result_vercel.stderr}")
            return False
            
    except Exception as e:
        log(f"Error inesperado: {str(e)}")
        return False

def main():
    log("Agente de Sincronización iniciado. Frecuencia: 15 minutos.")
    while True:
        success = run_sync()
        if success:
            log("Sincronización completa. Esperando 15 minutos...")
        else:
            log("Sincronización fallida. Reintentando en 5 minutos...")
            time.sleep(5 * 60)
            continue
            
        time.sleep(INTERVAL_MINUTES * 60)

if __name__ == "__main__":
    main()
