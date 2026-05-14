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
        # Master Style from 'Comic Book Creator' skill
        layout_rules = "A 4-panel comic strip, 2x2 grid, square panels"
        style_dna = "American Superhero Comic style, bold black outlines, CMYK halftone dots, primary colors, dramatic shadows, action poses"
        quality_boost = "pop art, thick lines, flat colors, high contrast, crisp details, NO shading, NO realism"
        negative_rules = "NO deformed eyes, NO bad anatomy, NO mutant, NO weird faces, NO text, NO blurry"
        master_style = f"{layout_rules}. {style_dna}. {quality_boost}. {negative_rules}."

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
                        
                        # Apply Comic Post-processing
                        try:
                            self.apply_comic_effects(output_path)
                        except Exception as e:
                            print(f"  Comic effect error: {e}")
                            
                        return output_path
                    else:
                        print(f"  Attempt {attempt+1}: Pollinations returned small/invalid data ({len(data)} bytes), retrying...")
            except Exception as ex:
                print(f"  Attempt {attempt+1}: Pollinations error — {ex}")

            wait = 3 * (attempt + 1)
            print(f"  Waiting {wait}s before retry...")
            time.sleep(wait)

        print(f"  ERROR: All {retries} attempts failed for Pollinations. Trying Fallback API (Hercai)...")
        try:
            # Fallback API: Hercai (Free)
            hercai_url = f"https://hercai.onrender.com/v3/text2image?prompt={urllib.parse.quote(clean_prompt)}"
            response = requests.get(hercai_url, timeout=60)
            if response.status_code == 200:
                res_json = response.json()
                img_url = res_json.get("url")
                if img_url:
                    img_data = requests.get(img_url).content
                    if self.is_valid_image(img_data):
                        with open(output_path, "wb") as f:
                            f.write(img_data)
                        self.apply_comic_effects(output_path)
                        print(f"  Image OK via Hercai Fallback.")
                        return output_path
        except Exception as e:
            print(f"  Hercai Fallback also failed: {e}")

        return None

    def apply_comic_effects(self, image_path):
        from PIL import Image, ImageDraw, ImageFilter, ImageOps
        
        img = Image.open(image_path).convert("RGB")
        
        # 1. Halftone Dot Effect
        def get_halftone(image, dot_spacing=6):
            img_gray = image.convert('L')
            result = Image.new('RGB', image.size, 'white')
            draw = ImageDraw.Draw(result)
            w, h = image.size
            for y in range(0, h, dot_spacing):
                for x in range(0, w, dot_spacing):
                    brightness = img_gray.getpixel((x, y)) / 255
                    radius = int((1 - brightness) * dot_spacing * 0.4)
                    if radius > 0:
                        draw.ellipse([x-radius, y-radius, x+radius, y+radius], fill='black')
            return result

        ht = get_halftone(img)
        img = Image.blend(img, ht, 0.15) # Light comic texture

        # 2. Bold Outline Extraction
        edges = img.filter(ImageFilter.FIND_EDGES).convert('L')
        edges = ImageOps.invert(edges)
        # Binarize to make it crisp
        edges = edges.point(lambda p: 0 if p < 128 else 255)
        
        # Thicken outlines
        edges = edges.filter(ImageFilter.MaxFilter(3))
        
        # Combine
        img = Image.composite(img, Image.new("RGB", img.size, "black"), edges)
        
        img.save(image_path)
        print(f"  Applied Halftone and Outlines to {os.path.basename(image_path)}")
