import os
import requests
import urllib.parse
import urllib.request
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import random
import textwrap

# 1. Image Generation via Pollinations (as requested)
def generate_base_image(prompt, output_path):
    print("Generating base image via Pollinations AI...")
    seed = random.randint(1, 1000000)
    # Appending skill instructions to prompt
    full_prompt = f"{prompt}, American Superhero Comic style, bold black outlines, vibrant flat colors, high quality"
    url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(full_prompt)}?width=720&height=1280&seed={seed}&nologo=true"
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        with open(output_path, "wb") as f:
            f.write(response.read())
    return output_path

# 2. Skill implementation using Pillow (Speech Bubble + Caption)
def apply_comic_skill(image_path, narration, dialogue, output_path):
    print("Applying Comic Skill (Speech Bubbles & Captions)...")
    img = Image.open(image_path).convert("RGBA")
    draw = ImageDraw.Draw(img)
    width, height = img.size

    # Try to load a comic-style font, fallback to default
    try:
        font_caption = ImageFont.truetype("C:\\Windows\\Fonts\\impact.ttf", 35)
        font_dialogue = ImageFont.truetype("C:\\Windows\\Fonts\\comic.ttf", 30) # Comic Sans
    except:
        font_caption = ImageFont.load_default()
        font_dialogue = ImageFont.load_default()

    # --- Draw Caption Box (Narration) ---
    # Draw yellow box at the bottom
    caption_margin = 20
    wrapper = textwrap.TextWrapper(width=45)
    lines = wrapper.wrap(text=narration.upper())
    line_height = 40
    box_height = len(lines) * line_height + 40
    
    box_y1 = height - box_height - caption_margin
    box_y2 = height - caption_margin
    
    # Yellow fill, Black outline
    draw.rectangle([caption_margin, box_y1, width - caption_margin, box_y2], 
                   fill="#FFD700", outline="black", width=4)
    
    y_text = box_y1 + 20
    for line in lines:
        try:
            left, top, right, bottom = draw.textbbox((0, 0), line, font=font_caption)
            text_w = right - left
        except: text_w = 0
        draw.text(((width - text_w) / 2, y_text), line, font=font_caption, fill="black")
        y_text += line_height

    # --- Draw Speech Bubble (Dialogue) ---
    if dialogue:
        wrapper = textwrap.TextWrapper(width=30)
        bubble_lines = wrapper.wrap(text=dialogue)
        b_line_height = 35
        
        # Calculate bubble size
        max_width = 0
        for line in bubble_lines:
            try:
                l, t, r, b = draw.textbbox((0, 0), line, font=font_dialogue)
                if (r-l) > max_width: max_width = (r-l)
            except: pass
            
        bubble_w = max_width + 60
        bubble_h = len(bubble_lines) * b_line_height + 40
        
        # Position at top right
        b_x = width - bubble_w - 40
        b_y = 60
        
        # Draw ellipse (the bubble)
        draw.ellipse([b_x, b_y, b_x + bubble_w, b_y + bubble_h], fill="white", outline="black", width=3)
        
        # Draw the tail of the bubble (pointing down-left towards character)
        tail_x = b_x + bubble_w * 0.2
        tail_y = b_y + bubble_h - 10
        point_x = tail_x - 40
        point_y = tail_y + 50
        draw.polygon([(tail_x, tail_y), (tail_x + 30, tail_y - 10), (point_x, point_y)], fill="white", outline="black")
        # redraw line to clean up internal polygon border
        draw.line([(tail_x, tail_y), (tail_x + 30, tail_y - 10)], fill="white", width=4)
        
        # Draw text inside bubble
        y_bubble_text = b_y + 20
        for line in bubble_lines:
            try:
                l, t, r, b = draw.textbbox((0, 0), line, font=font_dialogue)
                text_w = (r-l)
            except: text_w = 0
            draw.text((b_x + (bubble_w - text_w) / 2, y_bubble_text), line, font=font_dialogue, fill="black")
            y_bubble_text += b_line_height

    # Convert back to RGB and save
    final_img = img.convert("RGB")
    final_img.save(output_path)
    print(f"Comic Skill applied successfully! Saved at {output_path}")

if __name__ == "__main__":
    prompt = "A cool hacker staring at multiple glowing screens in a dark room"
    narration = "Dher saari screens ke beech, usne system ko bypass kar diya tha."
    dialogue = "I am in! Ab dekhte hain sach kya hai."
    
    base_img = "test_base.png"
    final_img = "test_comic_skill.png"
    
    generate_base_image(prompt, base_img)
    apply_comic_skill(base_img, narration, dialogue, final_img)
