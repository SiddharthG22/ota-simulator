import os
import shutil
import subprocess
import time
from rollback_handler import rollback_device

UPDATE_VERSION = "v2"  # Change this to switch versions (e.g., v1 or v2)
DEVICE_APP_PATH = "device/app.py"
UPDATE_SOURCE = f"updates/{UPDATE_VERSION}/app.py"
LOG_FILE = "logs/deployment.log"

def log(message):
    timestamp = time.strftime("[%Y-%m-%d %H:%M:%S]")
    with open(LOG_FILE, "a") as f:
        f.write(f"{timestamp} {message}\n")
    print(f"{timestamp} {message}")

def apply_update():
    log(f"Applying update: {UPDATE_VERSION}")
    try:
        shutil.copy(UPDATE_SOURCE, DEVICE_APP_PATH)
        log("Copied update to device directory.")
    except Exception as e:
        log(f"ERROR copying update: {e}")
        return False

    result = subprocess.run(["docker", "compose", "build"], capture_output=True, text=True)
    if result.returncode != 0:
        log(f"Build failed: {result.stderr}")
        return False

    result = subprocess.run(["docker", "compose", "up", "-d", "--force-recreate"], capture_output=True, text=True)
    if result.returncode != 0:
        log(f"Container restart failed: {result.stderr}")
        return False

    log("Containers rebuilt and restarted.")
    return True

def verify_update():
    success = True
    failed_devices = []

    for device in ["device1", "device2"]:
        result = subprocess.run(["docker", "logs", device], capture_output=True, text=True)
        if f"v{UPDATE_VERSION[-1]}" not in result.stdout:
            log(f"{device} FAILED update verification.")
            failed_devices.append(device)
            success = False
        else:
            log(f"{device} successfully updated.")

    for device in failed_devices:
        rollback_device(device)

    return success

def main():
    if apply_update():
        log("Update applied. Verifying...")
        if verify_update():
            log("✅ Update successful on all devices.")
        else:
            log("❌ Update failed on one or more devices.")
    else:
        log("❌ Update process failed during application.")

if __name__ == "__main__":
    main()
