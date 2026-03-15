from fastapi import APIRouter, Depends, HTTPException

from app.database import SupabaseRepository, get_repository
from app.models import ClipRequest, ClipResponse
from app.services.clipping import ClippingService

router = APIRouter(prefix='/clips', tags=['clips'])


@router.post('/videos/{video_id}', response_model=ClipResponse)
def create_clip(
    video_id: int,
    request: ClipRequest,
    repository: SupabaseRepository = Depends(get_repository),
) -> ClipResponse:
    service = ClippingService(repository)
    try:
        clip = service.create_clip(
            video_id=video_id,
            start=request.start,
            end=request.end,
            pre_roll_seconds=request.pre_roll_seconds,
            post_roll_seconds=request.post_roll_seconds,
        )
    except ValueError as error:
        detail = str(error)
        status_code = 404 if 'not found' in detail.lower() else 400
        raise HTTPException(status_code=status_code, detail=detail) from error

    return ClipResponse(**clip)
