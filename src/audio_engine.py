import os
import requests
from dotenv import load_dotenv

load_dotenv()

class AudioEngine:
    def __init__(self, api_key=None):
        self.api_key = (api_key or os.getenv("ELEVENLABS_API_KEY") or "").strip()
        self.voice_id = (os.getenv("ELEVENLABS_VOICE_ID") or "nPczCjzI2devNBz1zQrb").strip()
        self.model_id = (os.getenv("ELEVENLABS_MODEL_ID") or "eleven_flash_v2_5").strip()
        
        if not self.api_key:
            print("Warning: ELEVENLABS_API_KEY not found. Audio generation will fail.")

    async def generate_audio(self, text, output_path):
        print(f"Generating audio for text: {text[:30]}... using ElevenLabs")
        
        # 1. Try ElevenLabs
        if self.api_key:
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.api_key
            }
            data = {
                "text": text,
                "model_id": self.model_id,
                "voice_settings": {"stability": 0.5, "similarity_boost": 0.5}
            }
            try:
                response = requests.post(url, json=data, headers=headers)
                if response.status_code == 200:
                    with open(output_path, "wb") as f:
                        f.write(response.content)
                    return True
                else:
                    print(f"ElevenLabs failed ({response.status_code}). Switching to Fallback...")
            except Exception as e:
                print(f"ElevenLabs exception: {e}. Switching to Fallback...")
        
        # 2. Fallback: Edge TTS (Free, high quality)
        print("Audio Fallback: Edge TTS (Free)...")
        try:
            import edge_tts
            # Using a Hindi/English voice for Hinglish content
            voice = "hi-IN-MadhurNeural"
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(output_path)
            if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                return True
        except Exception as e:
            print(f"Edge TTS failed: {e}")

        # 3. Last Resort: gTTS
        print("Audio Fallback: gTTS (Free)...")
        try:
            from gtts import gTTS
            tts = gTTS(text=text, lang='hi')
            tts.save(output_path)
            return True
        except Exception as e:
            print(f"gTTS failed: {e}")

        return False

if __name__ == "__main__":
    # Test requires local ELEVENLABS_API_KEY
    import asyncio
    engine = AudioEngine()
    asyncio.run(engine.generate_audio("Testing ElevenLabs integration in the pipeline.", "test_pipeline_audio.mp3"))
