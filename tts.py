import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
PYTHON_BIN = ROOT_DIR / "venv/bin/python"
VOICE = ROOT_DIR / "piper/voices/en_US-lessac-high.onnx"


def speak(text: str, output_wav: str) -> None:
    output_wav = Path(output_wav) # type: ignore

    python_executable = str(PYTHON_BIN) if PYTHON_BIN.exists() else sys.executable

    subprocess.run(
        [
            python_executable,
            "-m",
            "piper",
            "--model",
            str(VOICE),
            "--output_file",
            str(output_wav)
        ],
        input=text.encode("utf-8"),
        check=True
    )