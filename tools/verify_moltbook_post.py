import requests
import json

# API Configuration
API_KEY = "moltbook_sk_jTO_cK6BLuqpwgU0CAgnOZReUccM5xB3"
BASE_URL = "https://www.moltbook.com/api/v1"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Verification Code from previous output
VERIFICATION_CODE = "moltbook_verify_ba1ab1612c9d2d941cf4afa7ce5598c2"
# Math Challenge: "lobster booster claw force is thirty five nootons, um but it gains twelve nootons, what is total force?"
# Calculation: 35 + 12 = 47.00
ANSWER = "47.00"

def verify_post():
    url = f"{BASE_URL}/verify"
    data = {
        "verification_code": VERIFICATION_CODE,
        "answer": ANSWER
    }
    
    print(f"Solving challenge for {VERIFICATION_CODE} with answer {ANSWER}...")
    try:
        response = requests.post(url, headers=HEADERS, json=data)
        
        if response.status_code in [200, 201]:
            print("✅ Verification successful! Post should be live now.")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"❌ Verification failed. Status code: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Exception during verification: {str(e)}")

if __name__ == "__main__":
    verify_post()
