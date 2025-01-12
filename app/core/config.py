from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    LOG_FILE_PATH: str = "logs/app.log"
    LOG_LEVEL: str = "INFO"
    LOG_ROTATION: str = "100 MB"
    LOG_RETENTION: str = "5 days"
    
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str
    MYSQL_DATABASE: str

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
