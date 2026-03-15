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

    def claim_next_uploaded_video(self) -> dict[str, Any] | None:
        response = (
            self.client.table('VIDEOS')
            .select('*')
            .eq('status', 'uploaded')
            .order('created_at', desc=False)
            .limit(1)
            .execute()
        )
        if not response.data:
            return None

        candidate = response.data[0]
        updated = (
            self.client.table('VIDEOS')
            .update({'status': 'processing', 'processing_error': None})
            .eq('id', candidate['id'])
            .eq('status', 'uploaded')
            .execute()
        )
        if not updated.data:
            return None
        return updated.data[0]

    def mark_video_transcribed(self, video_id: int, duration: float) -> dict[str, Any]:
        response = (
            self.client.table('VIDEOS')
            .update({'status': 'transcribed', 'duration': duration, 'processing_error': None})
            .eq('id', video_id)
            .execute()
        )
        return response.data[0]

    def mark_video_failed(self, video_id: int, error_message: str) -> dict[str, Any]:
        response = (
            self.client.table('VIDEOS')
            .update({'status': 'uploaded', 'processing_error': error_message[:1000]})
            .eq('id', video_id)
            .execute()
        )
        return response.data[0]

    def get_transcript(self, video_id: int) -> dict[str, Any] | None:
        response = (
            self.client.table('TRANSCRIPTS')
            .select('*')
            .eq('video_id', video_id)
            .limit(1)
            .execute()
        )
        if not response.data:
            return None
        return response.data[0]

    def upsert_transcript(self, payload: dict[str, Any]) -> dict[str, Any]:
        response = self.client.table('TRANSCRIPTS').upsert(payload, on_conflict='video_id').execute()
        return response.data[0]

    def create_query(self, payload: dict[str, Any]) -> dict[str, Any]:
        response = self.client.table('QUERIES').insert(payload).execute()
        return response.data[0]

    def create_clip(self, payload: dict[str, Any]) -> dict[str, Any]:
        response = self.client.table('CLIPS').insert(payload).execute()
        return response.data[0]


def get_repository() -> SupabaseRepository:
    return SupabaseRepository()
