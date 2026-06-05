"""
Configuration management for CABP Client Application.
Handles environment variables and application settings using Pydantic.
"""

import os
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class CABPConfig(BaseModel):
    """
    CABP Client Configuration Model.
    
    Manages all application configuration with validation and defaults.
    Configuration can be provided via environment variables or .env file.
    """
    
    # API Configuration
    base_url: str = Field(
        default=os.getenv("CABP_BASE_URL", "http://localhost:8000"),
        description="CABP API base URL"
    )
    api_key: Optional[str] = Field(
        default=os.getenv("CABP_API_KEY"),
        description="API authentication key"
    )
    
    # Request Configuration
    timeout: int = Field(
        default=int(os.getenv("REQUEST_TIMEOUT", "30")),
        description="Request timeout in seconds",
        ge=1,
        le=300
    )
    max_retries: int = Field(
        default=int(os.getenv("MAX_RETRIES", "3")),
        description="Maximum retry attempts for failed requests",
        ge=0,
        le=10
    )
    retry_delay: int = Field(
        default=int(os.getenv("RETRY_DELAY", "1")),
        description="Delay between retries in seconds",
        ge=0,
        le=60
    )
    
    # Logging Configuration
    log_level: str = Field(
        default=os.getenv("LOG_LEVEL", "INFO"),
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )
    log_file: str = Field(
        default=os.getenv("LOG_FILE", "cabp_client.log"),
        description="Log file path"
    )
    log_format: str = Field(
        default=os.getenv(
            "LOG_FORMAT",
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        ),
        description="Log message format"
    )
    
    # Environment
    environment: str = Field(
        default=os.getenv("ENVIRONMENT", "development"),
        description="Application environment (development, staging, production)"
    )
    
    # Feature Flags
    enable_debug: bool = Field(
        default=os.getenv("ENABLE_DEBUG", "false").lower() == "true",
        description="Enable debug mode"
    )
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is one of the allowed values."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(
                f"Invalid log level: {v}. Must be one of {valid_levels}"
            )
        return v_upper
    
    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment is one of the allowed values."""
        valid_envs = ["development", "staging", "production"]
        v_lower = v.lower()
        if v_lower not in valid_envs:
            raise ValueError(
                f"Invalid environment: {v}. Must be one of {valid_envs}"
            )
        return v_lower
    
    @field_validator("base_url")
    @classmethod
    def validate_base_url(cls, v: str) -> str:
        """Validate and normalize base URL."""
        if not v:
            raise ValueError("Base URL cannot be empty")
        # Remove trailing slash
        return v.rstrip("/")
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"
    
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"
    
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == "development"
    
    def get_full_url(self, endpoint: str) -> str:
        """
        Get full URL for an endpoint.
        
        Args:
            endpoint: API endpoint path
            
        Returns:
            Full URL combining base_url and endpoint
        """
        endpoint = endpoint.lstrip("/")
        return f"{self.base_url}/{endpoint}"


# Global configuration instance
# This will be imported and used throughout the application
config = CABPConfig()


def reload_config() -> CABPConfig:
    """
    Reload configuration from environment.
    Useful for testing or when environment variables change.
    
    Returns:
        New configuration instance
    """
    load_dotenv(override=True)
    return CABPConfig()

# Made with Bob
