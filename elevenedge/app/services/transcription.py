from __future__ import annotations

from pathlib import Path

import whisper

from app.config import get_settings
from app.database import SupabaseRepository
from utils.ffmpeg_utils import extract_audio


class TranscriptionService:
    def __init__(self, repository: SupabaseRepository) -> None:
        self.settings = get_settings()
        self.repository = repository
        self.model = whisper.load_model(self.settings.whisper_model)

    def transcribe_video(self, video_id: int, video_path: Path) -> dict:
        audio_path = self.settings.audio_cache_dir() / f'{video_id}.wav'
        extract_audio(video_path, audio_path)

        result = self.model.transcribe(str(audio_path), fp16=False)
        segments = [
            {
                'start': float(segment['start']),
                'end': float(segment['end']),
                'text': str(segment['text']).strip(),
            }
            for segment in result.get('segments', [])
        ]
        transcript_text = result.get('text', '').strip()
        duration = float(segments[-1]['end']) if segments else 0.0

        return self.repository.update_video_transcript(video_id, transcript_text, segments, duration)
