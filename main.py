import asyncio
import os
import shutil
import random
from datetime import datetime
from dotenv import load_dotenv

from src.story_engine import StoryEngine
from src.image_engine import ImageEngine
from src.audio_engine import AudioEngine
from src.video_engine import VideoEngine
from src.uploader import YouTubeUploader

load_dotenv()

# Topics to choose from automatically
TOPICS = [
    "Mona and Andy find a time machine", "Mona and Andy explore a haunted school", 
    "Mona and Andy get lost in a dinosaur forest", "Mona and Andy discover a secret alien base",
    "Mona and Andy try to bake a giant cake", "Mona and Andy find a magic portal in the attic"
]

async def run_pipeline():
    # Setup directories
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_dir = f"temp_{timestamp}"
    os.makedirs(temp_dir, exist_ok=True)
    
    try:
        # 1. Generate Story
        print("--- Step 1: Generating Story ---")
        story_engine = StoryEngine()
        topic = random.choice(TOPICS)
        story_data = story_engine.generate_story(topic)
        if not story_data:
            return
        
        title = story_data.get("title", "AI Story")
        print(f"Title: {title}")

        # 2. Generate Assets for each scene
        print("--- Step 2: Generating Assets ---")
        image_engine = ImageEngine()
        audio_engine = AudioEngine()
        
        scenes_data = []
        for i, scene in enumerate(story_data["scenes"]):
            print(f"Processing Scene {i+1}...")
            img_path = os.path.join(temp_dir, f"scene_{i}.png")
            aud_path = os.path.join(temp_dir, f"scene_{i}.mp3")
            
            # Generate Image
            image_engine.generate_image(scene["image_prompt"], img_path)
            
            # Generate Audio
            await audio_engine.generate_audio(scene["narration"], aud_path)
            
            scenes_data.append({
                "image": img_path,
                "audio": aud_path,
                "text": scene["narration"]
            })

        # 3. Compose Video
        print("--- Step 3: Composing Video ---")
        video_engine = VideoEngine()
        video_path = f"{title.replace(' ', '_')}_{timestamp}.mp4"
        video_engine.compose_video(scenes_data, video_path)

        # 4. Upload to YouTube
        print("--- Step 4: Uploading to YouTube ---")
        uploader = YouTubeUploader()
        description = f"AI generated story about {topic}.\n\n#shorts #ai #storytelling #storytype"
        uploader.upload_video(video_path, f"{title} | AI Story", description)

        print("--- Pipeline Complete! ---")

    except Exception as e:
        print(f"Error in pipeline: {e}")
    finally:
        # Clean up assets (keep video)
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

if __name__ == "__main__":
    asyncio.run(run_pipeline())
