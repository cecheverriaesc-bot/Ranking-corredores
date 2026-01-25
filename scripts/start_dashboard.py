
import subprocess
import time
import threading
import sys
import os
from datetime import datetime

# Configuration
# Script is now in ranking-corredores-rm---dashboard/scripts/
# We want to run etl_ranking.py (in same dir)
# And run npm run dev in parent dir (ranking-corredores-rm---dashboard)

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # scripts/
PROJECT_ROOT = os.path.dirname(BASE_DIR) # ranking-corredores-rm---dashboard/

ETL_SCRIPT = os.path.join(BASE_DIR, "etl_ranking.py")
DASHBOARD_DIR = PROJECT_ROOT
POLL_INTERVAL_MINUTES = 30

def run_etl():
    """Runs the ETL script and prints output."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Updating data...")
    try:
        # Run in PROJECT_ROOT context or BASE_DIR? 
        # ETL script expects to find .env in specific place? 
        # ETL has absolute path to .env hardcoded: c:\Users\assetplan\Desktop\Ranking Enero 2026\.env
        # So CWD doesn't matter much for env, but matters for constants.ts output
        # ETL writes to os.path.join(script_dir, "..", "constants.ts") -> works if script is in scripts/
        
        result = subprocess.run([sys.executable, ETL_SCRIPT], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Data updated successfully.")
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Error updating data:\n{result.stderr}")
    except Exception as e:
        print(f"Error running ETL: {e}")

def etl_loop():
    """Background thread to run ETL periodically."""
    while True:
        run_etl()
        print(f"Waiting {POLL_INTERVAL_MINUTES} minutes for next update...")
        time.sleep(POLL_INTERVAL_MINUTES * 60)

def start_dashboard():
    """Starts the Vite dev server."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting Dashboard...")
    # npm run dev in DASHBOARD_DIR
    process = subprocess.Popen("npm run dev", shell=True, cwd=DASHBOARD_DIR)
    return process

def main():
    print("--- AUTOMATED DASHBOARD LAUNCHER ---")
    print(f"Logic: Run ETL immediately, start Server, then update every {POLL_INTERVAL_MINUTES} mins.")

    # 1. Start ETL Loop in Background
    etl_thread = threading.Thread(target=etl_loop, daemon=True)
    etl_thread.start()

    # 2. Start Dashboard
    # Give the first ETL a moment to finish? Or let them race (Vite HMR matches file changes anyway)
    # A small delay ensures constants.ts is fresh for initial load
    time.sleep(5) 
    
    dashboard_process = start_dashboard()

    try:
        # Keep main thread alive to let dashboard run
        dashboard_process.wait()
    except KeyboardInterrupt:
        print("\nStopping Dashboard...")
        dashboard_process.terminate()

if __name__ == "__main__":
    main()
