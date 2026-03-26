"""Continuous Backend Execution Scheduler for ECI Pipeline."""
import time
import subprocess
from datetime import datetime

# Run pipeline every 6 hours (6 * 60 * 60 = 21600 seconds)
# You can change this to 3600 for every 1 hour, etc.
INTERVAL_SECONDS = 6 * 60 * 60

def run_job():
    print(f"\n{'='*50}")
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Triggering ECI Pipeline Run...")
    print(f"{'='*50}")
    try:
        # We use standard subprocess to run the pipeline exactly as you would in the terminal
        subprocess.run(["uv", "run", "main.py", "--stage", "all"], check=True)
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ECI Pipeline Run Complete.")
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Pipeline run failed with exit code: {e.returncode}")
    except Exception as e:
        print(f"\n[ERROR] Unexpected error triggering pipeline: {e}")

if __name__ == "__main__":
    print(f"Started ECI Pipeline Scheduler. Interval: {INTERVAL_SECONDS / 3600:.1f} hours.")
    print("Press Ctrl+C to stop.")
    
    # Run immediately on startup
    run_job()
    
    # Then wait for the interval and loop indefinitely
    while True:
        print(f"\nWaiting {INTERVAL_SECONDS / 3600:.1f} hours for the next run...")
        try:
            time.sleep(INTERVAL_SECONDS)
            run_job()
        except KeyboardInterrupt:
            print("\nScheduler stopped by user.")
            break
