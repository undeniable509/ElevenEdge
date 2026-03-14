from __future__ import annotations

from dataclasses import dataclass
from queue import Empty, Queue


@dataclass
class TranscriptionJob:
    video_id: int
    video_path: str


class ProcessingQueue:
    def __init__(self) -> None:
        self._transcription_queue: Queue[TranscriptionJob] = Queue()

    def enqueue_transcription(self, job: TranscriptionJob) -> None:
        self._transcription_queue.put(job)

    def dequeue_transcription(self, timeout_seconds: float = 0.1) -> TranscriptionJob | None:
        try:
            return self._transcription_queue.get(timeout=timeout_seconds)
        except Empty:
            return None


processing_queue = ProcessingQueue()
