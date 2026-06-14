"""
Text-to-Speech module using Piper for audio synthesis.

This module provides speech synthesis capabilities with:
- Robust error handling for missing models and synthesis failures
- Support for multiple languages and voices
- Automatic retry mechanisms for failed operations
- Detailed logging for debugging
- Audio file validation and cleanup
"""

import subprocess
import sys
from pathlib import Path
import logging
import time
from typing import Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
PYTHON_BIN = ROOT_DIR / "venv/bin/python"


@dataclass
class VoiceConfig:
    """Configuration for a TTS voice."""
    model_path: Path
    language: str


class TTSError(Exception):
    """Base exception for TTS operations."""
    pass


class TTSConfigError(TTSError):
    """Exception raised for configuration errors."""
    pass


class TTSSynthesisError(TTSError):
    """Exception raised when synthesis fails."""
    pass


def _validate_voice_model(model_path: Path) -> bool:
    """
    Validate that the voice model file exists and is valid.
    
    Args:
        model_path: Path to the voice model file
        
    Returns:
        True if model is valid
        
    Raises:
        TTSConfigError: If model is invalid
    """
    if not model_path.exists():
        raise TTSConfigError(f"Voice model not found: {model_path}")
    
    if not model_path.is_file():
        raise TTSConfigError(f"Voice model is not a file: {model_path}")
    
    # Check file size (voice models should be > 100MB typically)
    file_size = model_path.stat().st_size
    if file_size < 10000000:  # Less than 10MB
        logger.warning(
            f"Voice model seems unusually small: {file_size / 1024 / 1024:.1f} MB"
        )
    
    logger.info(f"Voice model valid: {model_path} ({file_size / 1024 / 1024:.1f} MB)")
    return True


def _validate_output_path(output_path: Path) -> bool:
    """
    Validate that output directory is writable.
    
    Args:
        output_path: Path where output will be written
        
    Returns:
        True if directory is valid and writable
        
    Raises:
        TTSError: If directory is not writable
    """
    output_dir = output_path.parent
    
    if not output_dir.exists():
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created output directory: {output_dir}")
        except OSError as e:
            raise TTSError(f"Cannot create output directory {output_dir}: {e}")
    
    if not output_dir.is_dir():
        raise TTSError(f"Output path is not a directory: {output_dir}")
    
    # Test write permissions
    try:
        test_file = output_dir / ".write_test"
        test_file.touch()
        test_file.unlink()
        logger.debug(f"Output directory is writable: {output_dir}")
    except OSError as e:
        raise TTSError(f"Output directory is not writable: {output_dir} - {e}")
    
    return True


def _get_python_executable() -> str:
    """
    Get the Python executable to use for Piper.
    
    Prefers venv Python if available, falls back to system Python.
    
    Returns:
        Path to Python executable
    """
    if PYTHON_BIN.exists():
        logger.debug(f"Using venv Python: {PYTHON_BIN}")
        return str(PYTHON_BIN)
    else:
        logger.debug(f"Using system Python: {sys.executable}")
        return sys.executable


def speak(
    text: str,
    output_wav: str,
    voice_model_path: Optional[Path] = None,
    retry_count: int = 1
) -> None:
    """
    Synthesize text to speech and save to WAV file.
    
    This function:
    - Validates input text and output path
    - Ensures voice model is available
    - Runs Piper with proper configuration
    - Handles synthesis errors with retry logic
    
    Args:
        text: Text to synthesize
        output_wav: Path where output WAV file will be saved
        voice_model_path: Path to voice model ONNX file.
                         If None, uses en_US-lessac-high
        retry_count: Number of retry attempts (default: 1)
        
    Raises:
        TTSConfigError: If configuration is invalid
        TTSSynthesisError: If synthesis fails
        TTSError: For other errors
    """
    # Validate input
    if not text or not isinstance(text, str):
        raise TTSError("Text must be a non-empty string")
    
    if len(text) > 10000:
        logger.warning(f"Text very long ({len(text)} chars), synthesis may take time")
    
    output_path = Path(output_wav)
    
    # Use default voice if not specified
    if voice_model_path is None:
        voice_model_path = ROOT_DIR / "piper/voices/en_US-lessac-high.onnx"
    else:
        voice_model_path = Path(voice_model_path)
    
    # Validate prerequisites
    try:
        _validate_voice_model(voice_model_path)
    except TTSConfigError as e:
        logger.error(f"Voice model validation failed: {e}")
        raise
    
    try:
        _validate_output_path(output_path)
    except TTSError as e:
        logger.error(f"Output path validation failed: {e}")
        raise
    
    # Get Python executable
    python_executable = _get_python_executable()
    
    # Attempt synthesis with retries
    attempt = 0
    last_error = None
    
    while attempt < retry_count:
        try:
            attempt += 1
            logger.info(f"Synthesis attempt {attempt}/{retry_count}")
            
            cmd = [
                python_executable,
                "-m",
                "piper",
                "--model",
                str(voice_model_path),
                "--output_file",
                str(output_path)
            ]
            
            # Run synthesis
            result = subprocess.run(
                cmd,
                input=text.encode("utf-8"),
                check=False,
                capture_output=True,
                timeout=120
            )
            
            if result.returncode != 0:
                error_msg = result.stderr.decode("utf-8", errors="ignore") or "Unknown error"
                raise TTSSynthesisError(
                    f"Piper failed with code {result.returncode}: {error_msg}"
                )
            
            # Verify output was created
            if not output_path.exists():
                raise TTSSynthesisError(f"Output file not created: {output_path}")
            
            # Check output file size
            file_size = output_path.stat().st_size
            if file_size < 1000:  # Less than 1KB
                raise TTSSynthesisError(
                    f"Output file too small ({file_size} bytes), synthesis likely failed"
                )
            
            logger.info(f"Synthesis successful: {output_path} ({file_size / 1024:.1f} KB)")
            return
            
        except subprocess.TimeoutExpired:
            last_error = TTSSynthesisError(
                f"Synthesis timed out (120 seconds) on attempt {attempt}"
            )
            logger.warning(f"{last_error}")
            if attempt < retry_count:
                time.sleep(2)
                continue
            raise last_error
            
        except TTSSynthesisError as e:
            last_error = e
            logger.warning(f"Synthesis failed on attempt {attempt}: {e}")
            if attempt < retry_count:
                time.sleep(2)
                continue
            raise
            
        except Exception as e:
            last_error = TTSError(f"Unexpected error during synthesis: {e}")
            logger.error(f"{last_error}")
            if attempt < retry_count:
                time.sleep(2)
                continue
            raise last_error
    
    # Should not reach here, but just in case
    if last_error:
        raise last_error
    else:
        raise TTSError("Synthesis failed for unknown reason")