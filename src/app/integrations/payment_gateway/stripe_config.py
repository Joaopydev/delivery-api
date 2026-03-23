from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    stripe_secret_key: str
    stripe_publishable_key: str
    stripe_webhook_secret: str
    domain: str = "http://127.0.0.1:8000/"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()
