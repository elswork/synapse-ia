import requests
import json

def main():
    api_key = "AIzaSyApBKxKkdLkgeQ4t0o_bKI7-SpGsJmpNPo"
    doc_id = "11PH_Mj05oJtgStCXLTMDXxJtKyeC37ATPIvOtG226Kk"
    
    url = f"https://docs.googleapis.com/v1/documents/{doc_id}?key={api_key}"
    print(f"Fetching document {doc_id} using API Key...")
    
    response = requests.get(url)
    print("Status Code:", response.status_code)
    
    try:
        data = response.json()
        if response.status_code == 200:
            print("Document Title:", data.get("title"))
            print("Document Keys:", data.keys())
            # Let's inspect the body content
            body = data.get("body", {})
            content = body.get("content", [])
            print(f"Found {len(content)} structural elements.")
            
            # Let's extract text
            text = ""
            for elem in content:
                paragraph = elem.get("paragraph")
                if paragraph:
                    elements = paragraph.get("elements", [])
                    for e in elements:
                        text_run = e.get("textRun")
                        if text_run:
                            text += text_run.get("content", "")
            print("\n--- Document Text Content ---")
            print(text)
            print("-----------------------------\n")
        else:
            print("Error Response:")
            print(json.dumps(data, indent=2))
    except Exception as e:
        print("Failed to parse response:", e)
        print("Raw response:", response.text[:500])

if __name__ == "__main__":
    main()
