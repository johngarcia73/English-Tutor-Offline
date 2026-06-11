# Quick Start Guide - English Tutor Offline

## What's New

This implementation adds a complete CLI frontend to your English Tutor project with:

✅ **Interactive Menu System** - Professional CLI with easy navigation  
✅ **Configuration Management** - Persistent settings between sessions  
✅ **Model Management** - Download and switch LLM models easily  
✅ **Error Recovery** - Robust error handling with automatic retries  
✅ **Comprehensive Documentation** - Detailed explanations of every feature

## Files Added/Modified

### New Files Created

- **cli.py** - Interactive menu system with menu navigation
- **config.py** - Configuration management with JSON persistence
- **model_manager.py** - LLM and voice model management utilities
- **DOCUMENTATION.md** - 400+ line comprehensive documentation

### Files Enhanced

- **main.py** - Better error handling and initialization
- **orchestrator.py** - Complete rewrite with menu system and error recovery
- **stt.py** - Enhanced with error handling and retries
- **tts.py** - Enhanced with error handling and retries
- **Readme.md** - Updated with new features

## Quick Start (5 minutes)

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Start Ollama (if not running)

```bash
ollama serve &
```

### Step 3: Run the Application

```bash
python3 main.py
```

### Step 4: Choose an Option

```
  [1] Start Talking          ← Practice with the AI tutor
  [2] Options                ← Change model/voice/language
  [3] Status                 ← Check system health
  [Q] Quit Application       ← Exit
```

## Main Features

### 1. Start Talking (Option 1)

```
- Press ENTER to record (5 seconds default)
- Speak your English naturally
- AI tutor responds with corrections
- Response plays back as audio
- Continue or exit
```

### 2. Options Menu (Option 2)

#### Change LLM Model

- View available models (llama3.1, mistral, etc.)
- Select different model instantly
- Changes take effect immediately

#### Download New Model

- Browse recommended models with sizes
- Download models from Ollama
- See estimated download time

#### Change Voice & Language

- Select language (English, German, etc.)
- Choose voice for that language
- STT (speech recognition) auto-updates

#### View Configuration

- See current model, voice, language
- See all active settings

### 3. Status (Option 3)

Check health of all components:

```
✓ Ollama Server: Running
✓ LLM Model: llama3.1:latest
✓ STT: en
✓ TTS: en_US
✓ Recording Tool (arecord)
✓ Playback Tool (ffplay)
✓ Text-to-Speech (piper)
```

## Error Handling

The application handles all errors gracefully:

- **Recording Failed?** → Offers to retry
- **Model Not Downloaded?** → Shows download option
- **Ollama Down?** → Attempts auto-restart
- **Audio Playback Issue?** → Tries alternative tools
- **Unexpected Error?** → Logs and offers recovery

## Configuration

Settings are automatically saved to `data/config.json`:

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

Your preferences are remembered between sessions!

## Logging

All activities are logged to `data/tutor.log`:

```bash
# View recent logs
tail -50 data/tutor.log

# View all logs
cat data/tutor.log
```

## Troubleshooting

### Application Won't Start

```bash
# Check Python version
python3 --version  # Should be 3.8+

# Check dependencies
pip install -r requirements.txt

# Check logs
tail data/tutor.log
```

### No Sound

```bash
# Test audio
arecord -t wav -c 2 -r 44100 test.wav
ffplay test.wav
```

### Poor Transcription

- Speak clearly
- Reduce background noise
- Use shorter sentences
- Check microphone quality

For more troubleshooting, see [DOCUMENTATION.md](DOCUMENTATION.md)

## Module Overview

| Module               | Purpose                    |
| -------------------- | -------------------------- |
| **main.py**          | Application entry point    |
| **orchestrator.py**  | Coordinates all components |
| **cli.py**           | Interactive menu system    |
| **config.py**        | Settings management        |
| **model_manager.py** | Model & voice management   |
| **stt.py**           | Speech → Text (Whisper)    |
| **chat.py**          | LLM interaction            |
| **tts.py**           | Text → Speech (Piper)      |
| **llm_server.py**    | Ollama management          |

## Architecture Highlights

### Error Recovery Strategy

```
Validation → Try Operation → Catch Error → Retry → User Feedback
```

### Data Flow

```
Recording → STT → LLM Processing → TTS → Playback
   ↓                                          ↓
Memory     Conversation History Saved    User Hears
```

### Configuration Hierarchy

```
Defaults → Load from File → User Changes → Save to File
```

## Supported Languages

**Text-to-Speech (Voices)**:

- English (en_US) - lessac-high
- German (de_DE) - thorsten-medium

**Speech Recognition**:

- English (en)
- German (de)
- French (fr)
- [More available via Whisper]

## Performance Tips

1. **Use GPU** if available (Ollama + Whisper support CUDA/Metal)
2. **Smaller Models** = Faster responses (neural-chat vs wizard-math)
3. **SSD Storage** = Better I/O performance
4. **Close Background Apps** = More RAM available
5. **Good Microphone** = Better transcription

## Known Limitations

- Single conversation at a time (sessions are sequential)
- Requires microphone for input
- Ollama model downloads can be large (3-13 GB)
- Some models may not be ideal for tutoring

## Next Steps

1. **Read DOCUMENTATION.md** for complete details
2. **Run `python3 main.py`** to start
3. **Try "Status"** first to verify setup
4. **Download a model** if needed (Options → Download New Model)
5. **Start Talking** to begin learning!

## File Locations

```
English-Tutor-Offline/
├── config.json           # Your settings (data/)
├── tutor.log             # Activity log (data/)
├── input.wav             # Your recorded speech (data/)
├── output.wav            # Tutor's audio response (data/)
├── DOCUMENTATION.md      # Full documentation
├── Readme.md             # Project overview
└── (Python files above)
```

## Example Session

```bash
$ python3 main.py

[APPLICATION STARTS]

  English Tutor Offline
  Main Menu
  [1] Start Talking
  [2] Options
  [3] Status
  [Q] Quit Application

  Select option: 3

[YOU SEE STATUS]
  ✓ Ollama Server: Running
  ✓ LLM Model: llama3.1:latest
  ✓ All components ready!

  Select option: 1

[CONVERSATION STARTS]
  Press ENTER to begin...
  [YOU PRESS ENTER]

  🎤 Recording... (speak now, 5 seconds)
  [YOU SPEAK: "Hello, how are you?"]

  📝 Transcribing audio...
  You said: "Hello, how are you?"

  🤖 Thinking...
  Tutor: "I'm doing well, thank you for asking!
  How are you doing today? Is there anything
  specific about English you'd like to practice?"

  🎵 Synthesizing speech...
  🔊 Playing response...
  [YOU HEAR TUTOR'S VOICE]

  Continue conversation? (y/n): y
  [REPEAT FOR NEXT TURN]
```

## Support Resources

1. **DOCUMENTATION.md** - Complete feature documentation
2. **data/tutor.log** - Detailed activity logs
3. **Code Comments** - Every function is documented
4. **This File** - Quick reference guide

## Summary

You now have:

- ✅ Professional CLI interface
- ✅ Configuration management
- ✅ Error recovery system
- ✅ Model management
- ✅ Multi-language support
- ✅ Comprehensive documentation
- ✅ Production-ready error handling

**Ready to start?** Run `python3 main.py`

---

For detailed information, see [DOCUMENTATION.md](DOCUMENTATION.md)
