#config file

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    gemini_api_key: str

    auth0_domain: str
    auth0_client_id: str
    auth0_client_secret: str
    app_secret_key: str

    class Config:
        env_file = ".env"

settings = Settings()
