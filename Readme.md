# English Tutor Offline

An offline-first conversational English tutor powered by local AI models with a user-friendly CLI interface.

The application allows you to practice spoken English directly from your microphone. Your speech is transcribed locally, sent to a local language model for conversation and corrections, and the response is synthesized back into speech.

## 🎯 Features

### Core Functionality

- ✅ **Speech-to-Text**: Whisper.cpp for accurate audio transcription
- ✅ **AI Tutoring**: Local LLMs via Ollama with grammar correction
- ✅ **Text-to-Speech**: Piper for natural voice synthesis
- ✅ **Continuous Conversations**: Full voice conversation loop
- ✅ **No Cloud Services**: Completely offline and self-hosted

### Advanced Features

- 🎚️ **Interactive CLI Menu**: Easy navigation with visual menus
- 🌍 **Multi-Language Support**: English, German, French, and more
- 📦 **Model Management**: Download and switch between LLM models
- 🎤 **Voice Selection**: Choose different voice models and languages
- 💾 **Configuration Persistence**: Settings saved between sessions
- 🔄 **Error Recovery**: Automatic retries with detailed error handling
- 📊 **Application Status**: Check component health anytime
- 📝 **Comprehensive Logging**: Full audit trail for debugging

## 🏗️ Architecture

```text
Microphone
    ↓
Audio Recording (arecord)
    ↓
Speech-to-Text (Whisper.cpp)
    ↓
Transcribed Text
    ↓
LLM Processing (Ollama + Llama/Mistral/etc)
    ↓
Tutor Response
    ↓
Text-to-Speech (Piper)
    ↓
Audio Synthesis
    ↓
Audio Playback (ffplay)
    ↓
Speaker
```

## 📋 Project Structure

```text
English-Tutor-Offline/
├── main.py                    # Application entry point
├── orchestrator.py            # Main application coordinator
├── cli.py                     # Interactive menu system
├── config.py                  # Configuration management
├── model_manager.py           # Model and voice management
│
├── stt.py                     # Speech-to-Text module (Whisper)
├── chat.py                    # LLM chat interface
├── tts.py                     # Text-to-Speech module (Piper)
├── llm_server.py              # Ollama server management
│
├── data/
│   ├── config.json            # Application configuration
│   ├── tutor.log              # Application logs
│   ├── input.wav              # Recorded user audio
│   └── output.wav             # Synthesized response audio
│
├── DOCUMENTATION.md           # Complete documentation
├── Readme.md                  # This file
└── requirements.txt           # Python dependencies
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Ollama (with at least one model)
- Whisper.cpp (pre-built in project)
- Piper TTS
- `arecord` (alsa-utils)
- `ffplay` (ffmpeg)

### Installation

```bash
# 1. Navigate to project
cd English-Tutor-Offline

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Ensure Ollama is running
ollama serve &

# 4. Start the application
python3 main.py
```

### First Use

1. Start the application
2. Select "Status" to verify all components
3. Select "Start Talking" to begin your first conversation
4. (Optional) Use "Options" to change models or languages

## 📚 Usage Guide

### Main Menu

```
============================================================
  English Tutor Offline
  Main Menu
============================================================

  [1] Start Talking
  [2] Options
  [3] Status
  [Q] Quit Application
```

### Option 1: Start Talking

- Begin an interactive conversation session
- Speak when prompted, listen to responses
- Tutor corrects grammar and asks follow-up questions
- Continue or exit after each turn

### Option 2: Options

- **Change LLM Model**: Switch between available AI models
- **Download New Model**: Download models from Ollama registry
- **Change Voice & Language**: Select different voice and language
- **View Configuration**: See current settings

### Option 3: Status

- View health of all components
- Check if Ollama, Whisper, Piper are properly configured
- Verify microphone and speaker access

## 🔧 Configuration

Configuration is automatically saved to `data/config.json`:

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

### Supported Languages

**Text-to-Speech**:

- English (en_US) - lessac-high
- German (de_DE) - thorsten-medium

**Speech-to-Text**:

- English (en)
- German (de)
- French (fr)
- and more supported by Whisper

## 📖 Documentation

For comprehensive documentation including:

- Detailed module explanations
- Error handling strategies
- Troubleshooting guide
- Advanced configuration
- Performance tips

See [DOCUMENTATION.md](DOCUMENTATION.md)

## 🔒 Error Handling & Recovery

The application features robust error handling:

- **Automatic Retries**: Failed operations retry with exponential backoff
- **Detailed Error Messages**: Clear feedback on what went wrong
- **Graceful Degradation**: Continues despite component failures
- **Comprehensive Logging**: Full audit trail in `data/tutor.log`
- **User Recovery Options**: Choose to retry or continue after errors

## 🛠️ Troubleshooting

### Application won't start

```bash
# Check logs
tail -50 data/tutor.log

# Verify Python version
python3 --version  # Should be 3.8+

# Install dependencies
pip install -r requirements.txt
```

### No sound output

```bash
# Check audio devices
aplay --list-devices

# Test recording
arecord -t wav -c 2 -r 44100 test.wav
ffplay test.wav
```

### Poor transcription

- Speak clearly and at normal pace
- Reduce background noise
- Use shorter recordings
- Try a different microphone

### Slow responses

- Check Ollama status: `ollama list`
- Try a smaller model
- Check system resources: `top`
- Restart Ollama: `pkill -f "ollama serve"`

For more troubleshooting, see [DOCUMENTATION.md](DOCUMENTATION.md#troubleshooting)

## 📦 Requirements

See `requirements.txt` for Python packages:

- ollama
- (piper-tts if not installed system-wide)

### System Requirements

- **Minimum**: 4GB RAM, 10GB storage
- **Recommended**: 8GB+ RAM, 30GB storage (for multiple models)
- **GPU**: Optional but recommended for better performance

## 💡 Tips for Best Results

1. **Speak Clearly**: Enunciate words carefully
2. **Use Complete Sentences**: Better for AI processing
3. **Reduce Background Noise**: Find a quiet location
4. **Check System Resources**: Close other applications
5. **Use Recommended Models**: They're optimized for English tutoring
6. **Shorter Recordings**: 3-5 sentences is ideal

## 🎓 How to Practice Effectively

1. **Start with Simple Topics**: Build confidence gradually
2. **Ask Questions**: The tutor responds to your questions
3. **Let Tutor Correct You**: Grammar corrections are valuable
4. **Follow Up Questions**: Tutor provides context for practice
5. **Multiple Sessions**: Consistent practice improves results

## ⚙️ Performance Optimization

- **Enable GPU Acceleration**: Ollama and Whisper support GPU
- **Use Smaller Models**: Faster response times
- **Reduce Recording Duration**: Faster processing
- **Install on SSD**: Better I/O performance
- **Close Background Apps**: Free up system resources

## 🤝 Contributing

Contributions are welcome! Please:

1. Test thoroughly
2. Document changes
3. Maintain error handling standards
4. Update logs appropriately

## 📄 License

See LICENSE file for details

## 🙏 Credits

Built with:

- [Whisper.cpp](https://github.com/ggerganov/whisper.cpp) - Speech recognition
- [Ollama](https://ollama.ai) - LLM inference
- [Piper](https://github.com/rhasspy/piper) - Text-to-speech
- [Llama](https://www.llama.com/) - Language model

## 📞 Support

For issues or feature requests:

1. Check [DOCUMENTATION.md](DOCUMENTATION.md)
2. Review logs: `data/tutor.log`
3. Test each component individually
4. Provide system info when reporting issues

---

**Happy learning! 🎉**
│
├── data/
│ ├── input.wav
│ └── output.wav
│
├── requirements.txt
└── README.md

````

## Requirements

### Python

- Python 3.10 or newer

### Python Dependencies

Install:

```bash
pip install -r requirements.txt
````

### System Dependencies

The following tools must be available on your system:

- Ollama
- Whisper.cpp
- Piper
- FFmpeg (for audio playback)
- ALSA or PipeWire audio stack

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd English-Tutor
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Ollama

Install Ollama following the official instructions for your operating system.

Pull a model:

```bash
ollama pull llama3.1
```

### 5. Install Whisper.cpp

Clone and build Whisper.cpp:

```bash
git clone https://github.com/ggml-org/whisper.cpp.git

cd whisper.cpp

cmake -B build -DBUILD_SHARED_LIBS=OFF
cmake --build build -j
```

Download an English model and place it in:

```text
whisper.cpp/models/
```

Example:

```text
ggml-base.en.bin
```

### 6. Install Piper

Create a virtual environment at projects's root and install piper there:

```text
pip install piper-tts
```

(This is where the executable route refers to, you can change it if you want)

Create a piper folder at project's root and...

Create a voices directory:

```text
piper/
└── voices/
```

Download a voice model such as:

```text
en_US-lessac-high.onnx
en_US-lessac-high.onnx.json
```

and place both files inside `piper/voices`.

## Running

Start Ollama:

```bash
ollama serve
```

Run the application:

```bash
python main.py
```

Press ENTER when prompted and start speaking.

## Example

User:

```text
Yesterday I go to school.
```

Tutor:

```text
You should say "Yesterday I went to school."

What did you do at school?
```

The response will be spoken aloud through Piper.

## Future Improvements

- Voice activity detection (VAD)
- Automatic silence detection
- Conversation memory
- Vocabulary training mode
- Pronunciation assessment
- IELTS/TOEFL practice modes
- Streaming transcription
- Streaming speech synthesis

## License

This project combines several open-source projects:

- Whisper.cpp
- Ollama
- Piper

Please consult each project's license for details.
