import os
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips
from PIL import Image, ImageDraw, ImageFont
import textwrap

class VideoEngine:
    def __init__(self, output_dir="outputs"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def add_text_to_image(self, image_path, text, output_path, is_dialogue=True):
        from PIL import Image, ImageDraw, ImageFont
        import textwrap

        img = Image.open(image_path).convert("RGB")
        draw = ImageDraw.Draw(img)
        w, h = img.size

        # 1. Load Font
        font_path = "hindi_font.ttf"
        font_size = 28
        try:
            if os.path.exists(font_path):
                font = ImageFont.truetype(font_path, font_size)
            else:
                font = ImageFont.load_default()
        except:
            font = ImageFont.load_default()

        # 2. Wrap Text
        wrapped_text = textwrap.fill(text, width=28)
        
        # 3. Measure Text
        try:
            bbox = draw.textbbox((0, 0), wrapped_text, font=font)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
        except:
            tw, th = draw.textsize(wrapped_text, font=font)

        pad = 20
        bw = tw + (pad * 2)
        bh = th + (pad * 2)

        if is_dialogue:
            # SPEECH BUBBLE (White Oval with Tail)
            bx = (w - bw) // 2
            by = h - bh - 80 
            
            # Tail
            tx = w // 2
            ty = by + bh
            draw.polygon([(tx - 15, ty - 5), (tx + 15, ty - 5), (tx, ty + 25)], fill="white", outline="black")
            # Oval
            draw.ellipse([bx, by, bx + bw, by + bh], fill="white", outline="black", width=4)
            # Text
            draw.text((bx + pad, by + pad), wrapped_text, font=font, fill="black")
        else:
            # CAPTION BOX (Yellow Rectangle for Narration)
            bx = (w - bw) // 2
            by = 40 # Top of the screen for narration
            
            # Box
            draw.rectangle([bx, by, bx + bw, by + bh], fill="#FFD700", outline="black", width=4)
            # Text
            draw.text((bx + pad, by + pad), wrapped_text, font=font, fill="black")

        img.save(output_path)
        return output_path

    def compose_video(self, scenes, output_filename, apply_overlay=True):
        clips = []
        
        for i, scene in enumerate(scenes):
            image_path = scene['image_path']
            audio_path = scene['audio_path']
            narration = scene.get('narration', '')
            dialogue = scene.get('dialogue', '')
            
            if apply_overlay:
                temp_image_with_text = f"temp_scene_{i}.png"
                if dialogue:
                    self.add_text_to_image(image_path, dialogue, temp_image_with_text, is_dialogue=True)
                else:
                    self.add_text_to_image(image_path, narration, temp_image_with_text, is_dialogue=False)
                processed_image = temp_image_with_text
            else:
                processed_image = image_path
            
            audio = AudioFileClip(audio_path)
            img_clip = ImageClip(processed_image)
            w, h = img_clip.size
            if w % 2 != 0: w -= 1
            if h % 2 != 0: h -= 1
            img_clip = img_clip.resized((w, h))
            
            clip = img_clip.with_duration(audio.duration)
            clip = clip.with_audio(audio)
            clips.append(clip)
            
        final_video = concatenate_videoclips(clips, method="compose")
        
        output_path = os.path.join(self.output_dir, output_filename)
        final_video.write_videofile(
            output_path, 
            fps=24, 
            codec="libx264", 
            audio_codec="aac",
            temp_audiofile='temp-audio.m4a',
            remove_temp=True,
            ffmpeg_params=["-pix_fmt", "yuv420p", "-level", "3.0"]
        )
        
        for clip in clips:
            clip.close()
        final_video.close()
        
        for i in range(len(scenes)):
            if os.path.exists(f"temp_scene_{i}.png"):
                os.remove(f"temp_scene_{i}.png")
                
        return output_path
