import requests
import json

api_key = "sk_d5d93912bf57136bdb1ba78cb6e085d823752ce5bddde26e"
url = "https://api.elevenlabs.io/v1/voices"

headers = {
    "xi-api-key": api_key
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    voices = response.json()["voices"]
    print(f"Found {len(voices)} voices available for your account:")
    for v in voices:
        print(f"- {v['name']} (ID: {v['voice_id']})")
else:
    print(f"Error: {response.status_code} - {response.text}")
