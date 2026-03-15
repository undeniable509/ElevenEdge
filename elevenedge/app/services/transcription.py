from __future__ import annotations

from pathlib import Path

from openai import OpenAI

from app.config import get_settings
from app.database import SupabaseRepository
from utils.ffmpeg_utils import extract_audio


class TranscriptionService:
    def __init__(self, repository: SupabaseRepository) -> None:
        self.settings = get_settings()
        self.repository = repository
        self.client = OpenAI(api_key=self.settings.openai_api_key)

    def transcribe_video(self, video_id: int, video_path: Path) -> dict:
        audio_path = self.settings.audio_cache_dir() / f'{video_id}.wav'
        extract_audio(video_path, audio_path)

        with audio_path.open('rb') as audio_file:
            transcript = self.client.audio.transcriptions.create(
                model=self.settings.whisper_model,
                file=audio_file,
                response_format='verbose_json',
                timestamp_granularities=['segment'],
            )

        raw_segments = getattr(transcript, 'segments', None) or []
        segments = [
            {
                'start': float(segment.start),
                'end': float(segment.end),
                'text': str(segment.text).strip(),
            }
            for segment in raw_segments
        ]
        transcript_text = str(getattr(transcript, 'text', '')).strip()
        duration = float(segments[-1]['end']) if segments else 0.0

        saved = self.repository.upsert_transcript(
            {
                'video_id': video_id,
                'transcript_text': transcript_text,
                'transcript_segments': segments,
                'language': getattr(transcript, 'language', None),
                'duration': duration,
            }
        )
        self.repository.mark_video_transcribed(video_id=video_id, duration=duration)
        return saved
