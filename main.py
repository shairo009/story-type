import os
import sys
import json
import asyncio
from datetime import datetime
from src.math_engine import MathEngine
from src.render_engine import RenderEngine
from src.audio_engine import AudioEngine
from src.video_engine import VideoEngine
from src.uploader import YouTubeUploader

async def main():
    print("--- MathMagic AI: Starting Daily Production ---")

    # 1. Setup Engines
    math_engine = MathEngine()
    render_engine = RenderEngine()
    audio_engine = AudioEngine()
    video_engine = VideoEngine()
    uploader = YouTubeUploader()

    # 2. Generate Lesson Content
    day = math_engine.get_current_day()
    lesson_data = math_engine.generate_lesson(day)
    lesson_data["day"] = day
    
    print(f"Lesson: {lesson_data['title']}")

    # 3. Render Visual Frames (HTML to PNG)
    print("Rendering 3D Visuals...")
    frame_paths = await render_engine.render_lesson(lesson_data)

    # 4. Generate Audio (Hindi TTS)
    print("Generating Hindi Audio...")
    os.makedirs("temp_audio", exist_ok=True)
    
    # Advanced logic: 1 single long explanation audio
    audio_path = "temp_audio/explanation.mp3"
    await audio_engine.generate_audio(lesson_data["explanation"], audio_path)
    
    scenes_data = [{
        "image_path": frame_paths[0],
        "audio_path": audio_path,
        "narration": lesson_data["explanation"]
    }]

    # 5. Compose Video
    print("Composing Final Video...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"math_{lesson_data['level'].replace(' ', '_')}_{timestamp}.mp4"
    video_path = video_engine.compose_video(scenes_data, output_filename, apply_overlay=False)

    # 6. Upload to YouTube
    print(f"Uploading Video: {video_path}")
    try:
        description = (
            f"Daily Math Magic - Day {day}: {lesson_data['title']}\n\n"
            f"Learn Math the fun way with AI and 3D visuals!\n"
            f"Topic: {lesson_data['explanation']}\n\n"
            "#math #learning #hindi #shorts #education #ai"
        )
        video_id = uploader.upload_video(
            file_path=video_path,
            title=f"Math Magic Day {day}: {lesson_data['title']} | #Shorts",
            description=description,
            tags=["math", "education", "hindi", "shorts", "learning"]
        )
        print(f"SUCCESS! YouTube URL: https://youtu.be/{video_id}")
        
        # Increment day count for tomorrow
        math_engine.increment_day()
        
        # Cleanup
        if os.path.exists(video_path):
            os.remove(video_path)

    except Exception as e:
        print(f"YouTube upload failed: {e}")
        print("Video saved locally for manual upload.")

if __name__ == "__main__":
    asyncio.run(main())
