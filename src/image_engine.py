import os
import requests
import time
import random
import urllib.parse
from dotenv import load_dotenv

load_dotenv()

class ImageEngine:
    def __init__(self):
        self.hf_token = os.getenv("HF_TOKEN")
        self.hf_url = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"

    def generate_image(self, prompt, output_path):
        print(f"Generating image for: {prompt[:50]}...")
        
        # Try Hugging Face First
        if self.hf_token:
            print("Trying Hugging Face (FLUX.1)...")
            try:
                headers = {"Authorization": f"Bearer {self.hf_token}"}
                response = requests.post(self.hf_url, headers=headers, json={"inputs": prompt}, timeout=60)
                if response.status_code == 200:
                    with open(output_path, "wb") as f:
                        f.write(response.content)
                    print("Success via HF!")
                    return output_path
                else:
                    print(f"HF Failed ({response.status_code}). Trying Pollinations...")
            except Exception as e:
                print(f"HF Exception: {e}")

        # Fallback to Pollinations (Free, no key)
        try:
            print("Using Pollinations.ai...")
            encoded = urllib.parse.quote(prompt)
            seed = random.randint(1, 99999)
            # Using turbo for faster results
            url = f"https://image.pollinations.ai/prompt/{encoded}?width=720&height=1280&model=flux&seed={seed}&nologo=true"
            r = requests.get(url, timeout=60)
            if r.status_code == 200:
                with open(output_path, "wb") as f:
                    f.write(r.content)
                print("Success via Pollinations!")
                return output_path
        except Exception as e:
            print(f"Pollinations Error: {e}")

        return None
