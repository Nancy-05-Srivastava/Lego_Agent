from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Azure OpenAI
    azure_openai_api_key: str
    azure_openai_endpoint: str
    azure_openai_deployment: str = "text-embedding-ada-002"
    azure_openai_api_version: str = "2024-02-01"

    # GitHub
    github_token: str = ""

    # Agent settings
    top_k: int = 5
    min_similarity_threshold: float = 0.0


settings = Settings()
