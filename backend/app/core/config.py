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

    memgraph_uri: str = "bolt://localhost:7687"
    memgraph_username: str = ""
    memgraph_password: str = ""

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379

    redis_broker_url: str = "redis://localhost:6379/0"
    redis_result_url: str = "redis://localhost:6379/1"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
