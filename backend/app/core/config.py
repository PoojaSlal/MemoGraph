from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "MemoGraph"
    app_version: str = "0.1.0"
    environment: str = "development"

    postgres_host: str
    postgres_port: int
    postgres_db: str
    postgres_user: str
    postgres_password: str

    qdrant_host: str
    qdrant_port: int

    memgraph_host: str
    memgraph_port: int

    redis_host: str
    redis_port: int
    redis_db: int = 0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()