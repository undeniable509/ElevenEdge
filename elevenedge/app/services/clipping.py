from __future__ import annotations

from pathlib import Path

from app.config import get_settings
from app.database import SupabaseRepository
from utils.ffmpeg_utils import generate_clip


class ClippingService:
    def __init__(self, repository: SupabaseRepository) -> None:
        self.repository = repository
        self.settings = get_settings()

    def create_clip(
        self,
        video_id: int,
        start: float,
        end: float,
        pre_roll_seconds: float,
        post_roll_seconds: float,
    ) -> dict:
        video = self.repository.get_video(video_id)
        if not video:
            raise ValueError(f'Video {video_id} not found')

        adjusted_start = max(0.0, start - pre_roll_seconds)
        adjusted_end = max(adjusted_start + 0.1, end + post_roll_seconds)

        video_path = self.settings.videos_dir() / video['filename']
        output_name = f"{video_id}_{adjusted_start:.2f}_{adjusted_end:.2f}.mp4"
        output_path = self.settings.clips_dir() / output_name

        generate_clip(video_path, output_path, adjusted_start, adjusted_end)

        return self.repository.create_clip(
            {
                'video_id': video_id,
                'start_time': adjusted_start,
                'end_time': adjusted_end,
                'clip_path': str(output_path),
            }
        )
