import sys
import os
import time
import subprocess
import signal
import psutil

# Configuration
MONITOR_SCRIPT = "guard_monitor.py"
MAX_RESTARTS_PER_MINUTE = 5
RESTART_WINDOW = 60

def run_supervisor():
    """
    Main supervisor loop.
    Launches guard_monitor.py and restarts it if it crashes or is killed.
    """
    python_exe = sys.executable
    # Use the directory of the current script to find the monitor, ensuring it works from any CWD
    base_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(base_dir, MONITOR_SCRIPT)
    
    print(f"🛡️  [WATCHDOG] Supervisor Active. Protecting: {MONITOR_SCRIPT}")
    
    restart_times = []
    
    while True:
        try:
            # 1. Launch the Monitor
            print(f"🛡️  [WATCHDOG] Launching Monitor...")
            
            # We use Popen so we can wait() on it
            # Redirect output to the same log files
            with open("guard_monitor.out", "a") as out, open("guard_monitor.err", "a") as err:
                process = subprocess.Popen(
                    [python_exe, script_path],
                    stdout=out,
                    stderr=err,
                    stdin=subprocess.DEVNULL,
                    cwd=base_dir # Run in the correct directory
                )
            
            # Save the MONITOR PID so we can trace it if needed (optional)
            with open("monitor_pid.txt", "w") as f:
                f.write(str(process.pid))
                
            print(f"🛡️  [WATCHDOG] Monitor Online (PID: {process.pid})")
            
            # 2. WAIT for it to exit (Blocking call)
            exit_code = process.wait()
            
            # If we get here, the process died.
            print(f"⚠️  [WATCHDOG] Monitor DIED (Exit Code: {exit_code})")
            
            # 3. Check for User Stop Signal (Graceful Exit)
            # If exited with 0, we assume it was a clean stop
            if exit_code == 0:
                print("🛡️  [WATCHDOG] Clean exit detected. Supervisor shutting down.")
                break
                
            # 4. Restart Logic (Throttle Check)
            now = time.time()
            restart_times.append(now)
            # Filter timestamps older than 1 minute
            restart_times = [t for t in restart_times if now - t < RESTART_WINDOW]
            
            if len(restart_times) > MAX_RESTARTS_PER_MINUTE:
                print("❌ [WATCHDOG] Restart loop detected (Too many crashes). Aborting.")
                break
                
            print("⚡️ [WATCHDOG] Restarting immediately...")
            time.sleep(1) # Small delay to prevent CPU spinning
            
        except KeyboardInterrupt:
            print("\n[WATCHDOG] Supervisor stopped by user.")
            break
        except Exception as e:
            print(f"❌ [WATCHDOG] Supervisor Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run_supervisor()
