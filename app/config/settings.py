from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

Timeframe = Literal["1m", "5m", "15m", "1h", "4h", "30m"]


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "CETHA-BETA"
    log_level: str = "INFO"

    db_user: str = "postgres"
    db_password: str = "postgres"
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "Cap_DB"
    db_schema: str = "CETHA_BETA"

    capital_api_key: str = Field(default="", alias="CAPITAL_API_KEY")
    capital_identifier: str = Field(default="", alias="CAPITAL_IDENTIFIER")
    capital_password: str = Field(default="", alias="CAPITAL_PASSWORD")
    capital_base_url: str = "https://api-capital.backend-capital.com/api/v1"

    instrument: str = "ETHUSD"
    default_timeframes: list[Timeframe] = ["1m", "5m", "15m", "1h", "4h"]
    include_optional_30m: bool = False

    backfill_points_per_timeframe: int = 1000

    @property
    def db_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.db_user}:{self.db_password}@"
            f"{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @property
    def active_timeframes(self) -> list[Timeframe]:
        if self.include_optional_30m and "30m" not in self.default_timeframes:
            return [*self.default_timeframes, "30m"]
        return self.default_timeframes


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
