# Handoff Report — Radio Streams Integration & Verification

## 1. Observation
- **Original diagnosis and proposed stream URLs**: Retrieved from `/home/pirate/docker/synapse-ia/.agents/teamwork_preview_explorer_m1/handoff.md`.
- **Target files to modify**:
  1. `/home/pirate/docker/synapse-ia/stations_data.js`
  2. `/home/pirate/docker/synapse-ia/radio_m2.json`
  3. `/home/pirate/docker/synapse-ia/test_radio.py`
- **Verification script to create**:
  - `/home/pirate/docker/synapse-ia/verify_radio_streams.py`
- **Command execution attempts**:
  - Running the command `python3 /home/pirate/docker/synapse-ia/verify_radio_streams.py` resulted in the following error:
    `Encountered error in step execution: Permission prompt for action 'command' on target 'python3 /home/pirate/docker/synapse-ia/verify_radio_streams.py' timed out waiting for user response. The user was not able to provide permission on time.`
    As per constraints, no further terminal commands could be executed.

## 2. Logic Chain
1. We read the replacement and protocol-downgraded URLs from the explorer's handoff. Specifically, 13 broken streams were replaced with active online equivalents, and 9 SomaFM/Radio Paradise streams were changed from `https://` to `http://` to bypass the system's MPD container certificate verification issue.
2. We modified `/home/pirate/docker/synapse-ia/stations_data.js` to update these 22 stream URLs.
3. We synchronized `/home/pirate/docker/synapse-ia/radio_m2.json` to keep M2's active JSON stream URLs aligned with `stations_data.js`.
4. We updated `/home/pirate/docker/synapse-ia/test_radio.py` to ensure its internal `STATIONS` list has the matching working stream endpoints.
5. We wrote `/home/pirate/docker/synapse-ia/verify_radio_streams.py` to dynamically load `stations_data.js`, request headers from each unique URL using `requests.get(..., stream=True)`, and verify that each stream returns a success code (< 400) and audio-compatible `Content-Type`.

## 3. Caveats
- Direct execution of the verification script and deployment scripts (such as `radio_injector_v2.py`, `fix_radio_json.py`, and `push_to_m2.py`) from this agent's workspace was blocked by terminal permission prompt timeouts. However, all file modifications were completed successfully, ensuring the scripts are fully prepared for local execution.

## 4. Conclusion
All broken and SSL-affected radio stream URLs have been updated across `stations_data.js`, `radio_m2.json`, and `test_radio.py`. The dynamic verification script `verify_radio_streams.py` is implemented and ready.

### File Modification Summaries
- **`stations_data.js`**: Updated 22 URLs.
- **`radio_m2.json`**: Updated 22 corresponding URLs in JSON format.
- **`test_radio.py`**: Updated URL mappings to correct active endpoints.

---

### Exact Code of `verify_radio_streams.py`
```python
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
```

## 5. Verification Method
To execute the injection and deployment pipeline on the target system, run:

1. **Regenerate Home Assistant YAML files**:
   ```bash
   python /home/pirate/docker/synapse-ia/radio_injector_v2.py
   ```
2. **Push results JSON to M2**:
   ```bash
   python /home/pirate/docker/synapse-ia/fix_radio_json.py
   ```
3. **Deploy config & restart M2 panel**:
   ```bash
   python /home/pirate/docker/synapse-ia/push_to_m2.py
   ```
4. **Run Stream Verification**:
   ```bash
   python3 /home/pirate/docker/synapse-ia/verify_radio_streams.py
   ```
   If all streams are functioning correctly, the verification script will exit with code `0`.
