import requests
base_url = "http://192.168.1.75:5380/api"
password = "Ek3cRWwBM2y2Cgi"
token = requests.get(f"{base_url}/user/login?user=admin&pass={password}").json()["token"]
r = requests.get(f"{base_url}/zones/export?token={token}&zone=deft.work&format=text")
print(r.text)
