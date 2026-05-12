import os
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips
from PIL import Image, ImageDraw, ImageFont
import textwrap

class VideoEngine:
    def __init__(self, output_dir="outputs"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def add_text_to_image(self, image_path, text, output_path):
        # We no longer apply manual text overlay.
        # Just copy the image directly or return the path.
        import shutil
        if image_path != output_path:
            shutil.copy(image_path, output_path)
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
            img_clip = img_clip.resized(newsize=(w, h))
            
            clip = img_clip.with_duration(audio.duration)
            clip = clip.with_audio(audio)
            clips.append(clip)
            
        # Concatenate all scenes
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
        
        # Explicitly close clips to release file handles
        for clip in clips:
            clip.close()
        final_video.close()
        
        # Cleanup temp images
        for i in range(len(scenes)):
            if os.path.exists(f"temp_scene_{i}.png"):
                os.remove(f"temp_scene_{i}.png")
                
        return output_path
