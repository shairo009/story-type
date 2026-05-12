import urllib.parse
import urllib.request
import random

def generate_consistent_comic(prompt, output_path):
    print("Generating consistent 4-panel comic via Pollinations AI...")
    
    # Master consistency and style prompt
    # Defining exact character looks and the 4-panel strip format
    consistency_rules = (
        "Andy is a young boy with curly brown hair, glasses, a white shirt and red tie. "
        "Mona is a young girl with short black hair and a pink-and-purple striped shirt. "
    )
    style_rules = (
        "A 4-panel comic strip, divided into a 2x2 grid of 4 separate square panels in one single image. "
        "vibrant flat colors, hand-drawn cartoon style, speech bubbles. symmetrical perfect eyes, detailed face, masterpiece. "
        "NO deformed eyes, NO bad anatomy, NO mutant, NO weird faces."
    )
    
    full_prompt = f"{prompt}. {consistency_rules}. {style_rules}"
    print(f"Full Prompt: {full_prompt}")
    
    seed = random.randint(1000000, 9999999)
    # Cache buster added to URL
    url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(full_prompt)}?width=1024&height=1024&seed={seed}&nologo=true&cache_buster={random.randint(1, 100000)}"
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    req = urllib.request.Request(url, headers=headers)
    
    import time
    for attempt in range(10): # Try up to 10 times
        try:
            with urllib.request.urlopen(req) as response:
                with open(output_path, "wb") as f:
                    f.write(response.read())
            print(f"Success! Image saved at {output_path}")
            return
        except urllib.error.HTTPError as e:
            if e.code == 429:
                print(f"Attempt {attempt+1}: 429 Too Many Requests. Retrying in 5 seconds...")
                time.sleep(5)
            else:
                print(f"Failed to generate image: {e}")
                return
        except Exception as e:
            print(f"Failed to generate image: {e}")
            return
    print("Failed after 10 attempts.")


if __name__ == "__main__":
    # A test prompt similar to the user's reference
    prompt = "Andy holding a strange machine with a red button, Mona looking worried next to him"
    output_file = "test_consistent_comic.png"
    
    generate_consistent_comic(prompt, output_file)
