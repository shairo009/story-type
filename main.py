import os
import sys
import time
from datetime import datetime
from src.story_engine import StoryEngine
from src.image_engine import ImageEngine
from src.audio_engine import AudioEngine
from src.video_engine import VideoEngine
from src.uploader import YouTubeUploader
import asyncio

async def main():
    print("--- 1-Minute Comic Production Starting ---")
    
    # 1. Generate Story
    story_engine = StoryEngine()
    topic = "The Mystery of Time Travel"
    story_data = story_engine.generate_story(topic)
    
    if not story_data or "scenes" not in story_data:
        print("Failed to generate story.")
        sys.exit(1)

    title = story_data.get('title', 'AI Story')
    print(f"Title: {title}")
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
        
        image_engine.generate_image(scene["image_prompt"], img_path)
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
    if not processed_scenes:
        print("Error: No scenes were successfully processed.")
        sys.exit(1)

    print("--- Step 3: Composing Video ---")
    output_filename = f"comic_long_{timestamp}.mp4"
    video_path = video_engine.compose_video(processed_scenes, output_filename)
    print(f"--- Video created: {video_path} ---")

    # 5. Upload to YouTube
    print("--- Step 4: Uploading to YouTube ---")
    try:
        uploader = YouTubeUploader(
            secrets_file="client_secrets.json",
            token_file="token.json"
        )
        description = (
            f"AI-generated Hinglish comic story: {title}\n\n"
            "Made with AI — story, images, audio, and video all generated automatically.\n"
            "#shorts #ai #comic #hinglish #story"
        )
        video_id = uploader.upload_video(
            file_path=video_path,
            title=f"{title} | AI Comic #Shorts",
            description=description,
            tags=["shorts", "ai", "comic", "hinglish", "story", "animation"]
        )
        print(f"--- SUCCESS! Uploaded to YouTube: https://youtu.be/{video_id} ---")
    except Exception as e:
        print(f"YouTube upload failed: {e}")
        print("Video is saved locally at:", video_path)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
