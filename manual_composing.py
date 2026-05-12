import os
import shutil
import asyncio
from src.video_engine import VideoEngine
from src.audio_engine import AudioEngine

# 1. Setup paths
assets_dir = "manual_assets"
os.makedirs(assets_dir, exist_ok=True)

# Sources from identified .tempmediaStorage
base_path = r"C:\Users\1001s\.gemini\antigravity\brain\3eb14454-e328-453d-9ff4-723627e39fc7\.tempmediaStorage"
sources = [
    os.path.join(base_path, "media_3eb14454-e328-453d-9ff4-723627e39fc7_1778597450214.png"),
    os.path.join(base_path, "media_3eb14454-e328-453d-9ff4-723627e39fc7_1778597527809.png"),
    os.path.join(base_path, "media_3eb14454-e328-453d-9ff4-723627e39fc7_1778597618588.png"),
    os.path.join(base_path, "media_3eb14454-e328-453d-9ff4-723627e39fc7_1778597706789.png"),
    os.path.join(base_path, "media_3eb14454-e328-453d-9ff4-723627e39fc7_1778597798319.png")
]

# Copy and rename
for i, src in enumerate(sources):
    if os.path.exists(src):
        shutil.copy(src, os.path.join(assets_dir, f"scene_{i}.png"))

# 2. Story Data
story_scenes = [
    {"narration": "Mona aur Andy purane school mein dakhil hue.", "dialogue": "Kitna darr lag raha hai!"},
    {"narration": "Achanak unhe ek asli bhoot dikha!", "dialogue": "Bhaago! Bhoot!"},
    {"narration": "Dono apni jaan bachakar bhage.", "dialogue": "Tezi se chalo!"},
    {"narration": "Ek khali classroom mein chhup gaye.", "dialogue": "Shhh... chup raho."},
    {"narration": "Lekin bhoot toh dosti karna chahta tha!", "dialogue": "Chalo dost bante hain!"}
]

# 3. Generate Audio & Prepare for Composing
audio_engine = AudioEngine()
scenes_to_compose = []

async def prepare_scenes():
    for i, scene in enumerate(story_scenes):
        img_path = os.path.join(assets_dir, f"scene_{i}.png")
        audio_path = os.path.join(assets_dir, f"scene_{i}.mp3")
        
        if not os.path.exists(img_path): continue
        
        # Generate audio (Properly awaited)
        await audio_engine.generate_audio(scene["narration"], audio_path)
        
        # Add to list for compose_video
        scenes_to_compose.append({
            'image_path': img_path,
            'audio_path': audio_path,
            'narration': scene['dialogue']
        })

# Run audio generation
asyncio.run(prepare_scenes())

# Final Video
video_engine = VideoEngine()
output_video = "haunted_school_final.mp4"
if scenes_to_compose:
    video_engine.compose_video(scenes_to_compose, output_video)
    print(f"VIDEO COMPLETED: {output_video}")
else:
    print("Error: No scenes to compose!")
