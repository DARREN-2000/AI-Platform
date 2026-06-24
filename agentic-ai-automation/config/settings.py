from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # LLM
    llm_provider: Literal["openai", "anthropic"] = "openai"
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    llm_model: str = "gpt-4o"

    # GitHub
    github_token: str
    github_webhook_secret: str = ""
    github_repo: str  # e.g. "owner/repo"

    # Notion
    notion_token: str = ""
    notion_database_id: str = ""

    # Scheduling
    reminder_interval_hours: int = 24
    stale_pr_threshold_days: int = 7
    stale_issue_threshold_days: int = 14

    # Persistence
    db_path: str = "automation.db"

    # Server / logging
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    log_level: str = "INFO"
    json_logs: bool = True

    @property
    def active_api_key(self) -> str:
        return self.anthropic_api_key if self.llm_provider == "anthropic" else self.openai_api_key

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
