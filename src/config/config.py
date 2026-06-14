"""
Configuration management module for the English Tutor Offline application.

This module handles loading, saving, and managing application settings including:
- Current LLM model
- Current TTS voice
- Spoken language
- Audio recording parameters

The configuration is persisted to a JSON file to maintain user settings between sessions.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
import logging

# Setup logging for config module
logger = logging.getLogger(__name__)


@dataclass
class TTSVoiceConfig:
    """Configuration for Text-to-Speech voice settings."""
    language_code: str  # e.g., "en_US", "de_DE"
    voice_name: str     # e.g., "lessac-high", "thorsten-medium"
    model_path: Path
    
    def __post_init__(self):
        """Ensure model_path is a Path object."""
        if isinstance(self.model_path, str):
            self.model_path = Path(self.model_path)


@dataclass
class STTModelConfig:
    """Configuration for Speech-to-Text model settings."""
    language_code: str  # e.g., "en", "de"
    model_name: str     # e.g., "base.en", "base.de"
    

@dataclass
class AppConfig:
    """Main application configuration."""
    llm_model: str = "llama3.1:latest"
    tts_voice: TTSVoiceConfig = None
    stt_language: STTModelConfig = None
    record_seconds: int = 5
    system_prompt: str = ""
    
    def __post_init__(self):
        """Initialize default configs if not provided."""
        if self.tts_voice is None:
            self.tts_voice = TTSVoiceConfig(
                language_code="en_US",
                voice_name="lessac-high",
                model_path=Path("piper/voices/en_US-lessac-high.onnx")
            )
        if self.stt_language is None:
            self.stt_language = STTModelConfig(
                language_code="en",
                model_name="base.en"
            )


class ConfigManager:
    """
    Manages application configuration persistence and access.
    
    Provides methods to:
    - Load configuration from file or create defaults
    - Save configuration to file
    - Validate configuration integrity
    - Ensure safe type conversions
    """
    SYSTEM_PROMPT = "You are a language professor."

    CONFIG_FILE = Path("data/config.json")
    
    # Available voices and their paths
    AVAILABLE_VOICES = {
        "en_US": {
            "lessac-high": Path("piper/voices/en_US-lessac-high.onnx"),
        },
        "de_DE": {
            "thorsten-medium": Path("piper/voices/de_DE-thorsten-medium.onnx"),
        },
    }
    
    # Available STT languages
    AVAILABLE_STT_LANGUAGES = {
        "en": "base.en",
        "de": "base.de",
    }
    
    def __init__(self):
        """Initialize ConfigManager and load configuration."""
        self.config = None
        self._load_or_create_config()
    
    def _load_or_create_config(self) -> None:
        """
        Load configuration from file or create default configuration.
        
        Attempts to load config.json from the data directory. If the file
        doesn't exist or is corrupted, creates a default configuration.
        """
        try:
            if self.CONFIG_FILE.exists():
                with open(self.CONFIG_FILE, 'r') as f:
                    data = json.load(f)
                    self.config = self._dict_to_config(data)
                logger.info(f"Loaded configuration from {self.CONFIG_FILE}")
            else:
                self.config = AppConfig()
                self._ensure_config_dir()
                self.save()
                logger.info("Created new configuration with defaults")
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to load config: {e}. Using defaults.")
            self.config = AppConfig()
    
    def _ensure_config_dir(self) -> None:
        """Ensure the config directory exists."""
        self.CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    def _dict_to_config(self, data: Dict[str, Any]) -> AppConfig:
        """
        Convert dictionary to AppConfig object with validation.
        
        Args:
            data: Dictionary containing configuration data
            
        Returns:
            AppConfig object with validated and converted data
        """
        try:
            tts_voice_data = data.get("tts_voice", {})
            tts_voice = TTSVoiceConfig(
                language_code=tts_voice_data.get("language_code", "en_US"),
                voice_name=tts_voice_data.get("voice_name", "lessac-high"),
                model_path=Path(tts_voice_data.get("model_path", "piper/voices/en_US-lessac-high.onnx"))
            )
            
            stt_lang_data = data.get("stt_language", {})
            stt_language = STTModelConfig(
                language_code=stt_lang_data.get("language_code", "en"),
                model_name=stt_lang_data.get("model_name", "base.en")
            )
            
            return AppConfig(
                llm_model=data.get("llm_model", "llama3.1:latest"),
                tts_voice=tts_voice,
                stt_language=stt_language,
                record_seconds=data.get("record_seconds", 5),
                system_prompt=data.get("system_prompt", self.SYSTEM_PROMPT)
            )
        except Exception as e:
            logger.error(f"Error converting config dict: {e}. Using defaults.")
            return AppConfig()
    
    def save(self) -> None:
        """
        Save current configuration to file.
        
        Converts AppConfig to dictionary and persists to JSON file.
        Creates necessary directories if they don't exist.
        """
        try:
            self._ensure_config_dir()
            config_dict = {
                "llm_model": self.config.llm_model,
                "tts_voice": {
                    "language_code": self.config.tts_voice.language_code,
                    "voice_name": self.config.tts_voice.voice_name,
                    "model_path": str(self.config.tts_voice.model_path),
                },
                "stt_language": {
                    "language_code": self.config.stt_language.language_code,
                    "model_name": self.config.stt_language.model_name,
                },
                "record_seconds": self.config.record_seconds,
                "system_prompt": self.config.system_prompt
            }
            
            with open(self.CONFIG_FILE, 'w') as f:
                json.dump(config_dict, f, indent=2)
            logger.info(f"Configuration saved to {self.CONFIG_FILE}")
        except IOError as e:
            logger.error(f"Failed to save configuration: {e}")
            raise
    
    def get_config(self) -> AppConfig:
        """
        Get the current application configuration.
        
        Returns:
            AppConfig object with current settings
        """
        return self.config
    
    def set_system_prompt(self, system_prompt: str)-> None:
        """
        Set the system prompt for the LLM to use.
        
        Args:
            system_prompt: Text to use as prompt. (e.g., "You are an English teacher.")  
        """
        self.config.system_prompt = system_prompt
        self.save()
        logger.info(f"System prompt set to: \"{system_prompt}\".")

    def set_llm_model(self, model_name: str) -> None:
        """
        Set the LLM model to use.
        
        Args:
            model_name: Name of the model (e.g., "llama3.1:latest")
        """
        self.config.llm_model = model_name
        self.save()
        logger.info(f"LLM model set to {model_name}")
    
    def set_tts_voice(self, language_code: str, voice_name: str) -> bool:
        """
        Set the TTS voice.
        
        Args:
            language_code: Language code (e.g., "en_US", "de_DE")
            voice_name: Voice name (e.g., "lessac-high")
            
        Returns:
            True if successful, False if voice not available
        """
        if language_code not in self.AVAILABLE_VOICES:
            logger.error(f"Language {language_code} not available")
            return False
        
        if voice_name not in self.AVAILABLE_VOICES[language_code]:
            logger.error(f"Voice {voice_name} not available for {language_code}")
            return False
        
        model_path = self.AVAILABLE_VOICES[language_code][voice_name]
        if not model_path.exists():
            logger.error(f"Voice model file not found: {model_path}")
            return False
        
        self.config.tts_voice = TTSVoiceConfig(
            language_code=language_code,
            voice_name=voice_name,
            model_path=model_path
        )
        self.save()
        logger.info(f"TTS voice set to {language_code}/{voice_name}")
        return True
    
    def set_stt_language(self, language_code: str) -> bool:
        """
        Set the STT language.
        
        Args:
            language_code: Language code (e.g., "en", "de")
            
        Returns:
            True if successful, False if language not available
        """
        if language_code not in self.AVAILABLE_STT_LANGUAGES:
            logger.error(f"STT language {language_code} not available")
            return False
        
        model_name = self.AVAILABLE_STT_LANGUAGES[language_code]
        self.config.stt_language = STTModelConfig(
            language_code=language_code,
            model_name=model_name
        )
        self.save()
        logger.info(f"STT language set to {language_code}")
        return True
    
    @staticmethod
    def get_available_voices() -> Dict[str, list]:
        """
        Get all available TTS voices.
        
        Returns:
            Dictionary mapping language codes to available voices
        """
        return ConfigManager.AVAILABLE_VOICES
    
    @staticmethod
    def get_available_stt_languages() -> Dict[str, str]:
        """
        Get all available STT languages.
        
        Returns:
            Dictionary mapping language codes to model names
        """
        return ConfigManager.AVAILABLE_STT_LANGUAGES
