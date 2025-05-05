import json
import os
import time

LOG_FILE = "logs/deployment.log"
METRICS_FILE = "logs/metrics.json"

def extract_metrics():
    if not os.path.exists(LOG_FILE):
        print("❌ deployment.log not found.")
        return None

    with open(LOG_FILE, "r") as f:
        lines = f.readlines()

    metrics = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "success_count": 0,
        "fail_count": 0,
        "rollback_count": 0
    }

    for line in lines:  # Scan full log file
        if "successfully updated" in line:
            metrics["success_count"] += 1
        elif "FAILED update verification" in line:
            metrics["fail_count"] += 1
        elif "[ROLLBACK]" in line and "rolled back" in line:
            metrics["rollback_count"] += 1

    if metrics["success_count"] == 0 and metrics["fail_count"] == 0 and metrics["rollback_count"] == 0:
        print("⚠️ No matching events found in deployment.log.")
        return None

    return metrics

def log_metrics():
    metrics = extract_metrics()
    if metrics is None:
        print("No metrics to log.")
        return

    existing = []

    if os.path.exists(METRICS_FILE):
        with open(METRICS_FILE, "r") as f:
            try:
                existing = json.load(f)
            except json.JSONDecodeError:
                print("⚠️ metrics.json was corrupted or empty. Overwriting.")
                existing = []

    existing.append(metrics)

    with open(METRICS_FILE, "w") as f:
        json.dump(existing, f, indent=2)

    print("✅ Metrics logged to", METRICS_FILE)
    print(json.dumps(metrics, indent=2))

if __name__ == "__main__":
    log_metrics()
