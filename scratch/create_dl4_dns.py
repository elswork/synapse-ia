import requests
import json

base_url = "http://192.168.1.75:5380/api"
password = "Ek3cRWwBM2y2Cgi"

def login():
    url = f"{base_url}/user/login?user=admin&pass={password}"
    r = requests.get(url)
    return r.json().get("token")

def create_zone(token, zone):
    url = f"{base_url}/zones/create?token={token}&zone={zone}&type=Primary"
    r = requests.get(url)
    return r.json()

def add_record(token, zone, domain, record_type, address):
    url = f"{base_url}/zones/records/add?token={token}&domain={domain}&type={record_type}&address={address}&zone={zone}"
    r = requests.get(url)
    return r.json()

token = login()
if token:
    print(f"Creating zone dl4.eu...")
    res1 = create_zone(token, "dl4.eu")
    print(json.dumps(res1, indent=2))
    
    if res1.get("status") == "ok" or "already exists" in res1.get("errorMessage", ""):
        print(f"Adding record palanca.dl4.eu...")
        res2 = add_record(token, "dl4.eu", "palanca.dl4.eu", "A", "192.168.1.75")
        print(json.dumps(res2, indent=2))
    else:
        print("Failed to create zone.")
else:
    print("Failed to login.")
