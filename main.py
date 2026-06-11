"""
English Tutor Offline - Main Application Entry Point

This application provides an interactive CLI for practicing English with an AI tutor.

Features:
- Speech recognition (Whisper.cpp)
- AI tutoring (Ollama)
- Text-to-speech (Piper)
- Configurable models and voices
- Full conversation history
- Error recovery with retries

Usage:
    python3 main.py

The application will start an interactive menu where you can:
1. Start a conversation
2. Configure settings (models, voices, languages)
3. View application status
4. Exit

Requirements:
- Ollama (LLM inference)
- Whisper.cpp (speech recognition)
- Piper (text-to-speech)
- ffplay (audio playback)
- arecord (audio recording)
"""

import sys
import logging
from pathlib import Path

# Ensure data directory exists
DATA_DIR = Path("data")
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(DATA_DIR / "tutor.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

try:
    from orchestrator import orchest
    
    def main():
        """Main application entry point."""
        logger.info("=" * 70)
        logger.info("English Tutor Offline Starting")
        logger.info("=" * 70)
        
        try:
            orchest()
        except KeyboardInterrupt:
            print("\n\nApplication interrupted by user. Goodbye!")
            logger.info("Application interrupted by user")
            sys.exit(0)
        except Exception as e:
            logger.error(f"Fatal error: {e}", exc_info=True)
            print(f"\nFatal error: {e}")
            print("Check the log file at data/tutor.log for more details.")
            sys.exit(1)
    
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    print(f"Error: Failed to import required modules: {e}")
    print("\nPlease ensure all dependencies are installed:")
    print("  pip install ollama piper-tts whisper")
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)