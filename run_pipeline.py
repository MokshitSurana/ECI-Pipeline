"""Real-Time Backend Worker for ECI Pipeline."""
import time
import subprocess
from datetime import datetime
from sqlalchemy import text
from utils.db import engine

def poll_for_jobs():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Worker started. Polling Supabase for pending jobs...")
    while True:
        try:
            with engine.connect() as conn:
                # Find a pending job
                job = conn.execute(text("SELECT id FROM pipeline_jobs WHERE status = 'pending' ORDER BY id ASC LIMIT 1")).fetchone()
                if job:
                    job_id = job[0]
                    # Mark as running
                    conn.execute(text("UPDATE pipeline_jobs SET status = 'running', started_at = now() WHERE id = :id"), {"id": job_id})
                    conn.commit()
                    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Picked up Job #{job_id}. Executing pipeline...")
                    
                    # Run the pipeline execution
                    process = subprocess.Popen(
                        ["uv", "run", "main.py", "--stage", "all"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        bufsize=1 # Line buffered
                    )
                    
                    # Read stdout line by line and proxy it directly to the logs table in Supabase
                    for line in iter(process.stdout.readline, ''):
                        if line:
                            # Strip to prevent excessive newlines in DB
                            log_str = line.strip('\n')
                            print(log_str)
                            try:
                                with engine.begin() as log_conn:
                                    log_conn.execute(text(
                                        "INSERT INTO pipeline_logs (job_id, log_line) VALUES (:job_id, :log_line)"
                                    ), {"job_id": job_id, "log_line": log_str})
                            except Exception as db_err:
                                print(f"[Worker Log DB Error] {db_err}")
                    
                    process.wait()
                    final_status = "completed" if process.returncode == 0 else "failed"
                    
                    # Update job completion
                    with engine.begin() as conn2:
                        conn2.execute(text("UPDATE pipeline_jobs SET status = :status, finished_at = now() WHERE id = :id"), 
                                      {"status": final_status, "id": job_id})
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Job #{job_id} {final_status}.")
        except Exception as e:
            pass # Suppress silent transient polling errors (like connection drops)
        
        # Sleep tight to avoid spamming the database
        time.sleep(3)

if __name__ == "__main__":
    poll_for_jobs()
