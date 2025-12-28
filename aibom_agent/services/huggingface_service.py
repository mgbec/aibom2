"""Hugging Face integration service."""

import asyncio
from typing import Optional

from huggingface_hub import HfApi, model_info, list_repo_files
from loguru import logger

from ..config.settings import HuggingFaceSettings
from ..models.analysis_result import ModelInfo


class HuggingFaceService:
    """Service for interacting with Hugging Face Hub."""
    
    def __init__(self, settings: HuggingFaceSettings):
        self.settings = settings
        self.api: Optional[HfApi] = None
    
    async def initialize(self) -> None:
        """Initialize the Hugging Face API client."""
        logger.info("Initializing Hugging Face service...")
        
        self.api = HfApi(token=self.settings.token)
        
        # Test connection
        try:
            await asyncio.get_event_loop().run_in_executor(
                None, self.api.whoami
            )
            logger.info("Hugging Face service initialized successfully")
        except Exception as e:
            logger.warning(f"Hugging Face authentication failed: {e}")
            # Continue without authentication for public models
    
    async def get_model_info(self, model_name: str) -> ModelInfo:
        """
        Fetch comprehensive information about a Hugging Face model.
        
        Args:
            model_name: Name of the model (e.g., 'microsoft/DialoGPT-medium')
            
        Returns:
            ModelInfo object with model details
        """
        logger.info(f"Fetching model info for: {model_name}")
        
        try:
            # Get model information
            info = await asyncio.get_event_loop().run_in_executor(
                None, model_info, model_name
            )
            
            # Get file list
            files = await asyncio.get_event_loop().run_in_executor(
                None, list_repo_files, model_name
            )
            
            # Convert to our ModelInfo structure
            model_info_obj = ModelInfo(
                name=model_name,
                author=info.author or "unknown",
                description=getattr(info, 'description', None),
                tags=info.tags or [],
                pipeline_tag=getattr(info, 'pipeline_tag', None),
                library_name=getattr(info, 'library_name', None),
                license=getattr(info, 'license', None),
                downloads=getattr(info, 'downloads', 0),
                likes=getattr(info, 'likes', 0),
                created_at=str(getattr(info, 'created_at', '')),
                last_modified=str(getattr(info, 'last_modified', '')),
                model_size=self._estimate_model_size(files),
                config=getattr(info, 'config', {}) or {},
                files=[{"name": f, "size": None} for f in files]
            )
            
            logger.info(f"Successfully fetched info for {model_name}")
            return model_info_obj
            
        except Exception as e:
            logger.error(f"Failed to fetch model info for {model_name}: {e}")
            raise
    
    def _estimate_model_size(self, files: list) -> Optional[int]:
        """Estimate model size based on file list."""
        # This is a simplified estimation
        # In practice, you'd want to get actual file sizes
        model_files = [f for f in files if f.endswith(('.bin', '.safetensors', '.h5'))]
        if model_files:
            # Rough estimation based on number of model files
            return len(model_files) * 500_000_000  # 500MB per file estimate
        return None
    
    async def download_model_files(self, model_name: str, file_patterns: list[str]) -> dict:
        """
        Download specific model files for analysis.
        
        Args:
            model_name: Name of the model
            file_patterns: List of file patterns to download
            
        Returns:
            Dictionary mapping file names to local paths
        """
        logger.info(f"Downloading files for {model_name}: {file_patterns}")
        
        # Implementation would use huggingface_hub.snapshot_download
        # with allow_patterns parameter
        
        # Placeholder implementation
        return {}
    
    async def cleanup(self) -> None:
        """Clean up resources."""
        logger.info("Cleaning up Hugging Face service...")
        # Clean up any cached files or connections
        pass