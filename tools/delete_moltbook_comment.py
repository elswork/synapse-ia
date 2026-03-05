import requests

API_KEY = "moltbook_sk_jTO_cK6BLuqpwgU0CAgnOZReUccM5xB3"
POST_ID = "076c997f-9e11-47b2-9087-415d131c800b"
COMMENT_ID = "5ae6455d-ce50-4d18-bfe4-0bf26d74b061"
BASE_URL = "https://www.moltbook.com/api/v1"

def delete_comment():
    url = f"{BASE_URL}/comments/{COMMENT_ID}"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    print(f"🗑️ Purgando comentario {COMMENT_ID} del post {POST_ID}...")
    response = requests.delete(url, headers=headers)
    
    if response.status_code in [200, 204]:
        print("✅ Comentario eliminado con éxito de la red.")
    else:
        print(f"❌ Fallo en la purga. Código de estado: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    delete_comment()
