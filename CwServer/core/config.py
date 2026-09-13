from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "CatWareHouse"
    DEBUG: bool = False
    DATABASE_URL: str = "sqlite+aiosqlite:///./catwarehouse.db"
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:5175"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
