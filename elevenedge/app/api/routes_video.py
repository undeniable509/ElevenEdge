from fastapi import APIRouter, Depends, File, UploadFile

from app.database import SupabaseRepository, get_repository
from app.models import UploadResponse
from app.services.video_ingest import VideoIngestService

router = APIRouter(prefix='/videos', tags=['videos'])


@router.post('/upload', response_model=UploadResponse)
async def upload_video(
    video: UploadFile = File(...),
    repository: SupabaseRepository = Depends(get_repository),
) -> UploadResponse:
    service = VideoIngestService(repository)
    payload = await service.ingest_upload(video)
    return UploadResponse(**payload)
