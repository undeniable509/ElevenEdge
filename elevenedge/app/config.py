from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    app_name: str = 'ElevenEdge'
    app_env: str = 'dev'
    app_host: str = '0.0.0.0'
    app_port: int = 8000

    supabase_url: str = Field(..., alias='SUPABASE_URL')
    supabase_key: str = Field(..., alias='SUPABASE_KEY')
    openai_api_key: str = Field(..., alias='OPENAI_API_KEY')

    whisper_model: str = 'whisper-1'
    storage_root: Path = Path('elevenedge/storage')
    videos_dir_name: str = 'videos'
    clips_dir_name: str = 'clips'
    audio_cache_dir_name: str = 'audio'

    discord_bot_token: str | None = Field(default=None, alias='DISCORD_BOT_TOKEN')
    worker_poll_interval_seconds: float = 2.0

    def videos_dir(self) -> Path:
        return self.storage_root / self.videos_dir_name

    def clips_dir(self) -> Path:
        return self.storage_root / self.clips_dir_name

    def audio_cache_dir(self) -> Path:
        return self.storage_root / self.audio_cache_dir_name


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    settings.videos_dir().mkdir(parents=True, exist_ok=True)
    settings.clips_dir().mkdir(parents=True, exist_ok=True)
    settings.audio_cache_dir().mkdir(parents=True, exist_ok=True)
    return settings
