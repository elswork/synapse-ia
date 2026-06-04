import requests

def main():
    doc_id = "11PH_Mj05oJtgStCXLTMDXxJtKyeC37ATPIvOtG226Kk"
    url = f"https://docs.google.com/document/d/{doc_id}/export?format=txt"
    print(f"Attempting to download document {doc_id} as text...")
    
    response = requests.get(url)
    print("Status Code:", response.status_code)
    if response.status_code == 200:
        print("\n--- Document Plain Text ---")
        print(response.text)
        print("---------------------------\n")
    else:
        print("Failed to download as text. Response body:")
        print(response.text[:500])

if __name__ == "__main__":
    main()
