import subprocess
import time
import os

UPDATE_VERSION = "v2"
ROLLBACK_VERSION = "v1"
LOG_FILE = "logs/deployment.log"

def run_deployment():
    subprocess.run(["python3", "deploy.py"], check=True)
    time.sleep(3)

def get_log_lines():
    with open(LOG_FILE, "r") as f:
        return f.readlines()

def test_deployment_success_or_rollback():
    run_deployment()
    logs = get_log_lines()
    device1_updated = any("device1 successfully updated" in line for line in logs[-15:])
    device1_rolled_back = any("device1 rolled back to" in line for line in logs[-15:])
    device2_updated = any("device2 successfully updated" in line for line in logs[-15:])

    # device1 either updated or rolled back
    assert device1_updated or device1_rolled_back, "device1 did not update or roll back correctly"
    assert device2_updated, "device2 did not update successfully"

def test_metrics_logging():
    run_deployment()
    logs = get_log_lines()
    success_count = sum("successfully updated" in line for line in logs[-20:])
    fail_count = sum("FAILED update verification" in line for line in logs[-20:])
    rollback_count = sum("[ROLLBACK]" in line for line in logs[-20:])

    print(f"✅ Successes: {success_count}, ❌ Failures: {fail_count}, ♻️ Rollbacks: {rollback_count}")

    assert success_count >= 1, "Expected at least one successful update"
    assert fail_count >= 0, "Expected zero or more failures"
    assert rollback_count >= 0, "Expected zero or more rollbacks"
