import requests
import json

base_url = "http://192.168.1.75:5380/api"
password = "Ek3cRWwBM2y2Cgi"

def get_zones():
    r = requests.get(f"{base_url}/user/login?user=admin&pass={password}")
    token = r.json().get("token")
    if not token:
        print("Login failed")
        return
    
    r_zones = requests.get(f"{base_url}/zones/list?token={token}")
    print(json.dumps(r_zones.json(), indent=2))

get_zones()
