import time

from app.config import get_settings
from app.database import get_repository
from app.services.transcription import TranscriptionService


def run_worker() -> None:
    settings = get_settings()
    repository = get_repository()
    service = TranscriptionService(repository)

    while True:
        job = repository.claim_next_uploaded_video()
        if not job:
            time.sleep(settings.worker_poll_interval_seconds)
            continue

        video_id = int(job['id'])
        video_path = settings.videos_dir() / job['filename']

        try:
            service.transcribe_video(video_id=video_id, video_path=video_path)
            print(f'[worker] transcribed video_id={video_id}')
        except Exception as error:  # noqa: BLE001
            repository.mark_video_failed(video_id=video_id, error_message=str(error))
            print(f'[worker] failed video_id={video_id}: {error}')


if __name__ == '__main__':
    run_worker()
