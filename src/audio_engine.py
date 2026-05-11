import os
import requests
from dotenv import load_dotenv

load_dotenv()

class AudioEngine:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY")
        self.voice_id = os.getenv("ELEVENLABS_VOICE_ID") or "nPczCjzI2devNBz1zQrb"
        self.model_id = os.getenv("ELEVENLABS_MODEL_ID") or "eleven_flash_v2_5"
        
        if not self.api_key:
            print("Warning: ELEVENLABS_API_KEY not found. Audio generation will fail.")

    async def generate_audio(self, text, output_path):
        print(f"Generating audio for text: {text[:30]}... using ElevenLabs")
        
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
        data = {
            "text": text,
            "model_id": self.model_id,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }
        
        try:
            response = requests.post(url, json=data, headers=headers)
            if response.status_code == 200:
                with open(output_path, "wb") as f:
                    f.write(response.content)
                return True
            else:
                print(f"Error from ElevenLabs: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"Exception during audio generation: {e}")
            return False

if __name__ == "__main__":
    # Test requires local ELEVENLABS_API_KEY
    import asyncio
    engine = AudioEngine()
    asyncio.run(engine.generate_audio("Testing ElevenLabs integration in the pipeline.", "test_pipeline_audio.mp3"))
