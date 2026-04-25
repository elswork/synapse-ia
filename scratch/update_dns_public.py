import requests
import json

base_url = "http://192.168.1.75:5380/api"
password = "Ek3cRWwBM2y2Cgi"
public_ip = "83.61.120.66"

def login():
    url = f"{base_url}/user/login?user=admin&pass={password}"
    r = requests.get(url)
    return r.json().get("token")

def update_record(token, zone, domain, record_type, address):
    # Primero borrar el viejo
    url_del = f"{base_url}/zones/records/delete?token={token}&domain={domain}&type={record_type}&zone={zone}"
    requests.get(url_del)
    # Añadir el nuevo
    url_add = f"{base_url}/zones/records/add?token={token}&domain={domain}&type={record_type}&ipAddress={address}&zone={zone}"
    r = requests.get(url_add)
    return r.json()

token = login()
if token:
    print(f"Updating palanca.dl4.eu to {public_ip}...")
    res = update_record(token, "dl4.eu", "palanca.dl4.eu", "A", public_ip)
    print(json.dumps(res, indent=2))
else:
    print("Failed to login.")
