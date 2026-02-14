from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):

    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Synca RAG - Edição Enterprise"
    
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "synca_admin"
    POSTGRES_PASSWORD: str = "synca_secure_pass_123"
    POSTGRES_DB: str = "synca_db"
    POSTGRES_PORT: int = 5444
    

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


    REDIS_HOST: str = "localhost"
    MINIO_ENDPOINT: str = "localhost:9000"
    
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), "../../.env"),
        env_file_encoding='utf-8',
        case_sensitive=True,
        extra='ignore'
    )

settings = Settings()