import requests
import json

base_url = "http://192.168.1.75:5380/api"
password = "Ek3cRWwBM2y2Cgi"

def login():
    url = f"{base_url}/user/login?user=admin&pass={password}"
    r = requests.get(url)
    return r.json().get("token")

def list_records(token, zone):
    url = f"{base_url}/zones/records/get?token={token}&domain={zone}"
    r = requests.get(url)
    return r.json()

token = login()
if token:
    print(json.dumps(list_records(token, "dl4.eu"), indent=2))
