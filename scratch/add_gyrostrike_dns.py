import requests
import json

base_url = "http://192.168.1.75:5380/api"
password = "Ek3cRWwBM2y2Cgi"

def login():
    url = f"{base_url}/user/login?user=admin&pass={password}"
    r = requests.get(url)
    data = r.json()
    if data.get("status") == "ok":
        return data["token"]
    else:
        print(f"Login failed: {data}")
        return None

def add_record(token, domain, record_type, address):
    zone = ".".join(domain.split(".")[-2:])
    # Intentamos primero con ipAddress (que es la API oficial para registros A)
    url = f"{base_url}/zones/records/add?token={token}&domain={domain}&type={record_type}&ipAddress={address}&zone={zone}"
    r = requests.get(url)
    return r.json()

token = login()
if token:
    print("Conectado a Technitium DNS...")
    res = add_record(token, "gyrostrike.deft.work", "A", "80.29.187.129")
    print(json.dumps(res, indent=2))
else:
    print("Error de autenticación.")
