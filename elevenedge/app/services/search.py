from __future__ import annotations

from typing import Any

from app.database import SupabaseRepository


class SearchService:
    def __init__(self, repository: SupabaseRepository) -> None:
        self.repository = repository

    @staticmethod
    def _format_timestamp(seconds: float) -> str:
        total = int(seconds)
        hh = total // 3600
        mm = (total % 3600) // 60
        ss = total % 60
        return f'{hh:02d}:{mm:02d}:{ss:02d}'

    def search(self, video_id: int, query: str, limit: int = 5) -> list[dict[str, Any]]:
        video = self.repository.get_video(video_id)
        if not video:
            return []

        keywords = [k.lower() for k in query.split() if k.strip()]
        segments = video.get('transcript_segments') or []

        scored: list[tuple[int, dict[str, Any]]] = []
        for segment in segments:
            text = str(segment.get('text', ''))
            normalized = text.lower()
            score = sum(1 for key in keywords if key in normalized)
            if score > 0:
                scored.append((score, segment))

        scored.sort(key=lambda item: item[0], reverse=True)

        matches = [
            {
                'timestamp': self._format_timestamp(float(segment['start'])),
                'start': float(segment['start']),
                'end': float(segment['end']),
                'text': str(segment['text']).strip(),
            }
            for _, segment in scored[:limit]
        ]

        self.repository.create_query(
            {
                'video_id': video_id,
                'query_text': query,
                'matched_segments': matches,
            }
        )

        return matches
