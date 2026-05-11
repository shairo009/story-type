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

load_dotenv()

TOPICS = [
    "Mona and Andy find a time machine", "Mona and Andy explore a haunted school", 
    "Mona and Andy get lost in a dinosaur forest", "Mona and Andy discover a secret alien base",
    "Mona and Andy try to bake a giant cake", "Mona and Andy find a magic portal in the attic"
]

async def run_dry_run():
    # Setup directories
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_dir = f"temp_dry_{timestamp}"
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
                "image_path": img_path,
                "audio_path": aud_path,
                "narration": scene["narration"]
            })

        # 3. Compose Video
        print("--- Step 3: Composing Video (Dry Run) ---")
        video_engine = VideoEngine()
        video_path_filename = f"DRY_RUN_{title.replace(' ', '_')}_{timestamp}.mp4"
        final_video_path = video_engine.compose_video(scenes_data, video_path_filename)

        print(f"--- Dry Run Complete! Video saved at: {final_video_path} ---")

    except Exception as e:
        print(f"Error in dry run: {e}")
    finally:
        # Clean up assets (keep video)
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

if __name__ == "__main__":
    asyncio.run(run_dry_run())
