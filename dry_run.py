import asyncio
import os
import shutil
import random
import sys
from datetime import datetime
from dotenv import load_dotenv

from src.story_engine import StoryEngine
from src.image_engine import ImageEngine
from src.audio_engine import AudioEngine
from src.video_engine import VideoEngine

load_dotenv()

TOPICS = [
    "Mona and Andy find a time machine",
    "Mona and Andy explore a haunted school",
    "Mona and Andy get lost in a dinosaur forest",
    "Mona and Andy discover a secret alien base",
    "Mona and Andy try to bake a giant cake",
    "Mona and Andy find a magic portal in the attic",
]


async def run_dry_run():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_dir = f"temp_dry_{timestamp}"
    os.makedirs(temp_dir, exist_ok=True)
    failed_images = []
    failed_audios = []

    try:
        print("=" * 50)
        print("DRY RUN STARTED")
        print("=" * 50)

        print("\n--- Step 1: Generating Story ---")
        story_engine = StoryEngine()
        topic = random.choice(TOPICS)
        print(f"Topic: {topic}")
        story_data = story_engine.generate_story(topic)
        if not story_data or "scenes" not in story_data:
            print("FAIL: Story generation failed.")
            sys.exit(1)

        title = story_data.get("title", "AI Story")
        scenes = story_data["scenes"]
        print(f"Title: {title}")
        print(f"Scenes generated: {len(scenes)}")

        print("\n--- Step 2: Generating Images & Audio ---")
        image_engine = ImageEngine()
        audio_engine = AudioEngine()

        scenes_data = []
        for i, scene in enumerate(scenes):
            print(f"\n  Scene {i+1}/{len(scenes)}")

            img_path = os.path.join(temp_dir, f"scene_{i}.png")
            aud_path = os.path.join(temp_dir, f"scene_{i}.mp3")

            img_result = image_engine.generate_image(scene["image_prompt"], img_path)
            if img_result and os.path.exists(img_path):
                size_kb = os.path.getsize(img_path) // 1024
                print(f"  Image: OK ({size_kb}KB)")
            else:
                print(f"  Image: FAILED (scene {i+1})")
                failed_images.append(i + 1)

            aud_result = await audio_engine.generate_audio(scene["narration"], aud_path)
            if aud_result and os.path.exists(aud_path):
                size_kb = os.path.getsize(aud_path) // 1024
                print(f"  Audio: OK ({size_kb}KB)")
            else:
                print(f"  Audio: FAILED (scene {i+1})")
                failed_audios.append(i + 1)

            if os.path.exists(img_path) and os.path.exists(aud_path):
                scenes_data.append({
                    "image_path": img_path,
                    "audio_path": aud_path,
                    "narration": scene.get("dialogue", scene["narration"])
                })

        print("\n--- Asset Summary ---")
        print(f"  Scenes with both assets: {len(scenes_data)}/{len(scenes)}")
        if failed_images:
            print(f"  Failed images at scenes: {failed_images}")
        if failed_audios:
            print(f"  Failed audios at scenes: {failed_audios}")

        if not scenes_data:
            print("\nFAIL: No scenes have both image and audio. Cannot compose video.")
            sys.exit(1)

        print("\n--- Step 3: Composing Video ---")
        video_engine = VideoEngine()
        out_name = f"DRY_RUN_{title.replace(' ', '_')[:40]}_{timestamp}.mp4"
        final_video_path = video_engine.compose_video(scenes_data, out_name)

        if final_video_path and os.path.exists(final_video_path):
            size_mb = os.path.getsize(final_video_path) / (1024 * 1024)
            print(f"\nSUCCESS: Video created at {final_video_path} ({size_mb:.1f}MB)")
        else:
            print("\nFAIL: Video was not created.")
            sys.exit(1)

        print("\n" + "=" * 50)
        print("DRY RUN COMPLETE")
        print(f"  Title       : {title}")
        print(f"  Total scenes: {len(scenes)}")
        print(f"  Used scenes : {len(scenes_data)}")
        if failed_images:
            print(f"  Img failures: {failed_images}")
        if failed_audios:
            print(f"  Aud failures: {failed_audios}")
        print(f"  Video       : {final_video_path}")
        print("=" * 50)

    except Exception as e:
        import traceback
        print(f"\nFATAL ERROR: {e}")
        traceback.print_exc()
        sys.exit(1)
    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            print("Temp files cleaned up.")


if __name__ == "__main__":
    asyncio.run(run_dry_run())
