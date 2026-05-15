# MathMagic AI — NCERT Math Series Bot

Automated YouTube Math channel that teaches **Class 1 to 10 NCERT mathematics** in Hindi, chapter by chapter, fully automatically.

## What It Does

- 📚 Reads from `curriculum.json` (86 NCERT chapters, Class 1-10)
- 🤖 AI generates lesson content in Hindi (Hinglish)
- 🎨 Renders **animated HTML slides** using Playwright (typewriter equations, step-by-step reveals)
- 🎙️ Generates Hindi audio (Edge-TTS / gTTS)
- 🎬 Composes full teaching video
- 📺 Uploads to YouTube automatically

## Curriculum Coverage

| Class | Chapters |
|-------|----------|
| 1 | 5 chapters |
| 2 | 5 chapters |
| 3 | 5 chapters |
| 4 | 5 chapters |
| 5 | 5 chapters |
| 6 | 13 chapters |
| 7 | 11 chapters |
| 8 | 14 chapters |
| 9 | 13 chapters |
| 10 | 14 chapters |
| **Total** | **86 lessons** |

## Files

```
main.py              — Entry point
curriculum.json      — NCERT Class 1-10 all chapters
src/
  math_engine.py     — Reads curriculum, generates AI lesson
  render_engine.py   — HTML → Animated frames (Playwright)
  audio_engine.py    — Hindi TTS (ElevenLabs → Edge-TTS → gTTS)
  video_engine.py    — Composes video (MoviePy)
  uploader.py        — YouTube upload
templates/
  animated_lesson.html — Animated teaching slide template
.github/workflows/
  daily_upload.yml   — Runs every 6 hours (4 videos/day)
```

## Setup

1. Clone this repo
2. Add secrets in GitHub Settings → Secrets:
   - `OPENCODE_API_KEY`
   - `ELEVENLABS_API_KEY`
   - `TOKEN_JSON`
   - `CLIENT_SECRETS_JSON`
3. Run workflow manually or wait for schedule

## Local Run

```bash
pip install -r requirements.txt
playwright install chromium
python main.py
```
