# ElevenEdge MVP

ElevenEdge is a Discord + FastAPI assistant that helps you:
1. Upload a long video.
2. Transcribe it with OpenAI Whisper API.
3. Search the transcript for moments.
4. Generate MP4 clips with FFmpeg.

This version is designed to run locally with **3 processes**:
- API server
- transcription worker
- Discord bot

---

## 1) Project compatibility fixes (what changed)

To make the MVP run end-to-end reliably, this project now uses:

- **Supabase-backed job queue** using `VIDEOS.status` (`uploaded`, `processing`, `transcribed`) instead of in-memory Python queue.
- **OpenAI Whisper API** (`whisper-1`) instead of local model loading.
- **Dedicated `TRANSCRIPTS` table** for transcript text + segment timestamps.
- **Fixed clip API response shape** so `clip_id` is returned correctly.
- **Clear bot status messages** for `/upload`, `/search`, and `/clip`.

---

## 2) Database setup (Supabase SQL)

Run this SQL in your Supabase SQL editor:

```sql
create table if not exists "VIDEOS" (
  id bigint generated always as identity primary key,
  video_hash text unique not null,
  filename text not null,
  status text not null default 'uploaded' check (status in ('uploaded', 'processing', 'transcribed')),
  duration double precision,
  processing_error text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists "TRANSCRIPTS" (
  id bigint generated always as identity primary key,
  video_id bigint not null unique references "VIDEOS"(id) on delete cascade,
  transcript_text text not null,
  transcript_segments jsonb not null default '[]'::jsonb,
  language text,
  duration double precision,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists "CLIPS" (
  id bigint generated always as identity primary key,
  video_id bigint not null references "VIDEOS"(id) on delete cascade,
  start_time double precision not null,
  end_time double precision not null,
  clip_path text not null,
  created_at timestamptz not null default now()
);

create table if not exists "QUERIES" (
  id bigint generated always as identity primary key,
  video_id bigint not null references "VIDEOS"(id) on delete cascade,
  query_text text not null,
  matched_segments jsonb not null,
  created_at timestamptz not null default now()
);

create index if not exists videos_status_created_at_idx on "VIDEOS"(status, created_at);
create index if not exists transcripts_video_id_idx on "TRANSCRIPTS"(video_id);
create index if not exists clips_video_id_idx on "CLIPS"(video_id);
create index if not exists queries_video_id_idx on "QUERIES"(video_id);
```

---

## 3) Environment configuration

Create a `.env` file in the repository root:

```bash
SUPABASE_URL=https://YOUR_PROJECT_ID.supabase.co
SUPABASE_KEY=YOUR_SUPABASE_SERVICE_ROLE_KEY
OPENAI_API_KEY=sk-...
DISCORD_BOT_TOKEN=YOUR_DISCORD_BOT_TOKEN
ELEVENEDGE_API_BASE_URL=http://localhost:8000
```

Where to get these values:
- `SUPABASE_URL`: Supabase project settings → API URL.
- `SUPABASE_KEY`: Supabase project settings → API keys (service role key recommended for server-side).
- `OPENAI_API_KEY`: OpenAI dashboard → API keys.
- `DISCORD_BOT_TOKEN`: Discord Developer Portal → your bot → token.

---

## 4) Local setup

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r elevenedge/requirements.txt
```

Install FFmpeg (required):
- Ubuntu/Debian: `sudo apt-get install ffmpeg`
- macOS (Homebrew): `brew install ffmpeg`

---

## 5) Run the system (3 terminals)

In each terminal, run:

```bash
source .venv/bin/activate
export PYTHONPATH=elevenedge
```

### Terminal A: API server
```bash
python elevenedge/app/main.py
```

### Terminal B: worker
```bash
python elevenedge/workers/transcription_worker.py
```

### Terminal C: Discord bot
```bash
python elevenedge/bot/discord_bot.py
```

---

## 6) How the queue works

- `/upload` creates a `VIDEOS` row with `status='uploaded'`.
- Worker polls Supabase for oldest uploaded video.
- Worker claims it (`status='processing'`), transcribes audio via Whisper API, writes `TRANSCRIPTS`, then marks video `transcribed`.
- If transcription fails, worker stores `processing_error` and resets status to `uploaded` for retry.

---

## 7) Discord commands

### `/upload`
Uploads a video to the backend and starts processing.

### `/search`
Searches transcript segments by keywords and returns timestamped matches.

### `/clip`
Creates a clip with pre/post roll and uploads the resulting MP4 file in Discord.

---

## 8) API examples

### Upload video
```bash
curl -X POST http://localhost:8000/videos/upload \
  -F "video=@/path/to/video.mp4"
```

### Search transcript
```bash
curl -X POST http://localhost:8000/search/videos/1 \
  -H "Content-Type: application/json" \
  -d '{"query":"lag is insane","limit":5}'
```

### Generate clip
```bash
curl -X POST http://localhost:8000/clips/videos/1 \
  -H "Content-Type: application/json" \
  -d '{"start":132.4,"end":136.7,"pre_roll_seconds":5,"post_roll_seconds":5}'
```

---

## 9) Testing the full workflow in Discord

1. Start API, worker, and bot.
2. In your Discord server, run `/upload` with a test video.
3. Wait until the worker logs a success message.
4. Run `/search video_id:<id> query:<phrase>`.
5. Pick a returned timestamp and run `/clip video_id:<id> start:<seconds> end:<seconds>`.
6. Confirm the bot uploads a playable MP4 clip.

If `/search` returns no results, wait a little longer or try a simpler query.
