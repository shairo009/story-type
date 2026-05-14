import os
import sys
import asyncio
from datetime import datetime
from src.math_engine import MathEngine
from src.render_engine import RenderEngine
from src.audio_engine import AudioEngine
from src.video_engine import VideoEngine
from src.uploader import YouTubeUploader

async def main():
    print("=" * 60)
    print("MathMagic AI - Multi-Slide Teaching Video")
    print("=" * 60)

    math_engine = MathEngine()
    render_engine = RenderEngine()
    audio_engine = AudioEngine()
    video_engine = VideoEngine()
    uploader = YouTubeUploader()

    # 1. Get current day & generate lesson
    day = math_engine.get_current_day()
    lesson = math_engine.generate_lesson(day)
    lesson["day"] = day
    print(f"\nLesson {day}: [{lesson['level']}] {lesson['topic']}")

    # 2. Render all 5 slides
    print("\nRendering 5 slides...")
    frame_paths = await render_engine.render_lesson(lesson)
    print(f"Frames ready: {len(frame_paths)}")

    # 3. Generate audio for each slide
    print("\nGenerating Hindi audio...")
    os.makedirs("temp_audio", exist_ok=True)

    slide_audios = [
        lesson["intro_text"],
        lesson["concept_audio"],
        lesson["graph_audio"],
        lesson["example_audio"],
        lesson["summary_audio"]
    ]

    scenes_data = []
    for i, (frame, narration) in enumerate(zip(frame_paths, slide_audios)):
        audio_path = f"temp_audio/slide_{i}.mp3"
        success = await audio_engine.generate_audio(narration, audio_path)
        if success and os.path.exists(audio_path):
            scenes_data.append({
                "image_path": frame,
                "audio_path": audio_path,
                "narration": narration
            })
        else:
            print(f"  Audio failed for slide {i}, skipping.")

    if not scenes_data:
        print("ERROR: No scenes generated.")
        sys.exit(1)

    print(f"\n{len(scenes_data)}/5 slides have audio")

    # 4. Compose final video
    print("\nComposing video...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    level_safe = lesson['level'].replace(' ', '_').replace('/', '-')
    output_filename = f"math_L{day}_{level_safe}_{timestamp}.mp4"
    video_path = video_engine.compose_video(scenes_data, output_filename, apply_overlay=False)
    print(f"Video ready: {video_path}")

    # 5. Upload to YouTube
    print("\nUploading to YouTube...")
    try:
        title = f"Lesson {day}: {lesson['topic']} | {lesson['level']} | MathMagic #Shorts"
        description = (
            f"📚 MathMagic - Lesson {day}\n"
            f"🎯 Level: {lesson['level']}\n"
            f"📖 Topic: {lesson['topic']}\n\n"
            f"Aaj humne seekha: {lesson['topic']}\n"
            f"Agli video mein: {lesson['next_topic']}\n\n"
            "#math #education #hindi #shorts #learning #maths #mathmagic"
        )
        video_id = uploader.upload_video(
            file_path=video_path,
            title=title,
            description=description,
            tags=["math", "education", "hindi", "shorts", "learning", lesson["topic"].lower()]
        )
        print(f"\n✅ UPLOADED: https://youtu.be/{video_id}")

        math_engine.increment_day()

        if os.path.exists(video_path):
            os.remove(video_path)
            print("Local video file cleaned up.")

    except Exception as e:
        print(f"YouTube upload failed: {e}")
        print(f"Video saved locally: {video_path}")

if __name__ == "__main__":
    asyncio.run(main())
