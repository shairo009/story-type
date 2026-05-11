import asyncio
import edge_tts
import os

class AudioEngine:
    def __init__(self, voice="en-US-ChristopherNeural"):
        self.voice = voice

    async def generate_audio(self, text, filename):
        print(f"Generating audio for text: {text[:30]}...")
        communicate = edge_tts.Communicate(text, self.voice)
        await communicate.save(filename)
        return True

if __name__ == "__main__":
    # Test run
    async def main():
        engine = AudioEngine()
        await engine.generate_audio("Hello, this is a test of the automated story voiceover.", "test_audio.mp3")
        print("Audio generated successfully!")

    asyncio.run(main())
