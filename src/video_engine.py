import os
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
from PIL import Image, ImageDraw, ImageFont
import textwrap

class VideoEngine:
    def __init__(self, output_dir="outputs"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def add_text_to_image(self, image_path, text, output_path):
        # Open the image
        img = Image.open(image_path)
        draw = ImageDraw.Draw(img)
        width, height = img.size
        
        # Use a punchy comic-style font (Roman script)
        font_paths = [
            "C:\\Windows\\Fonts\\arialbd.ttf",
            "C:\\Windows\\Fonts\\impact.ttf",
            "hindi_font.ttf"
        ]
        
        font = None
        for path in font_paths:
            if os.path.exists(path):
                font = ImageFont.truetype(path, 45)
                break
        
        if not font:
            font = ImageFont.load_default()

        # Wrap text
        wrapper = textwrap.TextWrapper(width=40)
        lines = wrapper.wrap(text=text)
        
        # Draw a semi-transparent background box for the text
        margin = 20
        line_height = 50
        box_height = len(lines) * line_height + 40
        
        # Position at the bottom
        shape = [margin, height - box_height - margin, width - margin, height - margin]
        draw.rectangle(shape, fill=(0, 0, 0, 180)) # Black box with transparency
        
        # Draw text
        y_text = height - box_height
        for line in lines:
            # Use textbbox for centering (available in newer Pillow)
            try:
                left, top, right, bottom = draw.textbbox((0, 0), line, font=font)
                text_width = right - left
            except:
                text_width = 0 # Fallback
            
            draw.text(((width - text_width) / 2, y_text), line, font=font, fill="white")
            y_text += line_height
            
        img.save(output_path)
        return output_path

    def compose_video(self, scenes, output_filename):
        clips = []
        
        for i, scene in enumerate(scenes):
            image_path = scene['image_path']
            audio_path = scene['audio_path']
            narration = scene['narration']
            
            # Step: Add text overlay to image before creating clip
            temp_image_with_text = f"temp_scene_{i}.png"
            self.add_text_to_image(image_path, narration, temp_image_with_text)
            
            audio = AudioFileClip(audio_path)
            # Ensure dimensions are even (H.264 requirement)
            img_clip = ImageClip(temp_image_with_text)
            w, h = img_clip.size
            if w % 2 != 0: w -= 1
            if h % 2 != 0: h -= 1
            img_clip = img_clip.resize(newsize=(w, h))
            
            clip = img_clip.set_duration(audio.duration)
            clip = clip.set_audio(audio)
            clips.append(clip)
            # audio.close() - Moved to after render
            
        # Concatenate all scenes
        final_video = concatenate_videoclips(clips, method="compose")
        
        output_path = os.path.join(self.output_dir, output_filename)
        # Write to file (using lower bitrate for faster processing on local)
        # Write to file with maximum compatibility (YUV420P is essential for Windows/QuickTime)
        final_video.write_videofile(
            output_path, 
            fps=24, 
            codec="libx264", 
            audio_codec="aac",
            temp_audiofile='temp-audio.m4a',
            remove_temp=True,
            ffmpeg_params=["-pix_fmt", "yuv420p", "-level", "3.0"]
        )
        
        # Explicitly close clips to release file handles
        for clip in clips:
            clip.close()
        final_video.close()
        
        # Cleanup temp images
        for i in range(len(scenes)):
            if os.path.exists(f"temp_scene_{i}.png"):
                os.remove(f"temp_scene_{i}.png")
                
        return output_path
