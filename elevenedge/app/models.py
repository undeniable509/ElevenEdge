from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class TranscriptSegment(BaseModel):
    start: float
    end: float
    text: str


class VideoRow(BaseModel):
    id: int
    video_hash: str
    filename: str
    status: Literal['uploaded', 'processing', 'transcribed']
    duration: float | None = None
    processing_error: str | None = None
    created_at: datetime | None = None


class TranscriptRow(BaseModel):
    id: int
    video_id: int
    transcript_text: str
    transcript_segments: list[dict[str, Any]]
    language: str | None = None
    duration: float | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ClipRow(BaseModel):
    id: int
    video_id: int
    start_time: float
    end_time: float
    clip_path: str
    created_at: datetime | None = None


class QueryRow(BaseModel):
    id: int
    video_id: int
    query_text: str
    matched_segments: list[dict[str, Any]]
    created_at: datetime | None = None


class UploadResponse(BaseModel):
    video_id: int
    video_hash: str
    status: str
    reused_transcript: bool


class SearchRequest(BaseModel):
    query: str = Field(min_length=1)
    limit: int = Field(default=5, ge=1, le=20)


class SearchMatch(BaseModel):
    timestamp: str
    start: float
    end: float
    text: str


class SearchResponse(BaseModel):
    video_id: int
    query: str
    matches: list[SearchMatch]


class ClipRequest(BaseModel):
    start: float
    end: float
    pre_roll_seconds: float = Field(default=5.0, ge=0)
    post_roll_seconds: float = Field(default=5.0, ge=0)


class ClipResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    clip_id: int = Field(alias='id')
    video_id: int
    clip_path: str
    start_time: float
    end_time: float
