import requests
import json

api_key = "sk_d5d93912bf57136bdb1ba78cb6e085d823752ce5bddde26e"
url = "https://api.elevenlabs.io/v1/text-to-speech/nPczCjzI2devNBz1zQrb" # Brian

headers = {
    "Accept": "audio/mpeg",
    "Content-Type": "application/json",
    "xi-api-key": api_key
}

data = {
    "text": "Hello! This is Brian from ElevenLabs. Your YouTube Shorts pipeline is going to sound amazing with this voice.",
    "model_id": "eleven_flash_v2_5",
    "voice_settings": {
        "stability": 0.5,
        "similarity_boost": 0.5
    }
}

print("Testing ElevenLabs API...")
response = requests.post(url, json=data, headers=headers)

if response.status_code == 200:
    with open("test_elevenlabs.mp3", "wb") as f:
        f.write(response.content)
    print("✅ ElevenLabs test successful! Audio saved as 'test_elevenlabs.mp3'")
else:
    print(f"❌ ElevenLabs test failed: {response.status_code} - {response.text}")
