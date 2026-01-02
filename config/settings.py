"""
config/settings.py - Application Settings

Centralized configuration with environment variable support.
"""

import os
from dataclasses import dataclass, field
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class Settings:
    """Application settings with defaults and env overrides."""
    
    # API Configuration
    gemini_api_key: str = field(default_factory=lambda: os.getenv("GEMINI_API_KEY", ""))
    gemini_model: str = field(default_factory=lambda: os.getenv("GEMINI_MODEL", "gemini-2.5-flash"))
    
    # Retry Configuration
    max_retries: int = 3
    base_retry_delay: float = 1.0
    
    # Database Configuration
    chroma_db_path: str = "./data/judge_db"
    collection_name: str = "judge_rulebook"
    
    # Data Files
    jurors_file: str = "./data/jurors.json"
    
    # Trial Configuration
    max_argument_rounds: int = 5
    jury_size: int = 6
    parallel_jury_workers: int = 6
    
    # Autonomous Debate Configuration
    autonomous_min_rounds: int = 2
    autonomous_max_rounds: int = 5
    
    # UI Configuration
    app_title: str = "Lex Umbra"
    app_subtitle: str = "The Shadow Judicial System"
    
    def validate(self) -> bool:
        """Validate required settings."""
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is required. Set it in your .env file.")
        return True


# Singleton instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get the application settings singleton."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
