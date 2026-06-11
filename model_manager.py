"""
Model management utilities for the English Tutor Offline application.

This module handles:
- Checking available LLM models in Ollama
- Downloading new models from Ollama
- Managing TTS voice models locally
- Providing model availability information
"""

import logging
from typing import List, Dict, Optional
from ollama import Client, ChatResponse, ListResponse
import time

logger = logging.getLogger(__name__)


class ModelManager:
    """
    Manages language models and voice models.
    
    Handles both Ollama LLM models and local Piper TTS voice models,
    providing unified interface for checking and downloading models.
    """
    
    # Curated list of recommended models for English tutoring
    RECOMMENDED_LLM_MODELS = [
        "llama3.1:latest",
        "neural-chat:latest",
        "mistral:latest",
    ]
    
    # All searchable models (can be downloaded from Ollama)
    SEARCHABLE_MODELS = [
        "llama3.1:latest",
        "llama2:latest",
        "mistral:latest",
        "neural-chat:latest",
        "wizard-math:latest",
        "codellama:latest",
        "qwen2.5-coder:latest",
    ]
    
    def __init__(self, ollama_host: str = "http://localhost:11434"):
        """
        Initialize ModelManager.
        
        Args:
            ollama_host: URL for Ollama server
        """
        self.ollama_host = ollama_host
        self.client = None
        self._ensure_ollama_connection()
    
    def _ensure_ollama_connection(self) -> bool:
        """
        Ensure connection to Ollama server.
        
        Returns:
            True if connected, False otherwise
        """
        try:
            self.client = Client(host=self.ollama_host)
            # Test connection
            self.client.list()
            logger.info("Connected to Ollama server")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Ollama: {e}")
            self.client = None
            return False
    
    def is_ollama_running(self) -> bool:
        """
        Check if Ollama server is running.
        
        Returns:
            True if server is running, False otherwise
        """
        if self.client is None:
            return self._ensure_ollama_connection()
        
        try:
            self.client.list()
            return True
        except Exception as e:
            logger.warning(f"Ollama connection lost: {e}")
            return False
    
    def get_available_models(self) -> List[str]:
        """
        Get list of models currently available in Ollama.
        
        Returns:
            List of model names, empty list if unable to connect
        """
        if not self.is_ollama_running():
            logger.warning("Cannot get available models: Ollama not running")
            return []
        
        try:
            response = self.client.list()
            models = [model.model for model in response.models] if response.models else []
            logger.info(f"Found {len(models)} available models")
            return models
        except Exception as e:
            logger.error(f"Error getting available models: {e}")
            return []
    
    def model_exists(self, model_name: str) -> bool:
        """
        Check if a model exists in Ollama.
        
        Args:
            model_name: Name of the model to check
            
        Returns:
            True if model exists, False otherwise
        """
        available_models = self.get_available_models()
        return model_name in available_models
    
    def download_model(self, model_name: str, show_progress: bool = True) -> bool:
        """
        Download a model from Ollama registry.
        
        Args:
            model_name: Name of the model to download
            show_progress: Whether to show download progress
            
        Returns:
            True if download successful, False otherwise
        """
        if not self.is_ollama_running():
            logger.error("Cannot download model: Ollama server not running")
            return False
        
        if self.model_exists(model_name):
            logger.info(f"Model {model_name} already exists")
            return True
        
        try:
            logger.info(f"Starting download of {model_name}...")
            
            # Attempt to pull the model
            self.client.pull(model_name)
            
            # Verify download was successful
            if self.model_exists(model_name):
                logger.info(f"Successfully downloaded {model_name}")
                return True
            else:
                logger.error(f"Model {model_name} not found after download")
                return False
                
        except Exception as e:
            logger.error(f"Failed to download model {model_name}: {e}")
            return False
    
    def get_model_size_estimate(self, model_name: str) -> str:
        """
        Get estimated size of a model.
        
        Note: This is a rough estimate based on model name patterns.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Estimated size as string (e.g., "3.5 GB")
        """
        # Rough estimates based on common model naming
        size_map = {
            "llama2": "3.5 GB",
            "llama3.1": "4.7 GB",
            "mistral": "4.1 GB",
            "neural-chat": "4.1 GB",
            "wizard-math": "13 GB",
            "codellama": "3.5 GB",
            "qwen": "4.0 GB",
        }
        
        for pattern, size in size_map.items():
            if pattern in model_name.lower():
                return size
        
        return "Unknown"
    
    def validate_model_name(self, model_name: str) -> bool:
        """
        Validate that a model name has correct format.
        
        Args:
            model_name: Model name to validate
            
        Returns:
            True if format is valid, False otherwise
        """
        if not model_name or not isinstance(model_name, str):
            return False
        
        if len(model_name) < 3 or len(model_name) > 100:
            return False
        
        # Check for valid characters (alphanumeric, colons, hyphens, underscores, dots)
        valid_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789:-_.")
        if not all(c in valid_chars for c in model_name):
            return False
        
        return True
    
    def get_recommended_models(self) -> List[str]:
        """
        Get list of recommended models for English tutoring.
        
        Returns:
            List of recommended model names
        """
        return self.RECOMMENDED_LLM_MODELS
    
    def get_searchable_models(self) -> List[str]:
        """
        Get list of models that can be searched and downloaded.
        
        Returns:
            List of searchable model names
        """
        return self.SEARCHABLE_MODELS
    
    def test_model(self, model_name: str, test_prompt: str = "Say 'hello'") -> bool:
        """
        Test a model by running a simple inference.
        
        Args:
            model_name: Name of the model to test
            test_prompt: Prompt to send to the model
            
        Returns:
            True if model works, False otherwise
        """
        if not self.is_ollama_running():
            logger.error("Cannot test model: Ollama server not running")
            return False
        
        try:
            response = self.client.generate(model=model_name, prompt=test_prompt)
            if response and 'response' in response:
                logger.info(f"Model {model_name} test successful")
                return True
            else:
                logger.error(f"Model {model_name} test failed: invalid response")
                return False
        except Exception as e:
            logger.error(f"Error testing model {model_name}: {e}")
            return False


class VoiceModelManager:
    """
    Manages voice models for Piper TTS.
    
    Handles verification of local voice model files.
    """
    
    def __init__(self):
        """Initialize VoiceModelManager."""
        pass
    
    @staticmethod
    def check_voice_model(model_path) -> bool:
        """
        Check if a voice model file exists and is valid.
        
        Args:
            model_path: Path to the voice model file
            
        Returns:
            True if model exists and has valid size, False otherwise
        """
        from pathlib import Path
        
        model_path = Path(model_path)
        
        if not model_path.exists():
            logger.error(f"Voice model not found: {model_path}")
            return False
        
        # Check file size (voice models should be > 100MB typically)
        file_size = model_path.stat().st_size
        if file_size < 1000000:  # Less than 1MB
            logger.warning(f"Voice model seems too small: {file_size} bytes")
            return False
        
        logger.info(f"Voice model valid: {model_path} ({file_size / 1024 / 1024:.1f} MB)")
        return True
