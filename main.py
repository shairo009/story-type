import os
import sys
import json
import random
from datetime import datetime
from src.story_engine import StoryEngine
from src.image_engine import ImageEngine
from src.audio_engine import AudioEngine
from src.video_engine import VideoEngine
from src.uploader import YouTubeUploader
import asyncio
import shutil

HISTORY_FILE = "video_history.json"

TOPIC_POOL = [
    "The Mystery of Time Travel",
    "A Robot Who Learns to Dream",
    "The Last Tree on Earth",
    "A Cat Who Becomes a Detective",
    "The School Where Magic is Real",
    "A Boy Who Can Talk to Clouds",
    "The Haunted Library at Night",
    "A Monkey Who Wants to Fly",
    "The Day the Sun Took a Holiday",
    "A Girl Who Found a Secret Door",
    "The Dragon Who Was Afraid of Fire",
    "A Scientist Who Discovers Dinosaurs",
    "The Ocean That Started Singing",
    "A Town Where No One Can Lie",
    "The Robot Who Steals a Bicycle",
    "A Superhero Who Hates Vegetables",
    "The Invisible Friend Who Appears",
    "A Wizard Who Forgot His Spells",
    "The Giant Who Wants to Be Small",
    "A Parrot Who Knows All Secrets",
    "The Ice Cream Shop on the Moon",
    "A Kid Who Controls the Weather",
    "The Mystery of the Missing Teacher",
    "A Dog Who Runs for Mayor",
    "The Night All the Clocks Stopped",
    "A Kingdom Under the Sea",
    "The Robot Who Falls in Love",
    "A Monkey King in Modern Delhi",
    "The Ghost Who Wants to Graduate",
    "A Rickshaw That Can Time Travel",
]


def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            try:
                return json.load(f)
            except:
                return {"videos": []}
    return {"videos": []}


def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


def pick_topic(history):
    used_topics = {v["topic"] for v in history.get("videos", [])}
    available = [t for t in TOPIC_POOL if t not in used_topics]
    if not available:
        print("All topics used. Recycling oldest topic.")
        available = TOPIC_POOL[:]
    return random.choice(available)


async def main():
    print("--- 1-Minute Comic Production Starting ---")

    history = load_history()
    topic = pick_topic(history)
    print(f"Selected topic: {topic} (from history of {len(history['videos'])} videos)")

    # 1. Generate Story
    story_engine = StoryEngine()
    story_data = story_engine.generate_story(topic)

    if not story_data or "scenes" not in story_data:
        print("Failed to generate story.")
        sys.exit(1)

    title = story_data.get("title", "AI Story")
    print(f"Title: {title}")
    scenes = story_data["scenes"]
    print(f"Scenes to process: {len(scenes)}")

    # 2. Setup Engines
    image_engine = ImageEngine()
    audio_engine = AudioEngine()
    video_engine = VideoEngine()
    uploader = YouTubeUploader()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_dir = f"temp_{timestamp}"
    os.makedirs(temp_dir, exist_ok=True)

    processed_scenes = []

    # 3. Process each scene
    for i, scene in enumerate(scenes):
        print(f"Processing Scene {i+1}/{len(scenes)}...")

        img_path = os.path.join(temp_dir, f"scene_{i}.png")
        audio_path = os.path.join(temp_dir, f"scene_{i}.mp3")

        # Generate Image & Audio
        image_engine.generate_image(scene["image_prompt"], img_path)
        await audio_engine.generate_audio(scene["narration"], audio_path)

        if os.path.exists(img_path) and os.path.exists(audio_path):
            processed_scenes.append({
                "image_path": img_path,
                "audio_path": audio_path,
                "narration": scene.get("narration", ""),
                "dialogue": scene.get("dialogue", "")
            })
        else:
            print(f"Warning: Missing assets for scene {i+1}. Skipping.")

    if not processed_scenes:
        print("Error: No scenes were successfully processed.")
        sys.exit(1)

    # 4. Compose Video
    print("--- Step 3: Composing 1-Minute Video ---")
    output_filename = f"comic_long_{timestamp}.mp4"
    video_path = video_engine.compose_video(processed_scenes, output_filename)
    print(f"--- SUCCESS! Video created: {video_path} ---")

    # 5. Upload to YouTube
    print("--- Step 4: Uploading to YouTube ---")
    video_id = None
    try:
        description = (
            f"AI-generated Hinglish comic story: {title}\n\n"
            "Made with AI story, images, audio, and video all generated automatically.\n"
            "#shorts #ai #comic #hinglish #story"
        )
        video_id = uploader.upload_video(
            file_path=video_path,
            title=f"{title} | AI Comic #Shorts",
            description=description,
            tags=["shorts", "ai", "comic", "hinglish", "story", "animation"]
        )
        print(f"--- SUCCESS! Uploaded to YouTube: https://youtu.be/{video_id} ---")
        
        # 6. Cleanup - ONLY delete the video file after successful upload
        # (Keeping source materials in temp_dir as requested)
        if os.path.exists(video_path):
            os.remove(video_path)
            print(f"Deleted local video file: {video_path}")
            
    except Exception as e:
        print(f"YouTube upload failed: {e}")
        print("Video is saved locally at:", video_path)
        # We don't delete if upload failed
    
    # Update History regardless of upload success (or only if success?)
    # Usually better if success.
    if video_id:
        history["videos"].append({
            "topic": topic,
            "title": title,
            "video_id": video_id,
            "uploaded_at": datetime.now().isoformat(),
            "youtube_url": f"https://youtu.be/{video_id}"
        })
        save_history(history)
        print(f"--- History updated. Total videos: {len(history['videos'])} ---")

if __name__ == "__main__":
    asyncio.run(main())
