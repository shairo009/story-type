import os
import time
from datetime import datetime
from src.story_engine import StoryEngine
from src.image_engine import ImageEngine
from src.audio_engine import AudioEngine
from src.video_engine import VideoEngine
import asyncio

async def main():
    print("--- 1-Minute Comic Production Starting ---")
    
    # 1. Generate Story (15 scenes for ~60 seconds)
    story_engine = StoryEngine()
    topic = "The Mystery of Time Travel" # default topic
    story_data = story_engine.generate_story(topic)
    
    if not story_data or "scenes" not in story_data:
        print("Failed to generate story.")
        return

    print(f"Title: {story_data.get('title', 'AI Story')}")
    scenes = story_data["scenes"]
    print(f"Scenes to process: {len(scenes)}")

    # 2. Setup Engines
    image_engine = ImageEngine()
    audio_engine = AudioEngine()
    video_engine = VideoEngine()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_dir = f"temp_{timestamp}"
    os.makedirs(temp_dir, exist_ok=True)

    processed_scenes = []

    # 3. Process each scene
    for i, scene in enumerate(scenes):
        print(f"Processing Scene {i+1}/{len(scenes)}...")
        
        img_path = os.path.join(temp_dir, f"scene_{i}.png")
        audio_path = os.path.join(temp_dir, f"scene_{i}.mp3")
        
        # Image Generation
        image_engine.generate_image(scene["image_prompt"], img_path)
        
        # Audio Generation
        await audio_engine.generate_audio(scene["narration"], audio_path)
        
        if os.path.exists(img_path) and os.path.exists(audio_path):
            processed_scenes.append({
                'image_path': img_path,
                'audio_path': audio_path,
                'narration': scene.get('dialogue', '')
            })
        else:
            print(f"Warning: Missing assets for scene {i+1}. Skipping.")

    # 4. Compose Video
    if processed_scenes:
        print("--- Step 3: Composing 1-Minute Video ---")
        output_filename = f"comic_long_{timestamp}.mp4"
        video_engine.compose_video(processed_scenes, output_filename)
        print(f"--- SUCCESS! Video created: outputs/{output_filename} ---")
    else:
        print("Error: No scenes were successfully processed.")

if __name__ == "__main__":
    asyncio.run(main())
