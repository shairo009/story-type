import os
import shutil
import asyncio
from src.video_engine import VideoEngine
from src.audio_engine import AudioEngine

# 1. Setup paths
assets_dir = "manual_assets_long"
os.makedirs(assets_dir, exist_ok=True)

# Latest screenshots from DeepAI/Browser subagent
base_path = r"C:\Users\1001s\.gemini\antigravity\brain\3eb14454-e328-453d-9ff4-723627e39fc7\.tempmediaStorage"
sources = [
    os.path.join(base_path, "media_3eb14454-e328-453d-9ff4-723627e39fc7_1778599544907.png"), # Scene 0
    os.path.join(base_path, "media_3eb14454-e328-453d-9ff4-723627e39fc7_1778599611381.png"), # Scene 1
    os.path.join(base_path, "media_3eb14454-e328-453d-9ff4-723627e39fc7_1778599646924.png"), # Scene 2
    os.path.join(base_path, "media_3eb14454-e328-453d-9ff4-723627e39fc7_1778599681944.png"), # Scene 3
    os.path.join(base_path, "media_3eb14454-e328-453d-9ff4-723627e39fc7_1778599718471.png"), # Scene 4
    os.path.join(base_path, "media_3eb14454-e328-453d-9ff4-723627e39fc7_1778599757342.png"), # Scene 5
    os.path.join(base_path, "media_3eb14454-e328-453d-9ff4-723627e39fc7_1778599791484.png"), # Scene 6
    os.path.join(base_path, "media_3eb14454-e328-453d-9ff4-723627e39fc7_1778599826437.png")  # Scene 7
]

# Copy and rename
for i, src in enumerate(sources):
    if os.path.exists(src):
        shutil.copy(src, os.path.join(assets_dir, f"scene_{i}.png"))

# 2. Long Story Data (for 1-minute feel)
story_scenes = [
    {"narration": "Mona aur Andy ne ek purani futuristic laboratory mein ek ajeeb machine dhoondh nikali. Ye shayad ek time machine thi.", "dialogue": "Kya hum ise chala sakte hain?"},
    {"narration": "Achanak, Andy ne bina soche samjhe ek bada laal button daba diya. Machine gungunane lagi.", "dialogue": "Nahi! Ruko!"},
    {"narration": "Dono ek neele portal ke andar kheenche chale gaye. Roshni itni tez thi ki unhe kuch dikhayi nahi de raha tha.", "dialogue": "Aaah! Bachao!"},
    {"narration": "Jab portal khula, wo ek ghane jungle mein the jahan bade-bade dinosaurs ghoom rahe the.", "dialogue": "Hum kahan aa gaye?"},
    {"narration": "Tabhi ek bada T-Rex unke peeche pad gaya! Dono apni jaan bachakar tezi se bhage.", "dialogue": "Bhaago! Jaldi!"},
    {"narration": "Unhe ek purani gufa mili jahan deewaron par ajeeb chitra bane hue the. Shayad ye portal wapas jane ka rasta tha.", "dialogue": "Dekho, ye portal hai!"},
    {"narration": "Portal wapas khul gaya aur dono ne ek baar fir roshni ke andar chhalang laga di.", "dialogue": "Wapas chalo!"},
    {"narration": "Dono wapas apni lab mein the. Wo safe the, lekin unhe yakeen nahi ho raha tha ki kya hua.", "dialogue": "Ab kabhi time travel nahi!"}
]

# 3. Async Audio & Video Generation
async def compose_long_video():
    audio_engine = AudioEngine()
    video_engine = VideoEngine()
    scenes_to_compose = []

    for i, scene in enumerate(story_scenes):
        img_path = os.path.join(assets_dir, f"scene_{i}.png")
        audio_path = os.path.join(assets_dir, f"scene_{i}.mp3")
        processed_img_path = os.path.join(assets_dir, f"processed_{i}.png")
        
        if not os.path.exists(img_path): continue
        
        # Longer narration audio
        await audio_engine.generate_audio(scene["narration"], audio_path)
        
        # Text overlay
        video_engine.add_text_to_image(img_path, scene["dialogue"], processed_img_path)
        
        scenes_to_compose.append({
            'image_path': processed_img_path,
            'audio_path': audio_path,
            'narration': scene['dialogue']
        })

    if scenes_to_compose:
        output_video = "time_travel_mystery_1min.mp4"
        video_engine.compose_video(scenes_to_compose, output_video)
        print(f"VIDEO COMPLETED: outputs/{output_video}")

if __name__ == "__main__":
    asyncio.run(compose_long_video())
