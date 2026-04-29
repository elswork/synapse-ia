import requests

base_url = "http://192.168.1.75:5380/api"
password = "Ek3cRWwBM2y2Cgi"
public_ip = "83.61.120.66"

r = requests.get(f"{base_url}/user/login?user=admin&pass={password}")
token = r.json().get("token")

# Get existing records
records = requests.get(f"{base_url}/zones/records/get", params={"token": token, "domain": "dl4.eu", "listZone": "true"}).json()
for rec in records["response"]["records"]:
    if rec["name"] == "palanca.dl4.eu" and rec["type"] == "A":
        # Delete
        requests.get(f"{base_url}/zones/records/delete", params={"token": token, "domain": "palanca.dl4.eu", "type": "A", "ipAddress": rec["rData"]["ipAddress"], "zone": "dl4.eu"})

# Add new public IP
requests.get(f"{base_url}/zones/records/add", params={"token": token, "domain": "palanca.dl4.eu", "type": "A", "ipAddress": public_ip, "zone": "dl4.eu"})
print("Palanca local IP updated to public IP.")
