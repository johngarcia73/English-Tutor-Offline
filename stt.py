import os
import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
WHISPER_CLI = ROOT_DIR / "whisper.cpp/build/bin/whisper-cli"
MODEL = ROOT_DIR / "whisper.cpp/models/ggml-base.en.bin"
LIB_WHISPER_DIR = ROOT_DIR / "whisper.cpp/build/src"
LIB_GGML_DIR = ROOT_DIR / "whisper.cpp/build/ggml/src"


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

    env = os.environ.copy()
    lib_paths = ":".join(str(p) for p in [LIB_WHISPER_DIR, LIB_GGML_DIR])
    ld_path = env.get("LD_LIBRARY_PATH", "")
    env["LD_LIBRARY_PATH"] = f"{lib_paths}:{ld_path}" if ld_path else lib_paths

    subprocess.run(cmd, check=True, env=env)

    txt_file = Path(str(out_prefix) + ".txt")

    return txt_file.read_text(encoding="utf-8").strip()