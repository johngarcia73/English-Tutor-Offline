from stt import transcribe
from chat import ask_llm
from tts import speak
from llm_server import ollama_llms_available, ollama_generate, run_ollama, get_ollama_client, get_models_names, get_response_text
import subprocess
from pathlib import Path


DATA_DIR = Path("data")
INPUT_AUDIO = DATA_DIR / "input.wav"
OUTPUT_AUDIO = DATA_DIR / "output.wav"

RECORD_SECONDS = 5

def record_audio():
    subprocess.run([
        "arecord",
        "-f", "cd",
        "-d", str(RECORD_SECONDS),
        str(INPUT_AUDIO)
    ], check=True)


def play_audio(path: Path):
    subprocess.run([
        "ffplay",
        "-nodisp",
        "-autoexit",
        str(path)
    ], check=True)

def orchest():

    history = []

    print("English tutor ready. Press ENTER to talk (Ctrl+C to exit)")

    run_ollama()

    while True:
        pass