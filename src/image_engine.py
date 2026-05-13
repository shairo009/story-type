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
        if len(data) < 5000:
            return False
        return data.startswith(b'\xff\xd8') or data.startswith(b'\x89PNG')

    def generate_image(self, prompt, output_path, retries=4):
        layout_rules = "A 4-panel comic strip, divided into a 2x2 grid of 4 separate square panels in one single image"
        quality_boost = "childrens coloring book style, extremely simple flat vector art, Peanuts comic style, simple dots for eyes, solid colors, NO shading, NO realism, 2d cartoon graphic"
        negative_rules = "NO deformed eyes, NO bad anatomy, NO mutant, NO weird faces, characters MUST NOT share hair styles"
        master_style = f"{layout_rules}. {quality_boost}. {negative_rules}."

        clean_prompt = f"{master_style} Narrative: " + prompt.split("Panel")[0].strip()[:150]
        print(f"Generating image (prompt length={len(clean_prompt)})...")

        for attempt in range(retries):
            seed = random.randint(1, 9999999)
            try:
                url = (
                    f"https://image.pollinations.ai/prompt/"
                    f"{urllib.parse.quote(clean_prompt)}"
                    f"?width=720&height=1280&seed={seed}&nologo=true"
                )
                headers = {'User-Agent': 'Mozilla/5.0'}
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=60) as response:
                    data = response.read()
                    if self.is_valid_image(data):
                        with open(output_path, "wb") as f:
                            f.write(data)
                        self.last_image_path = output_path
                        print(f"  Image OK via Pollinations (attempt {attempt+1}, seed={seed}, {len(data)//1024}KB)")
                        return output_path
                    else:
                        print(f"  Attempt {attempt+1}: Pollinations returned small/invalid data ({len(data)} bytes), retrying...")
            except Exception as ex:
                print(f"  Attempt {attempt+1}: Pollinations error — {ex}")

            wait = 3 * (attempt + 1)
            print(f"  Waiting {wait}s before retry...")
            time.sleep(wait)

        print(f"  ERROR: All {retries} attempts failed for this scene. No fallback used.")
        return None
