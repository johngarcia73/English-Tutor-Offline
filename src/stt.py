import subprocess
from pathlib import Path

WHISPER_CLI = Path("whisper.cpp/build/bin/whisper-cli")
MODEL = Path("whisper.cpp/models/ggml-base.en.bin")


def transcribe(audio_path: str) -> str:
    audio_path = Path(audio_path) # type: ignore

    out_prefix = audio_path.with_suffix("") # type: ignore

    cmd = [
        str(WHISPER_CLI),
        "-m", str(MODEL),
        "-f", str(audio_path),
        "-l", "en",
        "-otxt",
        "-of", str(out_prefix),
        "-nt"
    ]

    subprocess.run(cmd, check=True)

    txt_file = Path(str(out_prefix) + ".txt")

    return txt_file.read_text(encoding="utf-8").strip()