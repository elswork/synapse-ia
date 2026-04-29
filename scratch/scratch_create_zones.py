import requests
import os

env_path = '/home/pirate/docker/Arquimedes/forge/src/.env'
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                k, v = line.strip().split('=', 1)
                os.environ[k] = v

LOCAL_TOKEN = os.getenv("LOCAL_TOKEN")
GCP_TOKEN = os.getenv("GCP_TOKEN")
LOCAL_IP = os.getenv("LOCAL_IP", "192.168.1.75")
GCP_IP = os.getenv("GCP_IP", "104.155.166.27")

BASE_URL_LOCAL = f"http://{LOCAL_IP}:5380/api"
BASE_URL_GCP = f"http://{GCP_IP}:5380/api"

r_local = requests.get(f"{BASE_URL_LOCAL}/zones/list", params={"token": LOCAL_TOKEN}).json()
r_gcp = requests.get(f"{BASE_URL_GCP}/zones/list", params={"token": GCP_TOKEN}).json()

local_zones = [z["name"] for z in r_local["response"]["zones"] if not z["internal"]]
gcp_zones = [z["name"] for z in r_gcp["response"]["zones"] if not z["internal"]]

for zone in local_zones:
    if zone not in gcp_zones:
        print(f"Creating zone {zone} on GCP...")
        requests.get(f"{BASE_URL_GCP}/zones/create", params={"token": GCP_TOKEN, "zone": zone, "type": "Primary"})
print("Zone check complete.")
