"""
Configuration management for the AI backbone system.
"""

import os
from typing import Dict, Any
from pathlib import Path
import json


class Config:
    """Configuration manager for the application."""

    def __init__(self, config_file: str = None):
        """
        Initialize configuration.

        Args:
            config_file: Optional path to configuration JSON file
        """
        self.config: Dict[str, Any] = {}

        if config_file and Path(config_file).exists():
            self.load_from_file(config_file)
        else:
            self.load_from_env()

    def load_from_file(self, config_file: str):
        """Load configuration from JSON file."""
        with open(config_file, "r") as f:
            self.config = json.load(f)

    def load_from_env(self):
        """Load configuration from environment variables."""
        self.config = {
            # Database
            "database": {
                "url": os.getenv("DATABASE_URL", "postgresql://localhost/ai_backbone"),
                "echo": os.getenv("DB_ECHO", "false").lower() == "true",
            },
            # LLM Configuration
            "llm": {
                "provider": os.getenv("LLM_PROVIDER", "openai"),
                "model": os.getenv("LLM_MODEL", "gpt-4"),
                "api_key": os.getenv("LLM_API_KEY", ""),
                "temperature": float(os.getenv("LLM_TEMPERATURE", "0.7")),
                "max_tokens": int(os.getenv("LLM_MAX_TOKENS", "2000")),
            },
            # Zoho CRM
            "zoho_crm": {
                "client_id": os.getenv("ZOHO_CLIENT_ID", ""),
                "client_secret": os.getenv("ZOHO_CLIENT_SECRET", ""),
                "refresh_token": os.getenv("ZOHO_REFRESH_TOKEN", ""),
            },
            # QuickBooks
            "quickbooks": {
                "client_id": os.getenv("QB_CLIENT_ID", ""),
                "client_secret": os.getenv("QB_CLIENT_SECRET", ""),
                "refresh_token": os.getenv("QB_REFRESH_TOKEN", ""),
                "realm_id": os.getenv("QB_REALM_ID", ""),
            },
            # Google Ads
            "google_ads": {
                "developer_token": os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN", ""),
                "client_id": os.getenv("GOOGLE_ADS_CLIENT_ID", ""),
                "client_secret": os.getenv("GOOGLE_ADS_CLIENT_SECRET", ""),
                "refresh_token": os.getenv("GOOGLE_ADS_REFRESH_TOKEN", ""),
                "customer_id": os.getenv("GOOGLE_ADS_CUSTOMER_ID", ""),
            },
            # Meta Ads
            "meta_ads": {
                "access_token": os.getenv("META_ACCESS_TOKEN", ""),
                "ad_account_id": os.getenv("META_AD_ACCOUNT_ID", ""),
            },
            # Time Doctor
            "time_doctor": {
                "access_token": os.getenv("TIME_DOCTOR_ACCESS_TOKEN", ""),
                "company_id": os.getenv("TIME_DOCTOR_COMPANY_ID", ""),
            },
            # Google Sheets
            "google_sheets": {
                "client_id": os.getenv("GOOGLE_SHEETS_CLIENT_ID", ""),
                "client_secret": os.getenv("GOOGLE_SHEETS_CLIENT_SECRET", ""),
                "refresh_token": os.getenv("GOOGLE_SHEETS_REFRESH_TOKEN", ""),
            },
            # Scheduler
            "scheduler": {
                "enabled": os.getenv("SCHEDULER_ENABLED", "true").lower() == "true"
            },
            # API
            "api": {
                "host": os.getenv("API_HOST", "0.0.0.0"),
                "port": int(os.getenv("API_PORT", "8000")),
                "reload": os.getenv("API_RELOAD", "false").lower() == "true",
            },
            # Logging
            "logging": {
                "level": os.getenv("LOG_LEVEL", "INFO"),
                "file": os.getenv("LOG_FILE", None),
            },
        }

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-notation key.

        Args:
            key: Configuration key (e.g., "database.url")
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key.split(".")
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any):
        """
        Set configuration value by dot-notation key.

        Args:
            key: Configuration key (e.g., "database.url")
            value: Value to set
        """
        keys = key.split(".")
        config = self.config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    def save_to_file(self, config_file: str):
        """Save configuration to JSON file."""
        with open(config_file, "w") as f:
            json.dump(self.config, f, indent=2)


# Global configuration instance
config = Config()
