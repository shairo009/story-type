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
        # Apply the Master Style with strict layout rules for a 2x2 4-panel grid and V2 simple cartoon style
        layout_rules = "A 4-panel comic strip, divided into a 2x2 grid of 4 separate square panels in one single image"
        quality_boost = "childrens coloring book style, extremely simple flat vector art, Peanuts comic style, simple dots for eyes, solid colors, NO shading, NO realism, 2d cartoon graphic"
        negative_rules = "NO deformed eyes, NO bad anatomy, NO mutant, NO weird faces, characters MUST NOT share hair styles"
        master_style = f"{layout_rules}. {quality_boost}. {negative_rules}."
        
        clean_prompt = f"{master_style} Narrative: " + prompt.split("Panel")[0].strip()[:150]
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
