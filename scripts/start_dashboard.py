
import subprocess
import time
import threading
import sys
import os
from datetime import datetime

# Configuration
ETL_SCRIPT = r"scripts/etl_ranking.py"
DASHBOARD_DIR = r"ranking-corredores-rm---dashboard"
POLL_INTERVAL_MINUTES = 30

def run_etl():
    """Runs the ETL script and prints output."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Updating data...")
    try:
        # Assuming current working dir is project root
        result = subprocess.run([sys.executable, ETL_SCRIPT], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Data updated successfully.")
            # Optional: Print summary line if needed, or just rely on script output
            # print(result.stdout)
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
    # Using npm run dev. Shell=True needed on Windows for npm
    # We use Popen so it runs in parallel
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
