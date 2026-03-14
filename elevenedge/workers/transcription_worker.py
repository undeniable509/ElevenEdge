import time
from pathlib import Path

from app.config import get_settings
from app.database import get_repository
from app.services.transcription import TranscriptionService
from workers.processing_queue import processing_queue


def run_worker() -> None:
    settings = get_settings()
    repository = get_repository()
    service = TranscriptionService(repository)

    while True:
        job = processing_queue.dequeue_transcription(timeout_seconds=settings.worker_poll_interval_seconds)
        if not job:
            continue
        service.transcribe_video(job.video_id, Path(job.video_path))
        time.sleep(0.05)


if __name__ == '__main__':
    run_worker()
