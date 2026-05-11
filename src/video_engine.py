from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, TextClip, CompositeVideoClip
import os

class VideoEngine:
    def __init__(self, size=(1080, 1920)):
        self.size = size

    def create_scene_clip(self, image_path, audio_path, text):
        audio = AudioFileClip(audio_path)
        duration = audio.duration
        
        # Load image and resize to fill the screen
        clip = ImageClip(image_path).set_duration(duration)
        clip = clip.resize(height=self.size[1])
        
        # Center crop to 1080x1920
        w, h = clip.size
        clip = clip.crop(x1=(w - self.size[0])/2, y1=0, x2=(w + self.size[0])/2, y2=self.size[1])
        
        # Simple zoom effect (Ken Burns)
        clip = clip.resize(lambda t: 1 + 0.05 * t/duration)
        
        # Add subtitles
        txt_clip = TextClip(
            text, 
            fontsize=70, 
            color='white', 
            font='Arial-Bold', 
            stroke_color='black', 
            stroke_width=2, 
            method='caption',
            size=(self.size[0]*0.8, None)
        ).set_duration(duration).set_position(('center', 1400))
        
        video = CompositeVideoClip([clip, txt_clip])
        video = video.set_audio(audio)
        
        return video

    def compose_video(self, scenes, output_filename):
        # scenes is a list of dicts: {"image": path, "audio": path, "text": text}
        clips = []
        for scene in scenes:
            clip = self.create_scene_clip(scene["image"], scene["audio"], scene["text"])
            clips.append(clip)
            
        final_video = concatenate_videoclips(clips, method="compose")
        final_video.write_videofile(output_filename, fps=24, codec="libx264", audio_codec="aac")
        return True

if __name__ == "__main__":
    # Note: TextClip requires ImageMagick installed on the system.
    print("VideoEngine test requires ImageMagick and assets. Skipping direct test.")
