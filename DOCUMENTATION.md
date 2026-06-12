# English Tutor Offline - Complete Documentation

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Architecture](#architecture)
4. [Installation & Setup](#installation--setup)
5. [Usage Guide](#usage-guide)
6. [Module Documentation](#module-documentation)
7. [Configuration](#configuration)
8. [Error Handling](#error-handling)
9. [Troubleshooting](#troubleshooting)

---

## Overview

English Tutor Offline is a comprehensive AI-powered English learning application that operates completely offline. It combines:

- **Speech Recognition**: Whisper.cpp for converting user speech to text
- **AI Tutoring**: Ollama running local LLMs for intelligent responses
- **Text-to-Speech**: Piper for converting tutor responses back to speech

The application provides a full conversation loop where users can practice English with an AI tutor that:

- Listens to user input
- Processes and responds with AI-generated text
- Plays back responses as audio

All processing happens locally with no internet connection required after initial setup.

---

## Features

### 1. Interactive CLI Menu System

- **Start Talking**: Begin a conversation session
- **Options Menu**: Configure models, languages, and download new models
- **Status Display**: Check application and component status
- **Graceful Exit**: Proper shutdown with resource cleanup

### 2. Multi-Language Support

- **Whisper.cpp Support**: English (en), German (de), French (fr), and others
- **Piper TTS Voices**: Multiple languages with high-quality voice models
- **Language Switching**: Change languages on-the-fly from the Options menu

### 3. Model Management

- **LLM Models**: Download and switch between different Ollama models
- **Model Availability**: Check which models are currently available
- **Model Testing**: Built-in functionality to test models
- **Automatic Model Detection**: Lists available models from Ollama

### 4. Robust Error Recovery

- **Automatic Retries**: Failed operations retry with exponential backoff
- **Detailed Error Messages**: Clear feedback on what went wrong
- **Graceful Degradation**: Application continues despite component failures
- **Comprehensive Logging**: Full audit trail in `data/tutor.log`

### 5. Configuration Persistence

- **Settings Saved**: All settings persist between sessions
- **Easy Reconfiguration**: Change settings anytime from Options menu
- **Default Values**: Sensible defaults for first-time users

---

## Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Main Application                         │
│                      (main.py)                              │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Application Orchestrator                        │
│           (orchestrator.py)                                 │
│  • Coordinates pipeline                                     │
│  • Manages conversations                                    │
│  • Handles menu navigation                                  │
└──┬──────────┬───────────┬────────────────┬─────────────────┘
   │          │           │                │
   ▼          ▼           ▼                ▼
┌────────┐ ┌───────┐ ┌─────────┐ ┌──────────────┐
│  CLI   │ │Config │ │  Audio  │ │  Conversation│
│ Menu   │ │Manager│ │ Handler │ │  Manager     │
│(cli.py)│ │ (.py) │ │  (.py)  │ │   (.py)      │
└────────┘ └───────┘ └─────────┘ └──────────────┘
   │          │           │
   └─────┬────┘           │
         │                │
         ▼                ▼
    ┌──────────┐   ┌─────────────────┐
    │  Model   │   │  Pipeline       │
    │ Manager  │   │  Components     │
    │          │   │                 │
    └──────────┘   ├─ STT (stt.py)   │
                   ├─ Chat (chat.py) │
                   ├─ TTS (tts.py)   │
                   └─ LLM (llm_..)   │
                      └─────────────┘
```

### Data Flow for Conversation

```
User Speech
    │
    ▼
┌──────────────────┐
│  Audio Recording │ (arecord)
│  Input: Microphone
│  Output: WAV file
└────────┬─────────┘
         │
         ▼
┌──────────────────────────┐
│  Speech-to-Text (STT)    │ (stt.py)
│  Input: WAV file
│  Output: Text string
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│  LLM Processing          │ (chat.py, llm_server.py)
│  Input: User text + history
│  Output: LLM response
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│  Text-to-Speech (TTS)    │ (tts.py)
│  Input: Response text
│  Output: WAV file
└────────┬─────────────────┘
         │
         ▼
┌──────────────────┐
│  Audio Playback  │ (ffplay)
│  Input: WAV file
│  Output: Speaker
└──────────────────┘
```

---

## Installation & Setup

### Prerequisites

Before running the application, ensure you have:

1. **Python 3.8+**: For running the application
2. **Ollama**: For LLM inference
3. **Whisper.cpp**: For speech recognition (typically pre-built)
4. **Piper**: For text-to-speech
5. **System Tools**:
   - `arecord` (alsa-utils) - for audio recording
   - `ffplay` (ffmpeg) - for audio playback

### Quick Start

```bash
# Clone or navigate to the project
cd /path/to/English-Tutor-Offline

# Install Python dependencies
pip install -r requirements.txt

# Start the application
python3 main.py
```

### Detailed Setup

#### 1. Install Ollama

```bash
# Download from ollama.ai
# https://ollama.ai

# Or on Linux:
curl https://ollama.ai/install.sh | sh

# Pull a model:
ollama pull llama3.1
```

#### 2. Setup Whisper.cpp (if not already built)

```bash
cd whisper.cpp
mkdir -p build
cd build
cmake ..
make -j$(nproc)
cd ..

# Download a model:
bash ./models/download-ggml-model.sh base.en
```

#### 3. Install Piper

```bash
pip install piper-tts
```

#### 4. Install System Tools (Ubuntu/Debian)

```bash
sudo apt-get install alsa-utils ffmpeg
```

#### 5. Run Application

```bash
python3 main.py
```

---

## Usage Guide

### Main Menu

When you start the application, you'll see the main menu:

```
============================================================
  English Tutor Offline
  Main Menu
============================================================

  [1] Start Talking
  [2] Options
  [3] Status
  [Q] Quit Application

------------------------------------------------------------
  Select option:
```

### Option 1: Start Talking

This begins an interactive conversation session:

1. **Recording**: Press ENTER, then speak for up to 5 seconds
2. **Processing**: The application transcribes your speech and sends it to the AI
3. **Response**: The tutor responds with corrected English
4. **Audio Playback**: You hear the tutor's response
5. **Loop**: Continue or exit

**Tips**:

- Speak clearly and at a normal pace
- Complete sentences are better than fragments
- The AI tutor corrects grammar and asks follow-up questions

### Option 2: Options Menu

#### Change LLM Model

- View available models in Ollama
- Select a different model for the tutor
- Changes take effect immediately

#### Download New Model

- Browse recommended and other available models
- See estimated download sizes
- Download models from Ollama's registry
- Note: Download can take 5-30 minutes depending on model size

#### Change Voice & Language

- Select a language (English, German, etc.)
- Choose a voice variant for that language
- STT (speech recognition) language automatically updates
- TTS (text-to-speech) updates to match

#### View Configuration

- See current settings:
  - Active LLM model
  - Active voice and language
  - STT language
  - Recording duration

### Option 3: Status

Shows the health of all components:

```
============================================================
  Application Status
============================================================

  Component Status:
    ✓ Ollama Server: Running
    ✓ LLM Model: llama3.1:latest
    ✓ STT: en
    ✓ TTS: en_US
    ✓ Recording Tool (arecord)
    ✓ Playback Tool (ffplay)
    ✓ Text-to-Speech (piper)
```

A ✗ indicates a component that may need attention.

---

## Module Documentation

### 1. **main.py** - Application Entry Point

**Purpose**: Entry point for the entire application

**Key Functions**:

```python
def main():
    """Main application entry point."""
```

**Responsibilities**:

- Initialize logging
- Handle import errors
- Catch fatal exceptions
- Provide graceful shutdown

**Error Handling**:

- Catches import errors and provides helpful messages
- Logs all exceptions to `data/tutor.log`

---

### 2. **orchestrator.py** - Central Coordinator

**Purpose**: Orchestrates the entire application flow and component interactions

**Key Classes**:

#### `AudioHandler`

Manages audio recording and playback

```python
class AudioHandler:
    @staticmethod
    def record_audio(output_path: Path, duration: int) -> None:
        """Record audio from microphone"""

    @staticmethod
    def play_audio(audio_path: Path, max_retries: int = 2) -> None:
        """Play audio file with retry logic"""
```

**Error Handling**:

- Validates output directory
- Checks file sizes
- Retry on temporary failures
- Clear error messages

#### `ConversationManager`

Maintains conversation history

```python
class ConversationManager:
    def add_turn(self, user_text: str, llm_response: str) -> None:
        """Add a turn to conversation"""

    def get_history(self) -> List[dict]:
        """Get history for LLM context"""
```

#### `ApplicationOrchestrator`

Main coordinator class

```python
class ApplicationOrchestrator:
    def _run_conversation(self) -> None:
        """Main conversation loop"""

    def _show_main_menu(self) -> None:
        """Display and handle main menu"""
```

**Key Methods**:

- `_ensure_ollama_running()`: Starts Ollama if not running
- `_run_conversation()`: Main conversation loop with full pipeline
- `_change_llm_model()`: Model selection interface
- `_download_model()`: Model download interface
- `_change_voice()`: Voice and language selection
- `_show_status()`: System component status

**Error Handling**:

- Validates Ollama availability before starting
- Checks model existence
- Retries failed operations
- Catches and displays specific error messages
- Offers users choice to retry or continue

---

### 3. **config.py** - Configuration Management

**Purpose**: Manages application settings with persistence

**Key Classes**:

#### `AppConfig` (dataclass)

```python
@dataclass
class AppConfig:
    llm_model: str = "llama3.1:latest"
    tts_voice: TTSVoiceConfig
    stt_language: STTModelConfig
    record_seconds: int = 5
```

#### `ConfigManager`

Main configuration handler

```python
class ConfigManager:
    def __init__(self):
        """Initialize and load config"""

    def set_llm_model(self, model_name: str) -> None:
        """Change LLM model"""

    def set_tts_voice(self, language: str, voice: str) -> bool:
        """Change TTS voice"""

    def set_stt_language(self, language: str) -> bool:
        """Change STT language"""
```

**Features**:

- JSON-based persistence in `data/config.json`
- Type-safe dataclass configuration
- Validation of all settings
- Default values for first-time use
- Automatic file creation and directory setup

**Error Handling**:

- Handles missing config files
- Recovers from corrupted JSON
- Validates language/voice availability
- Checks model file existence

---

### 4. **model_manager.py** - Model Management

**Purpose**: Handles LLM model and voice model management

**Key Classes**:

#### `ModelManager`

LLM model management

```python
class ModelManager:
    def is_ollama_running(self) -> bool:
        """Check if Ollama is running"""

    def get_available_models(self) -> List[str]:
        """List available models"""

    def model_exists(self, model_name: str) -> bool:
        """Check if model is available"""

    def download_model(self, model_name: str) -> bool:
        """Download a model from registry"""
```

**Model Lists**:

- **Recommended Models**: Vetted models for English tutoring
- **Searchable Models**: Can be downloaded from Ollama

**Features**:

- Connection pooling for Ollama
- Model existence verification
- Download with progress tracking
- Model size estimation
- Model validation via test inference

#### `VoiceModelManager`

Voice model validation

```python
class VoiceModelManager:
    @staticmethod
    def check_voice_model(model_path) -> bool:
        """Validate voice model file"""
```

**Error Handling**:

- Detects connection failures
- Handles HTTP errors gracefully
- Validates model names
- Checks file integrity
- Provides size warnings for unusual models

---

### 5. **cli.py** - Interactive Menu System

**Purpose**: Provides interactive CLI with menu navigation

**Key Classes**:

#### `Menu`

Interactive menu display and navigation

```python
class Menu:
    def __init__(self, title: str, subtitle: str = ""):
        """Initialize menu"""

    def add_option(self, key: str, label: str, action: Callable) -> None:
        """Add menu option"""

    def run(self) -> None:
        """Run menu loop"""
```

#### `CLIHelper`

Utility functions for CLI display

```python
class CLIHelper:
    @staticmethod
    def print_success(message: str) -> None
    @staticmethod
    def print_error(message: str) -> None
    @staticmethod
    def print_warning(message: str) -> None
    @staticmethod
    def print_info(message: str) -> None
    @staticmethod
    def get_yes_no(prompt: str) -> bool
    @staticmethod
    def get_choice(prompt: str, choices: List[str]) -> str
```

**Features**:

- Keyboard interrupt handling
- Input validation
- Visual hierarchy with sections
- Consistent error/success messaging
- Menu history/back button support

**Error Handling**:

- Catches KeyboardInterrupt (Ctrl+C)
- Handles invalid input gracefully
- Retries on errors
- Clear error messages

---

### 6. **stt.py** - Speech-to-Text Module

**Purpose**: Transcribe audio to text using Whisper.cpp

**Key Functions**:

```python
def transcribe(
    audio_path: str,
    language: str = "en",
    retry_count: int = 1
) -> str:
    """Transcribe audio file to text"""
```

**Custom Exceptions**:

- `STTError`: Base exception
- `STTConfigError`: Configuration errors
- `STTTranscriptionError`: Transcription failures

**Validation**:

- Prerequisite checking (CLI, libraries, models)
- Audio file validation
- Model file availability
- Output file verification

**Features**:

- Multi-language support
- Automatic retry with backoff
- Detailed error messages
- Timeout protection (120 seconds)
- Library path setup for Linux

**Error Handling**:

- Missing files → STTConfigError
- Invalid audio → STTError
- Process failure → STTTranscriptionError
- Timeout → STTTranscriptionError
- Retries after delays

---

### 7. **tts.py** - Text-to-Speech Module

**Purpose**: Synthesize text to speech using Piper

**Key Functions**:

```python
def speak(
    text: str,
    output_wav: str,
    voice_model_path: Optional[Path] = None,
    retry_count: int = 1
) -> None:
    """Synthesize text to speech"""
```

**Custom Exceptions**:

- `TTSError`: Base exception
- `TTSConfigError`: Configuration errors
- `TTSSynthesisError`: Synthesis failures

**Validation**:

- Voice model file existence
- Output directory writability
- Input text validation
- Output file integrity

**Features**:

- Multi-language voice support
- Automatic Python executable detection
- Retry mechanism with backoff
- Timeout protection (120 seconds)
- Output file size validation

**Error Handling**:

- Missing model → TTSConfigError
- Non-writable directory → TTSError
- Synthesis failure → TTSSynthesisError
- Timeout → TTSSynthesisError
- Retries after delays

---

### 8. **chat.py** - LLM Chat Interface

**Purpose**: Interface with LLM for tutoring responses

**Key Functions**:

```python
def ask_llm(user_text: str, history=None) -> str:
    """Get LLM response"""
```

**System Prompt**:

```
You are an English tutor.
Speak only English.
Keep responses short.
Ask a follow-up question.
```

**Features**:

- Conversation history support
- Automatic grammar correction
- Engaging follow-up questions

---

### 9. **llm_server.py** - Ollama Management

**Purpose**: Manage Ollama server and model interactions

**Key Functions**:

```python
def check_ollama_server() -> bool:
    """Check if Ollama is running"""

def run_ollama() -> Popen|None:
    """Start Ollama if not running"""

def get_ollama_client() -> Client:
    """Get Ollama client"""

def download_model(client: Client, model_name: str):
    """Download model"""
```

**Error Handling**:

- Connection failure detection
- Server startup verification
- Model availability checking

---

## Configuration

### Configuration File Location

Configuration is stored in: `data/config.json`

### Example Configuration

```json
{
  "llm_model": "llama3.1:latest",
  "tts_voice": {
    "language_code": "en_US",
    "voice_name": "lessac-high",
    "model_path": "piper/voices/en_US-lessac-high.onnx"
  },
  "stt_language": {
    "language_code": "en",
    "model_name": "base.en"
  },
  "record_seconds": 5
}
```

### Configuration Options

| Setting                      | Type    | Default           | Description        |
| ---------------------------- | ------- | ----------------- | ------------------ |
| `llm_model`                  | string  | "llama3.1:latest" | Active LLM model   |
| `tts_voice.language_code`    | string  | "en_US"           | TTS language code  |
| `tts_voice.voice_name`       | string  | "lessac-high"     | Voice variant      |
| `stt_language.language_code` | string  | "en"              | STT language code  |
| `record_seconds`             | integer | 5                 | Recording duration |

### Supported Languages

**TTS Voices**:

- English (en_US): lessac-high
- German (de_DE): thorsten-medium

**STT Languages**:

- English (en): base.en
- German (de): base.de
- French (fr): base.fr
- (and more supported by Whisper)

---

## Error Handling

### Error Recovery Strategy

The application uses a multi-layered error handling approach:

#### Layer 1: Validation

Checks prerequisites before operations:

```python
def _validate_prerequisites() -> bool:
    # Check files exist
    # Check directories accessible
    # Check dependencies available
```

#### Layer 2: Try-Catch with Retry

Attempts operation with exponential backoff:

```python
for attempt in range(1, retry_count + 1):
    try:
        # Perform operation
        return result
    except SpecificError as e:
        if attempt < retry_count:
            time.sleep(2 ** (attempt - 1))  # Exponential backoff
            continue
        raise
```

#### Layer 3: User Feedback

Clear error messages and options:

```python
except RecordingError as e:
    CLIHelper.print_error(f"Recording failed: {e}")
    if CLIHelper.get_yes_no("Try again?"):
        continue
    else:
        break
```

#### Layer 4: Logging

Detailed audit trail:

```python
logger.error(f"Component failed: {e}", exc_info=True)
```

### Common Errors and Solutions

| Error                       | Cause                      | Solution                               |
| --------------------------- | -------------------------- | -------------------------------------- |
| "Ollama server not running" | Ollama service not started | Start Ollama: `ollama serve`           |
| "Model not found"           | Model not downloaded       | Download from Options menu             |
| "arecord not found"         | Recording tool missing     | `sudo apt install alsa-utils`          |
| "ffplay not found"          | Playback tool missing      | `sudo apt install ffmpeg`              |
| "Transcription timeout"     | Whisper taking too long    | Check audio quality, try shorter clips |
| "Permission denied"         | Directory not writable     | Check data/ directory permissions      |

---

## Troubleshooting

### Application Won't Start

1. **Check Python version**:

   ```bash
   python3 --version  # Should be 3.8+
   ```

2. **Check dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Check logs**:
   ```bash
   cat data/tutor.log
   ```

### No Sound Output

1. **Check audio device**:

   ```bash
   aplay --list-devices
   ffplay -h  # Check audio options
   ```

2. **Test recording**:

   ```bash
   arecord -t wav -c 2 -r 44100 test.wav
   ffplay test.wav
   ```

3. **Check permissions**:
   ```bash
   ls -la /dev/snd/
   # Should be readable/writable
   ```

### Poor Transcription

1. **Try shorter recordings**: Break long sentences into shorter phrases
2. **Speak clearly**: Enunciate words carefully
3. **Reduce background noise**: Find a quiet location
4. **Check microphone**: Test recording with `arecord test.wav`

### Slow Response

1. **Check Ollama status**:

   ```bash
   ollama list  # See loaded models
   ```

2. **Try smaller model**: Some models are faster
3. **Check system resources**: `top` or `htop`
4. **Check network**: Ensure no internet interruptions

### Memory Issues

1. **Close other applications**: Free up RAM
2. **Use smaller models**: e.g., "neural-chat" instead of "wizard-math"
3. **Check swap**: `free -h`

### Model Download Fails

1. **Check internet connection**: Download needs stable connection
2. **Check Ollama**: Ensure `ollama serve` is running
3. **Try different model**: Some models may be temporarily unavailable
4. **Check disk space**: Models can be 3-13 GB

### File Permission Errors

1. **Check directory**:

   ```bash
   ls -la data/
   ```

2. **Fix permissions**:
   ```bash
   chmod 755 data/
   chmod 644 data/config.json
   ```

### Still Having Issues?

1. **Check the log file**:

   ```bash
   tail -100 data/tutor.log
   ```

2. **Provide feedback**: Include logs when reporting issues

3. **Verify prerequisites**: Run `python3 main.py` and check status

---

## Advanced Configuration

### Changing Recording Duration

Edit `data/config.json`:

```json
{
  "record_seconds": 10
}
```

Higher values give more time to speak but delay processing.

### Adding Custom Models

1. Download model using Ollama:

   ```bash
   ollama pull mistral
   ```

2. It will automatically appear in the Options menu

### Adding Custom Voices

1. Download voice model to `piper/voices/`
2. Update `config.py` `AVAILABLE_VOICES` dictionary
3. Restart application

---

## Performance Tips

1. **Use GPU**: Ollama and Whisper benefit from GPU acceleration
2. **Choose faster models**: Smaller models respond faster
3. **Reduce record duration**: Shorter audio processes faster
4. **Close background apps**: Free up system resources
5. **Use SSD**: Faster disk I/O helps

---

## Security Considerations

1. **Local Processing**: All data stays on your machine
2. **No Network**: Application works completely offline (after setup)
3. **Configuration File**: Contains only settings, no sensitive data
4. **Logs**: May contain transcribed text, stored in `data/tutor.log`

---

## Support & Contribution

For issues, feature requests, or contributions:

1. Check existing issues
2. Provide detailed error logs
3. Describe steps to reproduce
4. Mention system specifications

---

## License & Credits

See README.md for license information.

---

## FAQ

**Q: Can I use this without Ollama?**
A: No, Ollama provides the LLM responses. It's a required component.

**Q: Can I use this without a microphone?**
A: No, speech input is core to the application. You need a working microphone.

**Q: How much storage do I need?**
A: Minimum 10GB (models + application). Recommended 30GB for multiple models.

**Q: How much RAM do I need?**
A: Minimum 4GB. Recommended 8GB+ for better performance.

**Q: Can I run multiple conversations?**
A: Currently no, but each session starts fresh with configurable history length.

**Q: Is the transcription always correct?**
A: Whisper is very accurate but not perfect. Speak clearly for best results.

**Q: Can I use this on Windows/Mac?**
A: Yes, with modifications to use native audio tools instead of arecord/ffplay.

---

## Changelog

### Version 1.1.0

- Documentation updated
- Initial release
- Full CLI menu system
- Multi-language support
- Model management
- Configuration persistence
- Comprehensive error handling
- Complete documentation

---

_Last Updated: 2026_
_Documentation Version: 1.1_
