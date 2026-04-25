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
    # Primero ver si la zona existe
    zone = ".".join(domain.split(".")[-2:])
    url = f"{base_url}/zones/records/add?token={token}&domain={domain}&type={record_type}&address={address}&zone={zone}"
    r = requests.get(url)
    return r.json()

token = login()
if token:
    print(f"Logged in, token: {token[:5]}...")
    result = add_record(token, "palanca.dl4.eu", "A", "192.168.1.75")
    print(json.dumps(result, indent=2))
else:
    print("Failed to login.")
