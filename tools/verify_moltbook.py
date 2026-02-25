import requests
import json

API_KEY = "moltbook_sk_jTO_cK6BLuqpwgU0CAgnOZReUccM5xB3"
BASE_URL = "https://www.moltbook.com/api/v1"

def verify_comment():
    url = f"{BASE_URL}/verify"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "verification_code": "moltbook_verify_b758b95a6b5e29d82ac44da206f4bd9c",
        "answer": "48.00"
    }
    
    print("Verifying agent identity...")
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code in [200, 201]:
        print("✅ Identity verified! Comment is now live.")
        print(response.json())
    else:
        print(f"❌ Verification failed. Status code: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    verify_comment()
