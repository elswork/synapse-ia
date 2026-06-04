import json
import os

path = "/home/pirate/.config/gws/token_cache.json"
print("File exists:", os.path.exists(path))
if os.path.exists(path):
    print("File size:", os.path.getsize(path))
    try:
        with open(path, "rb") as f:
            data = f.read()
            print("First 100 bytes:", data[:100])
            # Try to decode as string
            text = data.decode("utf-8", errors="ignore")
            print("Text start:", text[:300])
            # Try parsing as json
            js = json.loads(text)
            print("Successfully parsed as JSON!")
            print("Keys:", js.keys())
    except Exception as e:
        print("Error:", e)
