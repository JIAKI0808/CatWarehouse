from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "CatWarehouse"
    DEBUG: bool = False
    DATABASE_URL: str = "sqlite+aiosqlite:///./catwarehouse.db"
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
