import requests
import json
import time

LOCAL_URL = "http://192.168.1.75:5380/api"
LOCAL_PASS = "Ek3cRWwBM2y2Cgi"

GCP_URL = "http://104.155.166.27:5380/api"
GCP_PASS = "Ek3cRWwBM2y2Cgi"

def login(base_url, password):
    url = f"{base_url}/user/login?user=admin&pass={password}"
    r = requests.get(url)
    data = r.json()
    if data.get("status") == "ok":
        return data["token"]
    raise Exception(f"Login failed at {base_url}: {data}")

def export_zone(token, base_url, zone):
    url = f"{base_url}/zones/export?token={token}&zone={zone}&format=text"
    r = requests.get(url)
    if r.status_code == 200 and not r.text.startswith('{"status":"error"'):
        return r.text
    raise Exception(f"Failed to export zone {zone}: {r.text}")

def delete_zone(token, base_url, zone):
    url = f"{base_url}/zones/delete?token={token}&zone={zone}"
    r = requests.get(url)
    if r.json().get("status") == "ok":
        return True
    return False

def create_zone(token, base_url, zone):
    url = f"{base_url}/zones/create?token={token}&zone={zone}&type=Primary"
    r = requests.get(url)
    if r.json().get("status") == "ok":
        return True
    return False

def import_zone(token, base_url, zone, zone_data):
    url = f"{base_url}/zones/import?token={token}&zone={zone}&format=text&overwrite=true&overwriteSoaSerial=true"
    files = {'file': (f'{zone}.txt', zone_data)}
    r = requests.post(url, files=files)
    data = r.json()
    if data.get("status") == "ok":
        return True
    else:
        print(f"Error importando zona {zone}: {data}")
        return False

def sync_zone(zone):
    print(f"=== Sincronizando {zone} ===")
    
    print("1. Conectando al DNS Local...")
    token_local = login(LOCAL_URL, LOCAL_PASS)
    print("OK.")
    
    print(f"2. Exportando zona {zone} del Local...")
    zone_data = export_zone(token_local, LOCAL_URL, zone)
    print(f"OK. ({len(zone_data)} bytes)")
    
    print("3. Conectando al DNS GCP...")
    token_gcp = login(GCP_URL, GCP_PASS)
    print("OK.")
    
    print(f"4. Recreando la zona en GCP...")
    delete_zone(token_gcp, GCP_URL, zone)
    create_zone(token_gcp, GCP_URL, zone)
    print("OK.")

    print(f"5. Importando zona {zone} en GCP...")
    success = import_zone(token_gcp, GCP_URL, zone, zone_data)
    if success:
        print("¡Sincronización Completada con Éxito!")
    else:
        print("Fallo la sincronización.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        zone_to_sync = sys.argv[1]
    else:
        zone_to_sync = "deft.work"
    
    try:
        sync_zone(zone_to_sync)
    except Exception as e:
        print(f"Error crítico: {e}")
