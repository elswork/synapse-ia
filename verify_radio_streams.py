import os
import re
import json
import sys
import requests

def load_stations():
    stations_path = "/home/pirate/docker/synapse-ia/stations_data.js"
    with open(stations_path, "r") as f:
        content = f.read()
    
    match = re.search(r'window\.STATIONS_DATA\s*=\s*(\{.*?\});', content, re.DOTALL)
    if not match:
        print("Error: Could not find STATIONS_DATA in stations_data.js")
        sys.exit(1)
        
    json_str = match.group(1)
    # Basic cleanup in case of trailing commas or comments
    json_str = re.sub(r',\s*}', '}', json_str)
    json_str = re.sub(r',\s*]', ']', json_str)
    
    try:
        data = json.loads(json_str)
    except Exception as e:
        print(f"Error parsing JSON from stations_data.js: {e}")
        sys.exit(1)
        
    return data

def verify_stream(name, url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    }
    try:
        # Use GET with stream=True so we only fetch headers and don't download the body
        with requests.get(url, stream=True, timeout=8, headers=headers, allow_redirects=True) as response:
            status = response.status_code
            content_type = response.headers.get('Content-Type', '')
            
            # We expect a success status code < 400
            # and a content type indicating audio/media/stream
            is_audio = any(t in content_type.lower() for t in ['audio', 'mpeg', 'ogg', 'octet-stream', 'video', 'stream'])
            
            if status < 400 and is_audio:
                print(f"[OK] {name:<30} | Code: {status} | Type: {content_type}")
                return True
            else:
                print(f"[FAIL] {name:<30} | Code: {status} | Type: {content_type} (Invalid stream)")
                return False
    except Exception as e:
        print(f"[FAIL] {name:<30} | Error: {e}")
        return False

def main():
    print("Loading station list...")
    data = load_stations()
    
    # Flatten stations and deduplicate by URL
    stations_to_verify = []
    seen_urls = set()
    for category, stations in data.items():
        for st in stations:
            url = st['url']
            if url not in seen_urls:
                seen_urls.add(url)
                stations_to_verify.append((st['name'], url))
                
    print(f"Loaded {len(stations_to_verify)} unique stations. Verifying streams...")
    print("-" * 80)
    
    all_ok = True
    for name, url in stations_to_verify:
        if not verify_stream(name, url):
            all_ok = False
            
    print("-" * 80)
    if all_ok:
        print("All stations verified successfully!")
        sys.exit(0)
    else:
        print("Some station streams failed verification!")
        sys.exit(1)

if __name__ == "__main__":
    main()
