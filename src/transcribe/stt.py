"""
Speech-to-Text module using Whisper.cpp for audio transcription.

This module provides speech recognition capabilities with:
- Robust error handling for missing files and failed transcription
- Support for multiple languages (en, de, etc.)
- Automatic retry mechanisms for failed operations
- Detailed logging for debugging
"""

import os
import subprocess
from pathlib import Path
import logging
import time
from typing import Optional

logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
WHISPER_CLI = ROOT_DIR / "whisper.cpp/build/bin/whisper-cli"
WHISPER_MODELS_DIR = ROOT_DIR / "whisper.cpp/models"
LIB_WHISPER_DIR = ROOT_DIR / "whisper.cpp/build/src"
LIB_GGML_DIR = ROOT_DIR / "whisper.cpp/build/ggml/src"

# Language to model mapping
LANGUAGE_MODELS = {
    "en": "ggml-base.en.bin",
    "de": "ggml-base.de.bin",
    "fr": "ggml-base.fr.bin",
}


class STTError(Exception):
    """Base exception for STT operations."""
    pass


class STTConfigError(STTError):
    """Exception raised for configuration errors."""
    pass


class STTTranscriptionError(STTError):
    """Exception raised when transcription fails."""
    pass


def _validate_prerequisites() -> bool:
    """
    Validate that all prerequisites for STT are available.
    
    Checks:
    - Whisper CLI binary exists
    - Library directories are accessible
    - At least one model is available
    
    Returns:
        True if all prerequisites are met
        
    Raises:
        STTConfigError: If any prerequisite is missing
    """
    errors = []
    
    if not WHISPER_CLI.exists():
        errors.append(f"Whisper CLI not found at {WHISPER_CLI}")
    
    if not LIB_WHISPER_DIR.exists():
        errors.append(f"Whisper library directory not found at {LIB_WHISPER_DIR}")
    
    if not LIB_GGML_DIR.exists():
        errors.append(f"GGML library directory not found at {LIB_GGML_DIR}")
    
    if not WHISPER_MODELS_DIR.exists():
        errors.append(f"Models directory not found at {WHISPER_MODELS_DIR}")
    
    if errors:
        error_msg = "\n".join(errors)
        logger.error(f"STT prerequisites not met:\n{error_msg}")
        raise STTConfigError(f"STT not properly configured:\n{error_msg}")
    
    logger.info("STT prerequisites validated successfully")
    return True


def _get_model_path(language: str) -> Path:
    """
    Get the model path for a given language.
    
    Args:
        language: Language code (e.g., "en", "de")
        
    Returns:
        Path to the model file
        
    Raises:
        STTConfigError: If model not found for language
    """
    if language not in LANGUAGE_MODELS:
        available = ", ".join(LANGUAGE_MODELS.keys())
        raise STTConfigError(
            f"Language '{language}' not supported. Available: {available}"
        )
    
    model_name = LANGUAGE_MODELS[language]
    model_path = WHISPER_MODELS_DIR / model_name
    
    if not model_path.exists():
        raise STTConfigError(
            f"Model file not found for language '{language}': {model_path}"
        )
    
    logger.info(f"Using model: {model_path}")
    return model_path


def _validate_audio_file(audio_path: Path) -> bool:
    """
    Validate that the audio file exists and is readable.
    
    Args:
        audio_path: Path to audio file
        
    Returns:
        True if file is valid
        
    Raises:
        STTError: If file is invalid
    """
    if not audio_path.exists():
        raise STTError(f"Audio file not found: {audio_path}")
    
    if not audio_path.is_file():
        raise STTError(f"Not a file: {audio_path}")
    
    # Check file size (should be at least a few KB)
    file_size = audio_path.stat().st_size
    if file_size < 1000:
        logger.warning(f"Audio file seems very small: {file_size} bytes")
    
    logger.info(f"Audio file validated: {audio_path} ({file_size} bytes)")
    return True


def _setup_environment() -> dict:
    """
    Setup environment variables for Whisper execution.
    
    Returns:
        Environment dictionary with library paths configured
    """
    env = os.environ.copy()
    lib_paths = ":".join(str(p) for p in [LIB_WHISPER_DIR, LIB_GGML_DIR])
    ld_path = env.get("LD_LIBRARY_PATH", "")
    env["LD_LIBRARY_PATH"] = f"{lib_paths}:{ld_path}" if ld_path else lib_paths
    
    logger.debug(f"Environment setup: LD_LIBRARY_PATH={env['LD_LIBRARY_PATH']}")
    return env


def transcribe(audio_path: str, language: str = "en", retry_count: int = 1) -> str:
    """
    Transcribe audio file to text using Whisper.cpp.
    
    This function:
    - Validates input audio file
    - Ensures model is available
    - Runs Whisper CLI with proper environment
    - Returns transcribed text
    - Provides detailed error messages on failure
    
    Args:
        audio_path: Path to audio file (WAV format)
        language: Language code (default: "en")
        retry_count: Number of retry attempts (default: 1)
        
    Returns:
        Transcribed text as string
        
    Raises:
        STTConfigError: If configuration is invalid
        STTTranscriptionError: If transcription fails
        STTError: For other errors
    """
    audio_path = Path(audio_path)
    attempt = 0
    last_error = None
    
    # Validate prerequisites once
    try:
        _validate_prerequisites()
    except STTConfigError:
        raise
    
    # Validate audio file
    try:
        _validate_audio_file(audio_path)
    except STTError as e:
        logger.error(f"Audio validation failed: {e}")
        raise
    
    # Get model path
    try:
        model_path = _get_model_path(language)
    except STTConfigError as e:
        logger.error(f"Model configuration error: {e}")
        raise
    
    # Prepare output path
    out_prefix = audio_path.with_suffix("")
    txt_file = Path(str(out_prefix) + ".txt")
    
    # Attempt transcription with retries
    while attempt < retry_count:
        try:
            attempt += 1
            logger.info(f"Transcription attempt {attempt}/{retry_count}")
            
            cmd = [
                str(WHISPER_CLI),
                "-m", str(model_path),
                "-f", str(audio_path),
                "-l", language,
                "-otxt",
                "-of", str(out_prefix),
                "-nt"
            ]
            
            env = _setup_environment()
            
            # Run transcription
            result = subprocess.run(
                cmd,
                check=False,
                env=env,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode != 0:
                error_msg = result.stderr or result.stdout or "Unknown error"
                raise STTTranscriptionError(
                    f"Whisper CLI failed with code {result.returncode}: {error_msg}"
                )
            
            # Read transcription result
            if not txt_file.exists():
                raise STTTranscriptionError(
                    f"Transcription output file not created: {txt_file}"
                )
            
            transcript = txt_file.read_text(encoding="utf-8").strip()
            
            if not transcript:
                raise STTTranscriptionError("Transcription produced empty result")
            
            logger.info(f"Transcription successful: '{transcript[:50]}...'")
            return transcript
            
        except subprocess.TimeoutExpired:
            last_error = STTTranscriptionError(
                f"Transcription timed out (120 seconds) on attempt {attempt}"
            )
            logger.warning(f"{last_error}")
            if attempt < retry_count:
                time.sleep(2)
                continue
            raise last_error
            
        except STTTranscriptionError as e:
            last_error = e
            logger.warning(f"Transcription failed on attempt {attempt}: {e}")
            if attempt < retry_count:
                time.sleep(2)
                continue
            raise
            
        except Exception as e:
            last_error = STTError(f"Unexpected error during transcription: {e}")
            logger.error(f"{last_error}")
            if attempt < retry_count:
                time.sleep(2)
                continue
            raise last_error
    
    # Should not reach here, but just in case
    if last_error:
        raise last_error
    else:
        raise STTError("Transcription failed for unknown reason")