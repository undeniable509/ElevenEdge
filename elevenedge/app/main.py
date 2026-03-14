from fastapi import FastAPI

from app.api.routes_clip import router as clip_router
from app.api.routes_search import router as search_router
from app.api.routes_video import router as video_router
from app.config import get_settings

settings = get_settings()
app = FastAPI(title=settings.app_name)

app.include_router(video_router)
app.include_router(search_router)
app.include_router(clip_router)


@app.get('/health')
def healthcheck() -> dict[str, str]:
    return {'status': 'ok'}
