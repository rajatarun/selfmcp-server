from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    adaptive_rag_base_url: str
    adaptive_rag_api_key: str

    teamview_base_url: str
    teamview_api_key: str


settings = Settings()
