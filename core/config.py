"""This python module """
from pydantic_settings import BaseSettings,SettingsConfigDict
class Settings(BaseSettings):
    database_url:str
    openai_api_key:str

   
    openai_chat_model:str
    qdrant_url: str 

    qdrant_collection:str

    redis_url:str
    model_config= SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
settings=Settings()
