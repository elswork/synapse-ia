import requests
import json

API_KEY = "moltbook_sk_jTO_cK6BLuqpwgU0CAgnOZReUccM5xB3"
POST_ID = "76c0b858-bf35-4f6d-9e17-84d9e4f92474"
BASE_URL = "https://www.moltbook.com/api/v1"

def get_comments():
    url = f"{BASE_URL}/posts/{POST_ID}/comments"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        with open("/tmp/molt_comments_final.json", "w") as f:
            json.dump(response.json(), f, indent=4)
        print("✅ Comments fetched and saved to /tmp/molt_comments_final.json")
    else:
        print(f"❌ Failed to fetch comments. Status: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    get_comments()
