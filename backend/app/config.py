from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(BASE_DIR / ".env"), extra="ignore")

    jwt_secret: str = "lifeassist-dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7
    database_url: str = f"sqlite:///{(BASE_DIR / 'lifeassist.db').as_posix()}"
    nominatim_user_agent: str = "LifeAssist/1.0 (portfolio app; educational use)"
    nominatim_url: str = "https://nominatim.openstreetmap.org/search"
    overpass_url: str = "https://overpass-api.de/api/interpreter"
    overpass_fallback_url: str = "https://overpass.kumi.systems/api/interpreter"
    osrm_url: str = "https://router.project-osrm.org"
    cache_ttl_places_hours: int = 24 * 7
    cache_ttl_geocode_hours: int = 24 * 30
    cache_ttl_walk_hours: int = 24


settings = Settings()
