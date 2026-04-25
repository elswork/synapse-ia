import requests
import json

base_url = "http://192.168.1.75:5380/api"
password = "Ek3cRWwBM2y2Cgi"

def login():
    url = f"{base_url}/user/login?user=admin&pass={password}"
    r = requests.get(url)
    return r.json().get("token")

def add_record(token, zone, domain, record_type, address):
    # Intentar con 'ipAddress' ya que 'address' falló
    url = f"{base_url}/zones/records/add?token={token}&domain={domain}&type={record_type}&ipAddress={address}&zone={zone}"
    r = requests.get(url)
    return r.json()

token = login()
if token:
    print(f"Adding record palanca.dl4.eu...")
    res2 = add_record(token, "dl4.eu", "palanca.dl4.eu", "A", "192.168.1.75")
    print(json.dumps(res2, indent=2))
else:
    print("Failed to login.")
