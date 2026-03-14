from fastapi import APIRouter, Depends

from app.database import SupabaseRepository, get_repository
from app.models import SearchRequest, SearchResponse
from app.services.search import SearchService

router = APIRouter(prefix='/search', tags=['search'])


@router.post('/videos/{video_id}', response_model=SearchResponse)
def search_video(
    video_id: int,
    request: SearchRequest,
    repository: SupabaseRepository = Depends(get_repository),
) -> SearchResponse:
    service = SearchService(repository)
    matches = service.search(video_id, request.query, request.limit)
    return SearchResponse(video_id=video_id, query=request.query, matches=matches)
