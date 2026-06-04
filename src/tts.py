import subprocess
from pathlib import Path

PIPER_BIN = Path("venv/bin/piper")
VOICE = Path("piper/voices/en_US-lessac-high.onnx")


def speak(text: str, output_wav: str) -> None:
    output_wav = Path(output_wav) # type: ignore

    subprocess.run(
        [
            str(PIPER_BIN),
            "--model", str(VOICE),
            "--output_file", str(output_wav)
        ],
        input=text.encode("utf-8"),
        check=True
    )