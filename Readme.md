# English Tutor Offline

An offline-first conversational English tutor powered by local AI models.

The application allows you to practice spoken English directly from your microphone. Your speech is transcribed locally, sent to a local language model for conversation and corrections, and the response is synthesized back into speech.

## Features

- Speech-to-text using Whisper.cpp
- Local conversational AI using Ollama and Llama 3.1
- Text-to-speech using Piper
- Continuous voice conversation loop
- Grammar correction and conversational practice
- No cloud services required
- Fully self-hosted

## Architecture

```text
Microphone
    ↓
Whisper.cpp
    ↓
Transcribed text
    ↓
Llama 3.1 (Ollama)
    ↓
Response text
    ↓
Piper
    ↓
Audio output
```

## Project Structure

```text
English-Tutor/
│
├── main.py
├── speech_to_text.py
├── chat.py
├── text_to_speech.py
│
├── whisper.cpp/
│   ├── build/
│   └── models/
│
├── piper/
│   └── voices/
│
├── data/
│   ├── input.wav
│   └── output.wav
│
├── requirements.txt
└── README.md
```

## Requirements

### Python

- Python 3.10 or newer

### Python Dependencies

Install:

```bash
pip install -r requirements.txt
```

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
