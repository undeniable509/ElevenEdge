# ElevenEdge MVP

ElevenEdge is an AI-powered clipping backend + Discord bot for finding moments in long videos and instantly generating clips.

## Architecture highlights

- **Human-in-the-loop**: user selects search results and explicitly requests clip creation.
- **No redundant processing**: SHA256 video hash prevents duplicate transcription.
- **Modular services**: ingest, transcription, search, clipping split into separate modules.
- **Worker queue ready for scale**: in-memory queue now, can be swapped with Redis/SQS later.

## Project layout

```text
elevenedge/
  app/
    main.py
    config.py
    database.py
    models.py
    services/
      video_ingest.py
      transcription.py
      search.py
      clipping.py
    api/
      routes_video.py
      routes_search.py
      routes_clip.py
  bot/
    discord_bot.py
  workers/
    processing_queue.py
    transcription_worker.py
  utils/
    hashing.py
    ffmpeg_utils.py
  storage/
    videos/
    clips/
  requirements.txt
  README.md
```

## Environment variables

Create `.env` in repo root:

```bash
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-service-role-or-anon-key
DISCORD_TOKEN=your-discord-bot-token
ELEVENEDGE_API_BASE_URL=http://localhost:8000
```

## Supabase schema

Run this in Supabase SQL editor:

```sql
create table if not exists "VIDEOS" (
  id bigint generated always as identity primary key,
  video_hash text unique not null,
  filename text not null,
  duration double precision,
  transcript_text text,
  transcript_segments jsonb default '[]'::jsonb,
  created_at timestamptz default now()
);

create table if not exists "CLIPS" (
  id bigint generated always as identity primary key,
  video_id bigint not null references "VIDEOS"(id) on delete cascade,
  start_time double precision not null,
  end_time double precision not null,
  clip_path text not null,
  created_at timestamptz default now()
);

create table if not exists "QUERIES" (
  id bigint generated always as identity primary key,
  video_id bigint not null references "VIDEOS"(id) on delete cascade,
  query_text text not null,
  matched_segments jsonb not null,
  created_at timestamptz default now()
);
```

## Setup

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r elevenedge/requirements.txt
```

Make sure FFmpeg is installed and available on PATH.

## Run API and worker

```bash
export PYTHONPATH=elevenedge
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
python -m workers.transcription_worker
```

## Run Discord bot

```bash
export PYTHONPATH=elevenedge
python -m bot.discord_bot
```

## Example API requests

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

## Notes for MVP production readiness

- Add authentication/authorization before external release.
- Move queue from memory to durable broker (Redis/SQS/Celery/RQ).
- Persist clips/videos to Supabase Storage or S3 for distributed deployment.
- Add retries + structured logging + observability for worker jobs.
