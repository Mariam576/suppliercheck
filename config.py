from functools import lru_cache
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config=SettingsConfigDict(env_file=".env", extra="ignore")
    APP_NAME : str= "SupplierCheck"
    COMPANIES_HOUSE_API_KEY : SecretStr
@lru_cache
def get_settings()-> Settings: 
    return Settings()