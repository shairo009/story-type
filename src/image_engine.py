import os
import requests
import time
import random
import urllib.parse
import urllib.request
from dotenv import load_dotenv

load_dotenv()

class ImageEngine:
    def __init__(self):
        self.last_image_path = None

    def is_valid_image(self, data):
        if len(data) < 2000: return False
        return data.startswith(b'\xff\xd8') or data.startswith(b'\x89PNG')

    def generate_image(self, prompt, output_path, retries=3):
        clean_prompt = prompt.split("Panel")[0].strip()[:100] + ", vibrant comic style"
        print(f"Generating image: {clean_prompt}...")
        
        for attempt in range(retries):
            # Try Hercai V3 Direct
            try:
                url = f"https://hercai.onrender.com/v3/text2image?prompt={urllib.parse.quote(clean_prompt)}"
                r = requests.get(url, timeout=30)
                if r.status_code == 200:
                    img_url = r.json().get("url")
                    if img_url:
                        # Use urllib.request for the actual image download
                        headers = {'User-Agent': 'Mozilla/5.0'}
                        req = urllib.request.Request(img_url, headers=headers)
                        with urllib.request.urlopen(req) as response:
                            data = response.read()
                            if self.is_valid_image(data):
                                with open(output_path, "wb") as f: f.write(data)
                                self.last_image_path = output_path
                                print(f"Success via Hercai!")
                                return output_path
            except Exception: pass

            # Try Pollinations V1 Direct
            try:
                seed = random.randint(1, 1000000)
                url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(clean_prompt)}?width=720&height=1280&seed={seed}&nologo=true"
                headers = {'User-Agent': 'Mozilla/5.0'}
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req) as response:
                    data = response.read()
                    if self.is_valid_image(data):
                        with open(output_path, "wb") as f: f.write(data)
                        self.last_image_path = output_path
                        print(f"Success via Pollinations!")
                        return output_path
            except Exception: pass
            
            time.sleep(2)

        # Fallback to last successful image
        if self.last_image_path and os.path.exists(self.last_image_path):
            print("Reusing last valid image as fallback.")
            import shutil
            shutil.copy(self.last_image_path, output_path)
            return output_path
        
        return None
