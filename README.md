# Story Type — AI Hinglish Comic YouTube Bot

Automatically generates and uploads Hinglish comic videos to YouTube every 4 hours using AI.

Each run:
1. Picks a unique topic (tracks history so no repeats)
2. Generates a 5-15 scene Hinglish story with AI
3. Generates a 4-panel comic image for each scene (Pollinations AI)
4. Generates Hindi/Hinglish voice narration (ElevenLabs)
5. Composes a video and uploads it to YouTube as a Short

---

## Required GitHub Actions Secrets

Go to your repo → **Settings → Secrets and variables → Actions → New repository secret**

| Secret Name | What it is | How to get it |
|---|---|---|
| `OPENCODE_API_KEY` | Story generation AI key | OpenCode.ai dashboard |
| `ELEVENLABS_API_KEY` | Text-to-speech API key | ElevenLabs dashboard |
| `CLIENT_SECRETS_JSON` | YouTube OAuth app credentials | Google Cloud Console (see below) |
| `TOKEN_JSON` | Your YouTube login token | Run `auth_youtube.py` locally (see below) |
| `GITHUB_PERSONAL_ACCESS_TOKEN` | GitHub token with `repo` scope | GitHub → Settings → Developer settings → Personal access tokens |

> **Currently missing:** `CLIENT_SECRETS_JSON` and `TOKEN_JSON` — YouTube upload will fail without these.

---

## One-Time YouTube Setup

### Step 1 — Create a Google Cloud Project

1. Go to [https://console.cloud.google.com](https://console.cloud.google.com)
2. Create a new project (e.g. `story-type-bot`)
3. Enable the **YouTube Data API v3**:
   - APIs & Services → Library → search "YouTube Data API v3" → Enable

### Step 2 — Create OAuth Credentials

1. APIs & Services → Credentials → **Create Credentials → OAuth client ID**
2. Application type: **Desktop app**
3. Download the JSON file → rename it to `client_secrets.json`

### Step 3 — Generate token.json (one-time login)

On your local machine (with `client_secrets.json` in the project folder):

```bash
pip install -r requirements.txt
python auth_youtube.py
```

A browser window will open. Log in with the YouTube account you want to upload to.
After login, `token.json` is created in the project folder.

### Step 4 — Add secrets to GitHub

```bash
# Copy the full content of each file as the secret value:
cat client_secrets.json   # paste as CLIENT_SECRETS_JSON
cat token.json            # paste as TOKEN_JSON
```

Go to GitHub → Settings → Secrets → Actions and add both.

---

## Running the Pipeline

### Manual trigger
GitHub → Actions → **Daily YouTube Upload** → Run workflow

### Dry run (no YouTube upload — just check video generation)
GitHub → Actions → **Dry Run Check** → Run workflow  
The output video will be available as a downloadable artifact.

### Automatic
Runs every 4 hours automatically via the `daily_upload.yml` schedule.

---

## Project Structure

```
main.py               — Full pipeline: story → images → audio → video → YouTube
dry_run.py            — Same as main.py but skips YouTube upload (for testing)
auth_youtube.py       — One-time local script to generate token.json
video_history.json    — Tracks all uploaded videos so topics never repeat
requirements.txt      — Python dependencies

src/
  story_engine.py     — AI story generation (OpenCode.ai / Pollinations fallback)
  image_engine.py     — Comic image generation (Pollinations AI)
  audio_engine.py     — Voice narration (ElevenLabs)
  video_engine.py     — Video composition (MoviePy)
  uploader.py         — YouTube upload (Google API)

.github/workflows/
  daily_upload.yml    — Scheduled upload every 4 hours
  dry_run.yml         — Manual dry run for testing
```

---

## Environment Variables (local development)

Create a `.env` file (see `.env.example`):

```env
OPENCODE_API_KEY=your_key_here
OPENCODE_BASE_URL=https://api.minimax.io/v1
ELEVENLABS_API_KEY=your_key_here
```

---

## Troubleshooting

**YouTube upload fails with auth error**
→ Your `TOKEN_JSON` secret is expired or missing. Re-run `auth_youtube.py` locally and update the secret.

**Images are blank or missing**
→ Pollinations API may be rate-limited. The pipeline retries 4 times with delays. Check the dry run logs.

**Story generation fails**
→ Check `OPENCODE_API_KEY` is valid. It falls back to Pollinations text API automatically.

**"No scenes processed" error**
→ Both image AND audio must succeed for a scene to be included. Check which API keys are set.
