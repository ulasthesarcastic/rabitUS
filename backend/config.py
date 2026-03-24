from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./rabitus.db"
    jwt_secret: str = "change-me-in-production-min-32-chars!!"
    jwt_expiration_hours: int = 24
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    model_config = {"env_prefix": "RABITUS_"}


settings = Settings()
