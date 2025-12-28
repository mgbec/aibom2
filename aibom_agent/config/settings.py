"""Configuration settings for the AIBOM Agent System."""

import os
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings
from pydantic import Field


class AWSSettings(BaseSettings):
    """AWS-specific configuration."""
    
    region: str = Field(default="us-east-1", env="AWS_REGION")
    bedrock_agent_id: Optional[str] = Field(default=None, env="BEDROCK_AGENT_ID")
    bedrock_agent_alias_id: str = Field(default="TSTALIASID", env="BEDROCK_AGENT_ALIAS_ID")
    s3_bucket: Optional[str] = Field(default=None, env="AIBOM_S3_BUCKET")
    
    class Config:
        env_prefix = "AWS_"


class HuggingFaceSettings(BaseSettings):
    """Hugging Face configuration."""
    
    token: Optional[str] = Field(default=None, env="HF_TOKEN")
    cache_dir: str = Field(default="./cache/huggingface", env="HF_CACHE_DIR")
    
    class Config:
        env_prefix = "HF_"


class AIBOMSettings(BaseSettings):
    """AIBOM generation settings."""
    
    owasp_generator_path: str = Field(
        default="./tools/owasp-aibom-generator", 
        env="OWASP_AIBOM_GENERATOR_PATH"
    )
    output_format: str = Field(default="json", env="AIBOM_OUTPUT_FORMAT")
    include_dependencies: bool = Field(default=True, env="AIBOM_INCLUDE_DEPS")
    
    class Config:
        env_prefix = "AIBOM_"


class Settings(BaseSettings):
    """Main application settings."""
    
    # Application settings
    app_name: str = "AIBOM Agent System"
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Output settings
    output_dir: str = Field(default="./reports", env="OUTPUT_DIR")
    temp_dir: str = Field(default="./tmp", env="TEMP_DIR")
    
    # Component settings
    aws: AWSSettings = AWSSettings()
    huggingface: HuggingFaceSettings = HuggingFaceSettings()
    aibom: AIBOMSettings = AIBOMSettings()
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    @classmethod
    def load(cls, config_file: Optional[str] = None) -> "Settings":
        """Load settings from file or environment."""
        if config_file and Path(config_file).exists():
            return cls(_env_file=config_file)
        return cls()
    
    def ensure_directories(self) -> None:
        """Ensure required directories exist."""
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        Path(self.temp_dir).mkdir(parents=True, exist_ok=True)
        Path(self.huggingface.cache_dir).mkdir(parents=True, exist_ok=True)