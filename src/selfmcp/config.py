from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    aws_region: str = "us-east-1"
    s3_bucket_name: str

    bedrock_agent_id: str
    bedrock_agent_alias_id: str


settings = Settings()
