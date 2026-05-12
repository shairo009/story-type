import os
import urllib.parse
import time
import random
import subprocess

class ImageEngine:
    def __init__(self):
        self.base_url = "https://pollinations.ai/p/"

    def generate_image(self, prompt, output_path):
        print(f"Generating image via Playwright (Ultra Stealth Mode)...")
        
        try:
            clean_prompt = prompt.split("Panel")[0].strip()[:100]
            encoded_prompt = urllib.parse.quote(clean_prompt)
            seed = random.randint(1, 99999)
            url = f"{self.base_url}{encoded_prompt}?width=720&height=1280&model=flux&seed={seed}"
            
            # Use PowerShell to download the file (Windows native, harder to block)
            ps_command = f'Invoke-WebRequest -Uri "{url}" -OutFile "{output_path}" -UserAgent "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"'
            
            subprocess.run(["powershell", "-Command", ps_command], capture_output=True)
            
            if os.path.exists(output_path) and os.path.getsize(output_path) > 15000:
                print(f"Image saved via PowerShell: {output_path}")
                time.sleep(10) # Cool-down
                return output_path
            else:
                print(f"PowerShell download failed or file too small.")
                return None
                
        except Exception as e:
            print(f"Error: {e}")
            return None
