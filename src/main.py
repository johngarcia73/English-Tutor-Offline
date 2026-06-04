import subprocess
from pathlib import Path

from stt import transcribe
from chat import ask_llm
from tts import speak


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


def main():
    history = []

    print("English tutor ready. Press ENTER to talk (Ctrl+C to exit)")

    while True:
        input("\nPress ENTER...")

        print("Recording...")
        record_audio()

        print("Transcribing...")
        text = transcribe(INPUT_AUDIO) # type: ignore
        print("You:", text)

        print("Thinking...")
        reply = ask_llm(text, history)
        print("Tutor:", reply)

        history.append({"role": "user", "content": text})
        history.append({"role": "assistant", "content": reply})

        print("Speaking...")
        speak(reply, OUTPUT_AUDIO) # type: ignore

        play_audio(OUTPUT_AUDIO)


if __name__ == "__main__":
    main()