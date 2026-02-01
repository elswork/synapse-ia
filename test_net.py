import requests
try:
    response = requests.head('https://www.google.com', timeout=5)
    print(f"Google: {response.status_code}")
except Exception as e:
    print(f"Error: {e}")
