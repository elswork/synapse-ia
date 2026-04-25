import requests
import json

base_url = "http://192.168.1.75:5380/api"
password = "Ek3cRWwBM2y2Cgi"

def login():
    url = f"{base_url}/user/login?user=admin&pass={password}"
    r = requests.get(url)
    return r.json().get("token")

def list_zones(token):
    url = f"{base_url}/zones/list?token={token}"
    r = requests.get(url)
    return r.json()

token = login()
if token:
    print(json.dumps(list_zones(token), indent=2))
