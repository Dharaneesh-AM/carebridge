import subprocess


WHISPER_BIN = "/home/dvm/whisper.cpp/build/bin/whisper-cli"
WHISPER_MODEL = "/home/dvm/whisper.cpp/models/ggml-tiny.en.bin"


def transcribe(audio_file):
    result = subprocess.run(
        [
            WHISPER_BIN,
            "-m",
            WHISPER_MODEL,
            "-f",
            audio_file,
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    lines = []

    for line in result.stdout.splitlines():
        line = line.strip()

        if line.startswith("[") and "]" in line:
            text = line.split("]", 1)[1].strip()

            if text and text != "[BLANK_AUDIO]" and text != "BLANK_AUDIO":
                lines.append(text)

    return " ".join(lines)
