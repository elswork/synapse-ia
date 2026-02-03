import psutil
import subprocess
from typing import Dict

class SystemTelemetryAdapter:
    def get_local_metrics(self) -> Dict[str, str]:
        try:
            cpu = psutil.cpu_percent(interval=1)
            ram = psutil.virtual_memory().percent
            return {"cpu": f"{cpu}%", "ram": f"{ram}%", "status": "🟢 Online"}
        except:
            return {"cpu": "N/A", "ram": "N/A", "status": "🟡 Error"}

    def get_remote_metrics(self, host: str) -> Dict[str, str]:
        try:
            # Example for HC1
            ssh_cmd = f"ssh -o ConnectTimeout=3 {host} \"top -bn1 | grep 'Cpu(s)' | awk '{{print \\$2 + \\$4}}' && free | grep Mem | awk '{{print \\$3/\\$2 * 100.0}}'\""
            output = subprocess.check_output(ssh_cmd, shell=True, text=True).splitlines()
            cpu = output[0] if len(output) > 0 else "N/A"
            ram = output[1] if len(output) > 1 else "N/A"
            return {"cpu": f"{cpu}%", "ram": f"{ram}%", "status": "🟢 Online"}
        except:
            return {"cpu": "N/A", "ram": "N/A", "status": "🔴 Offline"}
