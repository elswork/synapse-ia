import requests

GCP_URL = "http://104.155.166.27:5380/api"
GCP_PASS = "Ek3cRWwBM2y2Cgi"

r = requests.get(f"{GCP_URL}/user/login?user=admin&pass={GCP_PASS}")
token = r.json()["token"]

# Create test zone
r = requests.get(f"{GCP_URL}/zones/create?token={token}&zone=deft.work.test&type=Primary")
print("Create:", r.json())

# Delete test zone
r = requests.get(f"{GCP_URL}/zones/delete?token={token}&zone=deft.work.test")
print("Delete:", r.json())
