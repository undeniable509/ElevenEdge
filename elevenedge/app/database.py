from __future__ import annotations

from typing import Any

from supabase import Client, create_client

from app.config import get_settings


class SupabaseRepository:
    def __init__(self) -> None:
        settings = get_settings()
        self.client: Client = create_client(settings.supabase_url, settings.supabase_key)

    def get_video_by_hash(self, video_hash: str) -> dict[str, Any] | None:
        response = (
            self.client.table('VIDEOS')
            .select('*')
            .eq('video_hash', video_hash)
            .limit(1)
            .execute()
        )
        if not response.data:
            return None
        return response.data[0]

    def get_video(self, video_id: int) -> dict[str, Any] | None:
        response = self.client.table('VIDEOS').select('*').eq('id', video_id).limit(1).execute()
        if not response.data:
            return None
        return response.data[0]

    def create_video(self, payload: dict[str, Any]) -> dict[str, Any]:
        response = self.client.table('VIDEOS').insert(payload).execute()
        return response.data[0]

    def update_video_transcript(
        self,
        video_id: int,
        transcript_text: str,
        transcript_segments: list[dict[str, Any]],
        duration: float,
    ) -> dict[str, Any]:
        response = (
            self.client.table('VIDEOS')
            .update(
                {
                    'transcript_text': transcript_text,
                    'transcript_segments': transcript_segments,
                    'duration': duration,
                }
            )
            .eq('id', video_id)
            .execute()
        )
        return response.data[0]

    def create_query(self, payload: dict[str, Any]) -> dict[str, Any]:
        response = self.client.table('QUERIES').insert(payload).execute()
        return response.data[0]

    def create_clip(self, payload: dict[str, Any]) -> dict[str, Any]:
        response = self.client.table('CLIPS').insert(payload).execute()
        return response.data[0]


def get_repository() -> SupabaseRepository:
    return SupabaseRepository()
