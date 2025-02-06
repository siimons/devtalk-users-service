from pydantic_settings import BaseSettings
from pydantic import ConfigDict


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

    MEMCACHED_HOST: str = "127.0.0.1"
    MEMCACHED_PORT: int = 11211
    
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    TESTING: bool = True

    model_config = ConfigDict(env_file=".env", extra="ignore")


settings = Settings()
