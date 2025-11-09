from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://admin:secret@localhost:5432/battlearena"
    LOG_LEVEL: str = "info"
    
    class Config:
        env_file = ".env"

settings = Settings()
