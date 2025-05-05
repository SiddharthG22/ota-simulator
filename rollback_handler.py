import shutil
import subprocess
import time

ROLLBACK_VERSION = "v1"
DEVICE_APP_PATH = "device/app.py"
ROLLBACK_SOURCE = f"updates/{ROLLBACK_VERSION}/app.py"
LOG_FILE = "logs/deployment.log"

def log(message):
    timestamp = time.strftime("[%Y-%m-%d %H:%M:%S]")
    with open(LOG_FILE, "a") as f:
        f.write(f"{timestamp} [ROLLBACK] {message}\n")
    print(f"{timestamp} [ROLLBACK] {message}")

def rollback_device(device_name):
    log(f"Rolling back {device_name} to {ROLLBACK_VERSION}...")
    try:
        shutil.copy(ROLLBACK_SOURCE, DEVICE_APP_PATH)
        log("Copied rollback version to device directory.")
    except Exception as e:
        log(f"ERROR copying rollback version: {e}")
        return False

    result = subprocess.run(["docker", "compose", "build", device_name], capture_output=True, text=True)
    if result.returncode != 0:
        log(f"Build failed for {device_name}: {result.stderr}")
        return False

    result = subprocess.run(["docker", "compose", "up", "-d", "--force-recreate", device_name], capture_output=True, text=True)
    if result.returncode != 0:
        log(f"Restart failed for {device_name}: {result.stderr}")
        return False

    log(f"{device_name} rolled back to {ROLLBACK_VERSION}.")
    return True
