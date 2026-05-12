import urllib.parse
import urllib.request
import random
import time
from PIL import Image, ImageDraw, ImageFont
import textwrap

def generate_single_panel(prompt, output_path):
    print(f"Generating panel: {prompt[:50]}...")
    seed = random.randint(1000000, 9999999)
    # Master style for a simple, flat cartoon (matching the user's reference)
    style = "childrens coloring book style, extremely simple flat vector art, Peanuts comic style, simple dots for eyes, solid colors, NO shading, NO realism, 2d cartoon graphic"
    full_prompt = f"{prompt}. {style}"
    
    url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(full_prompt)}?width=512&height=512&seed={seed}&nologo=true&cache_buster={random.randint(1, 100000)}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    req = urllib.request.Request(url, headers=headers)
    
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req) as response:
                with open(output_path, "wb") as f:
                    f.write(response.read())
            return True
        except Exception as e:
            time.sleep(2)
    return False

def add_speech_bubble(img, dialogue):
    draw = ImageDraw.Draw(img)
    width, height = img.size
    try: font = ImageFont.truetype("C:\\Windows\\Fonts\\arialbd.ttf", 20)
    except: font = ImageFont.load_default()

    wrapper = textwrap.TextWrapper(width=25)
    lines = wrapper.wrap(text=dialogue)
    line_height = 25
    
    bubble_w = max([draw.textbbox((0,0), line, font=font)[2] for line in lines]) + 40
    bubble_h = len(lines) * line_height + 30
    
    b_x, b_y = 20, 20
    draw.ellipse([b_x, b_y, b_x + bubble_w, b_y + bubble_h], fill="white", outline="black", width=2)
    
    # Tail
    draw.polygon([(b_x + 30, b_y + bubble_h - 10), (b_x + 40, b_y + bubble_h + 20), (b_x + 50, b_y + bubble_h - 5)], fill="white", outline="black")
    
    y_text = b_y + 15
    for line in lines:
        tw = draw.textbbox((0,0), line, font=font)[2]
        draw.text((b_x + (bubble_w - tw)/2, y_text), line, font=font, fill="black")
        y_text += line_height
    return img

def create_4_panel_grid():
    c_andy = "A boy named Andy with curly brown hair, round glasses, and a white shirt."
    c_mona = "A girl named Mona with short black hair and a pink striped shirt."
    panels_data = [
        {"prompt": f"{c_andy} holding a futuristic yellow horn-shaped gadget in his right hand. {c_mona} is standing far away from him, pointing at it.", "dialogue": "What is this machine?"},
        {"prompt": f"Close up of {c_mona} looking scared. Her hands are up in defense.", "dialogue": "Don't touch it Andy!"},
        {"prompt": f"Close up of {c_andy} excitedly pressing a big red button on the yellow gadget.", "dialogue": "I'm going to press it!"},
        {"prompt": f"{c_andy} and {c_mona} looking shocked. A giant swirling blue portal is logically placed behind them.", "dialogue": "Oh no! A portal!"}
    ]
    
    panel_imgs = []
    for i, data in enumerate(panels_data):
        path = f"temp_p{i}.png"
        if generate_single_panel(data["prompt"], path):
            img = Image.open(path).convert("RGBA")
            img = add_speech_bubble(img, data["dialogue"])
            panel_imgs.append(img)
    
    if len(panel_imgs) == 4:
        # Create 1024x1024 canvas (plus borders)
        border = 10
        grid_w = 512 * 2 + border * 3
        grid_h = 512 * 2 + border * 3
        grid_img = Image.new('RGB', (grid_w, grid_h), color='white')
        
        # Paste panels
        grid_img.paste(panel_imgs[0], (border, border)) # Top Left
        grid_img.paste(panel_imgs[1], (512 + border*2, border)) # Top Right
        grid_img.paste(panel_imgs[2], (border, 512 + border*2)) # Bottom Left
        grid_img.paste(panel_imgs[3], (512 + border*2, 512 + border*2)) # Bottom Right
        
        # Draw borders (Black grid lines)
        draw = ImageDraw.Draw(grid_img)
        draw.line([(0, 512 + border*1.5), (grid_w, 512 + border*1.5)], fill="black", width=border)
        draw.line([(512 + border*1.5, 0), (512 + border*1.5, grid_h)], fill="black", width=border)
        draw.rectangle([(0,0), (grid_w, grid_h)], outline="black", width=border)
        
        output_file = "perfect_4_panel_grid_v2.png"
        grid_img.save(output_file)
        print(f"Perfect Grid Created: {output_file}")
    else:
        print("Failed to generate all panels.")

if __name__ == "__main__":
    create_4_panel_grid()
