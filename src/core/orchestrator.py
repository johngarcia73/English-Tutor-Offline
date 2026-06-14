"""
Main orchestrator for the English Tutor Offline application.

This module coordinates all components:
- Audio recording and playback
- Speech-to-text transcription
- LLM chat interaction
- Text-to-speech synthesis
- Configuration management
- Error handling and recovery

The orchestrator provides the complete conversation pipeline.
"""

import subprocess
import logging
import time
from pathlib import Path
from typing import List, Optional, Tuple
from dataclasses import dataclass

from src.config.config import ConfigManager, AppConfig
from src.llm.model_manager import ModelManager
from src.cli.cli import Menu, CLIHelper
from src.transcribe.stt import transcribe as transcribe_audio, STTError
from src.llm.chat import ask_llm
from src.audio.tts import speak as synthesize_speech, TTSError
from src.llm.llm_server import (
    run_ollama, get_ollama_client, ollama_llms_available,
    download_model, check_ollama_server, get_response_text
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/tutor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
DATA_DIR = Path("data")
INPUT_AUDIO = DATA_DIR / "input.wav"
OUTPUT_AUDIO = DATA_DIR / "output.wav"
RECORD_SECONDS = 5


class RecordingError(Exception):
    """Exception for audio recording errors."""
    pass


class PlaybackError(Exception):
    """Exception for audio playback errors."""
    pass


@dataclass
class ConversationTurn:
    """Represents one turn in the conversation."""
    user_text: str
    llm_response: str
    timestamp: str


class AudioHandler:
    """Handles audio recording and playback."""
    
    @staticmethod
    def record_audio(output_path: Path, duration: int) -> None:
        """
        Record audio from microphone.
        
        Args:
            output_path: Where to save the WAV file
            duration: Recording duration in seconds
            
        Raises:
            RecordingError: If recording fails
        """
        try:
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Recording audio for {duration} seconds...")
            print(f"\n  🎤 Recording... (speak now, {duration} seconds)")
            
            result = subprocess.run(
                [
                    "arecord",
                    "-f", "cd",  # CD quality (16-bit, 44.1kHz, stereo)
                    "-d", str(duration),
                    str(output_path)
                ],
                check=False,
                capture_output=True,
                text=True,
                timeout=duration + 10
            )
            
            if result.returncode != 0:
                error = result.stderr or "Unknown error"
                raise RecordingError(f"arecord failed: {error}")
            
            if not output_path.exists():
                raise RecordingError("Recording file was not created")
            
            file_size = output_path.stat().st_size
            if file_size < 1000:
                raise RecordingError("Recording file is too small (likely empty)")
            
            logger.info(f"Audio recorded successfully: {output_path}")
            
        except subprocess.TimeoutExpired:
            raise RecordingError("Recording timeout (arecord didn't respond)")
        except Exception as e:
            raise RecordingError(f"Recording failed: {e}")
    
    @staticmethod
    def play_audio(audio_path: Path, max_retries: int = 2) -> None:
        """
        Play audio file.
        
        Args:
            audio_path: Path to audio file
            max_retries: Maximum retry attempts
            
        Raises:
            PlaybackError: If playback fails
        """
        if not audio_path.exists():
            raise PlaybackError(f"Audio file not found: {audio_path}")
        
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"Playing audio: {audio_path} (attempt {attempt})")
                print("\n  🔊 Playing response...")
                
                result = subprocess.run(
                    [
                        "ffplay",
                        "-nodisp",      # Don't display window
                        "-autoexit",    # Exit after playback
                        str(audio_path)
                    ],
                    check=False,
                    capture_output=True,
                    timeout=300  # 5 minutes max
                )
                
                if result.returncode == 0:
                    logger.info("Audio playback completed")
                    return
                else:
                    error = result.stderr.decode('utf-8', errors='ignore') or "Unknown error"
                    if attempt == max_retries:
                        raise PlaybackError(f"ffplay failed: {error}")
                    logger.warning(f"Playback attempt {attempt} failed, retrying...")
                    time.sleep(1)
                    
            except subprocess.TimeoutExpired:
                raise PlaybackError("Playback timeout (ffplay didn't respond)")
            except Exception as e:
                if attempt == max_retries:
                    raise PlaybackError(f"Playback failed: {e}")
                time.sleep(1)
        
        raise PlaybackError("Playback failed after all attempts")


class ConversationManager:
    """Manages the conversation history and state."""
    
    def __init__(self):
        """Initialize conversation manager."""
        self.history: List[ConversationTurn] = []
        self.chat_messages = []  # Format for LLM API
    
    def add_turn(self, user_text: str, llm_response: str) -> None:
        """
        Add a turn to the conversation.
        
        Args:
            user_text: User's input
            llm_response: LLM's response
        """
        from datetime import datetime
        turn = ConversationTurn(
            user_text=user_text,
            llm_response=llm_response,
            timestamp=datetime.now().isoformat()
        )
        self.history.append(turn)
        
        # Add to chat history
        self.chat_messages.append({"role": "user", "content": user_text})
        self.chat_messages.append({"role": "assistant", "content": llm_response})
        
        logger.info(f"Conversation turn added: {user_text[:50]}...")
    
    def get_history(self) -> List[dict]:
        """Get conversation history for LLM context."""
        return self.chat_messages
    
    def clear_history(self) -> None:
        """Clear conversation history."""
        self.history.clear()
        self.chat_messages.clear()
        logger.info("Conversation history cleared")
    
    def get_summary(self) -> str:
        """Get summary of conversation."""
        return f"Total turns: {len(self.history)}"


class ApplicationOrchestrator:
    """
    Main application orchestrator.
    
    Coordinates all components and manages the application flow.
    """
    
    def __init__(self):
        """Initialize the orchestrator."""
        self.config_manager = ConfigManager()
        self.model_manager = ModelManager()
        self.audio_handler = AudioHandler()
        self.conversation = ConversationManager()
        self.ollama_process = None
        self.is_running = False
    
    def _ensure_ollama_running(self) -> bool:
        """
        Ensure Ollama server is running.
        
        Returns:
            True if running, False otherwise
        """
        if self.model_manager.is_ollama_running():
            logger.info("Ollama server is running")
            return True
        
        logger.info("Starting Ollama server...")
        try:
            self.ollama_process = run_ollama()
            time.sleep(2)  # Wait for server to start
            
            if self.model_manager.is_ollama_running():
                logger.info("Ollama server started successfully")
                return True
            else:
                logger.error("Ollama server failed to start")
                return False
        except Exception as e:
            logger.error(f"Failed to start Ollama: {e}")
            return False
    
    def _show_main_menu(self) -> None:
        """Show the main menu."""
        menu = Menu("English Tutor Offline", "Main Menu")
        menu.add_option("1", "Start Talking", self._run_conversation, "Begin a conversation with the tutor")
        menu.add_option("2", "Options", self._show_options_menu, "Configure application settings")
        menu.add_option("3", "Status", self._show_status, "Show application status")
        menu.run()
    
    def _run_conversation(self) -> None:
        """Run a conversation session."""
        config = self.config_manager.get_config()
        
        # Ensure prerequisites
        if not self._ensure_ollama_running():
            CLIHelper.print_error("Ollama server is not available. Please start it manually.")
            return
        
        # Check current model exists
        if not self.model_manager.model_exists(config.llm_model):
            CLIHelper.print_error(f"Model '{config.llm_model}' not available.")
            CLIHelper.print_info("Available models:")
            for model in self.model_manager.get_available_models():
                print(f"  • {model}")
            return
        
        CLIHelper.print_section(f"Starting Conversation with {config.llm_model}")
        print("  Instructions:")
        print("    • Press ENTER to start talking")
        print("    • Speak clearly for the full duration")
        print("    • Press Ctrl+C to stop recording at any time")
        print("    • Press Ctrl+D to exit conversation\n")
        
        try:
            input("  Press ENTER to begin...")
        except (KeyboardInterrupt, EOFError):
            return
        
        # Conversation loop
        turn_count = 0
        while True:
            try:
                turn_count += 1
                print(f"\n  --- Turn {turn_count} ---")
                
                # Record user input
                try:
                    self.audio_handler.record_audio(INPUT_AUDIO, RECORD_SECONDS)
                except RecordingError as e:
                    CLIHelper.print_error(f"Recording failed: {e}")
                    if CLIHelper.get_yes_no("Try again?"):
                        continue
                    else:
                        break
                
                # Transcribe audio
                try:
                    print("  📝 Transcribing audio...")
                    user_text = transcribe_audio(
                        str(INPUT_AUDIO),
                        language=config.stt_language.language_code
                    )
                    print(f"  You said: \"{user_text}\"")
                except STTError as e:
                    CLIHelper.print_error(f"Transcription failed: {e}")
                    if CLIHelper.get_yes_no("Try again?"):
                        continue
                    else:
                        break
                
                # Get LLM response
                try:
                    print("  🤖 Thinking...")
                    llm_response = ask_llm(
                        user_text,
                        history=self.conversation.get_history(),
                        system_prompt=config.system_prompt
                    )
                    print(f"  Tutor: {llm_response}")
                except Exception as e:
                    CLIHelper.print_error(f"LLM error: {e}")
                    if CLIHelper.get_yes_no("Try again?"):
                        continue
                    else:
                        break
                
                # Synthesize response
                try:
                    print("  🎵 Synthesizing speech...")
                    synthesize_speech(
                        llm_response,
                        str(OUTPUT_AUDIO),
                        voice_model_path=config.tts_voice.model_path
                    )
                except TTSError as e:
                    CLIHelper.print_error(f"Speech synthesis failed: {e}")
                    if CLIHelper.get_yes_no("Try again?"):
                        continue
                    else:
                        break
                
                # Play response
                try:
                    self.audio_handler.play_audio(OUTPUT_AUDIO)
                except PlaybackError as e:
                    CLIHelper.print_warning(f"Playback failed: {e}")
                
                # Add to history
                self.conversation.add_turn(user_text, llm_response)
                
                # Ask if continue
                if not CLIHelper.get_yes_no("\nContinue conversation?"):
                    break
                    
            except KeyboardInterrupt:
                print("\n  Conversation interrupted by user.")
                break
            except EOFError:
                print("\n  Conversation ended.")
                break
            except Exception as e:
                logger.error(f"Unexpected error in conversation: {e}")
                CLIHelper.print_error(f"Unexpected error: {e}")
                if not CLIHelper.get_yes_no("Try again?"):
                    break
        
        CLIHelper.print_success(f"Conversation ended. Total turns: {turn_count}")
    
    def _show_options_menu(self) -> None:
        """Show options menu."""
        menu = Menu("Options", "Configuration Settings")
        menu.add_option("1", "Change LLM Model", self._change_llm_model)
        menu.add_option("2", "Run Ollama", self._ensure_ollama_running)
        menu.add_option("3", "Download New Model", self._download_model)
        menu.add_option("4", "Change Voice & Language", self._change_voice)
        menu.add_option("5", "Change System Prompt", self._change_system_prompt)
        menu.add_option("6", "View Configuration", self._view_config)
        menu.run()
    
    def _change_llm_model(self) -> None:
        """Change the LLM model."""
        CLIHelper.print_section("Change LLM Model")
        
        available_models = self.model_manager.get_available_models()
        if not available_models:
            CLIHelper.print_error("No models available. Ollama server may not be running.")
            return
        
        print("  Available models:")
        for i, model in enumerate(available_models, 1):
            print(f"    {i}. {model}")
        
        try:
            choice_idx = int(input("\n  Select model number (or press ENTER to cancel): ") or "-1") - 1
            if choice_idx < 0 or choice_idx >= len(available_models):
                print("  Cancelled.")
                return
            
            selected_model = available_models[choice_idx]
            self.config_manager.set_llm_model(selected_model)
            CLIHelper.print_success(f"Model changed to: {selected_model}")
            
        except ValueError:
            CLIHelper.print_error("Invalid input.")
    
    def _change_system_prompt(self):
        "Change the System Prompt"

        try:
            CLIHelper.print_section("Change System Prompt")

            prompt = input("Type the new system prompt:")
            CLIHelper.print_success(f"New prompt entablished")
            self.config_manager.set_system_prompt(prompt)

        except ValueError:
            CLIHelper.print_error("Invalid input.")

    def _download_model(self) -> None:
        """Download a new model."""
        CLIHelper.print_section("Download Model")
        
        print("  Recommended models:")
        recommended = self.model_manager.get_recommended_models()
        for i, model in enumerate(recommended, 1):
            size = self.model_manager.get_model_size_estimate(model)
            exists = "✓" if self.model_manager.model_exists(model) else "✗"
            print(f"    {i}. {model} [{size}] {exists}")
        
        print("\n  Other available models:")
        searchable = self.model_manager.get_searchable_models()
        for i, model in enumerate(searchable, len(recommended) + 1):
            size = self.model_manager.get_model_size_estimate(model)
            exists = "✓" if self.model_manager.model_exists(model) else "✗"
            print(f"    {i}. {model} [{size}] {exists}")
        
        try:
            choice_idx = int(input("\n  Select model number (or press ENTER to cancel): ") or "-1") - 1
            all_models = recommended + searchable
            if choice_idx < 0 or choice_idx >= len(all_models):
                print("  Cancelled.")
                return
            
            model_to_download = all_models[choice_idx]
            
            if self.model_manager.model_exists(model_to_download):
                CLIHelper.print_info(f"Model '{model_to_download}' already downloaded.")
                return
            
            if not CLIHelper.get_yes_no(f"Download {model_to_download}? (This may take several minutes)"):
                print("  Cancelled.")
                return
            
            print("\n  Downloading... (this may take a while)")
            if self.model_manager.download_model(model_to_download):
                CLIHelper.print_success(f"Model downloaded: {model_to_download}")
            else:
                CLIHelper.print_error(f"Failed to download: {model_to_download}")
                
        except ValueError:
            CLIHelper.print_error("Invalid input.")
    
    def _change_voice(self) -> None:
        """Change voice and language settings."""
        CLIHelper.print_section("Change Voice & Language")
        
        voices = self.config_manager.get_available_voices()
        languages = list(voices.keys())
        
        print("  Available languages:")
        for i, lang in enumerate(languages, 1):
            print(f"    {i}. {lang}")
        
        try:
            lang_idx = int(input("\n  Select language (or press ENTER to cancel): ") or "-1") - 1
            if lang_idx < 0 or lang_idx >= len(languages):
                print("  Cancelled.")
                return
            
            selected_lang = languages[lang_idx]
            available_voices = voices[selected_lang]
            
            print(f"\n  Voices for {selected_lang}:")
            voice_list = list(available_voices.keys())
            for i, voice in enumerate(voice_list, 1):
                print(f"    {i}. {voice}")
            
            voice_idx = int(input(f"\n  Select voice: ") or "-1") - 1
            if voice_idx < 0 or voice_idx >= len(voice_list):
                print("  Cancelled.")
                return
            
            selected_voice = voice_list[voice_idx]
            
            if self.config_manager.set_tts_voice(selected_lang, selected_voice):
                CLIHelper.print_success(f"Voice changed to: {selected_lang}/{selected_voice}")
                
                # Also change STT language
                stt_langs = self.config_manager.get_available_stt_languages()
                lang_code = selected_lang.split('_')[0]  # Extract language code (en from en_US)
                if lang_code in stt_langs:
                    self.config_manager.set_stt_language(lang_code)
                    CLIHelper.print_success(f"STT language changed to: {lang_code}")
            else:
                CLIHelper.print_error("Failed to change voice.")
                
        except ValueError:
            CLIHelper.print_error("Invalid input.")
    
    def _view_config(self) -> None:
        """Display current configuration."""
        CLIHelper.print_section("Current Configuration")
        
        config = self.config_manager.get_config()
        
        print(f"  LLM Model: {config.llm_model}")
        print(f"  Voice: {config.tts_voice.language_code} - {config.tts_voice.voice_name}")
        print(f"  STT Language: {config.stt_language.language_code}")
        print(f"  Record Duration: {config.record_seconds} seconds")
        print(f"  System Prompt: {config.system_prompt}")
        
        
        print("\n  Ollama Status:")
        if self.model_manager.is_ollama_running():
            print("    ✓ Ollama is running")
            available = self.model_manager.get_available_models()
            print(f"    Available models: {len(available)}")
        else:
            print("    ✗ Ollama is not running")
    
    def _show_status(self) -> None:
        """Show application status."""
        CLIHelper.print_section("Application Status")
        
        # Check each component
        print("  Component Status:")
        
        # Ollama
        ollama_ok = self.model_manager.is_ollama_running()
        print(f"    {'✓' if ollama_ok else '✗'} Ollama Server: {'Running' if ollama_ok else 'Not running'}")
        
        # LLM Model
        config = self.config_manager.get_config()
        model_ok = self.model_manager.model_exists(config.llm_model)
        print(f"    {'✓' if model_ok else '✗'} LLM Model: {config.llm_model}")
        
        # STT
        print(f"    ✓ STT: {config.stt_language.language_code}")
        
        # TTS
        print(f"    ✓ TTS: {config.tts_voice.language_code}")
        
        # Recording/Playback tools
        arecord_ok = self._check_command("arecord")
        print(f"    {'✓' if arecord_ok else '✗'} Recording Tool (arecord)")
        
        ffplay_ok = self._check_command("ffplay")
        print(f"    {'✓' if ffplay_ok else '✗'} Playback Tool (ffplay)")
        
        piper_ok = self._check_command("piper")
        print(f"    {'✓' if piper_ok else '✗'} Text-to-Speech (piper)")
    
    @staticmethod
    def _check_command(command: str) -> bool:
        """Check if a command is available."""
        try:
            result = subprocess.run(
                ["which", command],
                capture_output=True,
                timeout=2
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def run(self) -> None:
        """Start the application."""
        logger.info("English Tutor Offline starting...")
        self.is_running = True
        
        try:
            self._show_main_menu()
        except KeyboardInterrupt:
            print("\n\n  Application interrupted by user.")
        except Exception as e:
            logger.error(f"Fatal error: {e}", exc_info=True)
            CLIHelper.print_error(f"Fatal error: {e}")
        finally:
            self.shutdown()
    
    def shutdown(self) -> None:
        """Shutdown the application."""
        logger.info("English Tutor Offline shutting down...")
        self.is_running = False
        
        # Clean up
        self.conversation.clear_history()
        
        # Note: We don't stop Ollama as it may be needed by other applications
        logger.info("Shutdown complete.")


def orchest() -> None:
    """Main entry point for the orchestrator."""
    orchestrator = ApplicationOrchestrator()
    orchestrator.run()