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
    print("  MathMagic AI — NCERT Series Bot")
    print("=" * 60)

    math_engine = MathEngine()
    render_engine = RenderEngine()
    audio_engine = AudioEngine()
    video_engine = VideoEngine()
    uploader = YouTubeUploader()

    # 1. Get lesson from NCERT curriculum (sequential)
    day = math_engine.get_current_day()
    lesson = math_engine.generate_lesson(day)
    print(f"\n✅ Lesson ready: Class {lesson['class_num']} | {lesson['topic']}")

    # 2. Render animated frames (18 frames @ 200ms = smooth animation)
    print("\nRendering animated frames...")
    frame_paths = await render_engine.render_lesson(lesson)

    # 3. Generate Hindi audio (3 parts: intro + main + outro)
    print("\nGenerating Hindi audio...")
    os.makedirs("temp_audio", exist_ok=True)

    audios = [
        ("intro", lesson["intro_audio"]),
        ("main",  lesson["main_audio"]),
        ("outro", lesson["outro_audio"])
    ]

    audio_paths = []
    for name, text in audios:
        path = f"temp_audio/{name}.mp3"
        ok = await audio_engine.generate_audio(text, path)
        if ok and os.path.exists(path):
            audio_paths.append(path)
            print(f"  Audio {name}: OK")
        else:
            print(f"  Audio {name}: FAILED")

    if not audio_paths:
        print("ERROR: No audio generated.")
        sys.exit(1)

    # 4. Build scenes — distribute animation frames across audio segments
    # frames_per_audio: spread all 18 frames across 3 audio parts
    frames_per_part = max(1, len(frame_paths) // len(audio_paths))
    scenes_data = []

    for i, audio_path in enumerate(audio_paths):
        start = i * frames_per_part
        end = start + frames_per_part if i < len(audio_paths) - 1 else len(frame_paths)
        part_frames = frame_paths[start:end]
        # Use last frame of each part as the static image for that scene
        chosen_frame = part_frames[-1] if part_frames else frame_paths[-1]
        scenes_data.append({
            "image_path": chosen_frame,
            "audio_path": audio_path,
            "narration": audios[i][1]
        })

    # 5. Compose video
    print("\nComposing video...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe = lesson['topic'].replace(' ', '_').replace('/', '-')[:30]
    out_file = f"math_C{lesson['class_num']}_L{day}_{safe}_{timestamp}.mp4"
    video_path = video_engine.compose_video(scenes_data, out_file, apply_overlay=False)
    print(f"Video: {video_path}")

    # 6. Upload
    print("\nUploading to YouTube...")
    try:
        title = (
            f"Class {lesson['class_num']} Math: {lesson['topic']} | "
            f"Lesson {day} | Hindi | #Shorts"
        )
        desc = (
            f"📚 MathMagic NCERT Series — Lesson {day}\n"
            f"🏫 Class: {lesson['class_num']}\n"
            f"📖 Chapter {lesson['chapter_num']}: {lesson['topic']}\n\n"
            f"{lesson['next_lesson_text']}\n\n"
            "#math #ncert #class{} #hindi #shorts #education #maths".format(lesson['class_num'])
        )
        vid_id = uploader.upload_video(
            file_path=video_path, title=title, description=desc,
            tags=["math", "ncert", "hindi", "shorts", "education", f"class{lesson['class_num']}"]
        )
        print(f"\n✅ LIVE: https://youtu.be/{vid_id}")
        math_engine.increment_day()
        if os.path.exists(video_path):
            os.remove(video_path)
    except Exception as e:
        print(f"Upload error: {e}")
        print(f"Video saved at: {video_path}")


if __name__ == "__main__":
    asyncio.run(main())
