from __future__ import annotations

from pathlib import Path

from fastapi import UploadFile

from app.config import get_settings
from app.database import SupabaseRepository
from utils.hashing import sha256_for_file
from workers.processing_queue import TranscriptionJob, processing_queue


class VideoIngestService:
    def __init__(self, repository: SupabaseRepository) -> None:
        self.repository = repository
        self.settings = get_settings()

    async def ingest_upload(self, upload: UploadFile) -> dict:
        temp_file = self.settings.videos_dir() / upload.filename

        with temp_file.open('wb') as destination:
            while chunk := await upload.read(1024 * 1024):
                destination.write(chunk)

        video_hash = sha256_for_file(temp_file)
        existing = self.repository.get_video_by_hash(video_hash)
        if existing:
            if temp_file.exists():
                temp_file.unlink(missing_ok=True)
            return {
                'video_id': existing['id'],
                'video_hash': video_hash,
                'status': 'reused_existing_video',
                'reused_transcript': True,
            }

        canonical_path = self.settings.videos_dir() / f'{video_hash}_{upload.filename}'
        temp_file.rename(canonical_path)

        created = self.repository.create_video(
            {
                'video_hash': video_hash,
                'filename': canonical_path.name,
                'duration': None,
                'transcript_text': None,
                'transcript_segments': [],
            }
        )
        processing_queue.enqueue_transcription(
            TranscriptionJob(video_id=created['id'], video_path=str(canonical_path))
        )

        return {
            'video_id': created['id'],
            'video_hash': video_hash,
            'status': 'queued_for_transcription',
            'reused_transcript': False,
        }
