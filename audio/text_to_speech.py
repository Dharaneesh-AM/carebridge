import subprocess
import tempfile
import time
import wave

PIPER_MODEL = "/home/dvm/CareBridge/models/piper/en_US-lessac-medium.onnx"
SPEAKER_TARGET = "bluez_output.41_42_DF_2A_50_F5.1"


def speak(text):
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp:
        audio_file = temp.name

    try:
        subprocess.run(
            [
                ".venv/bin/piper",
                "-m",
                PIPER_MODEL,
                "--sentence-silence",
                "0.3",
                "-f",
                audio_file,
            ],
            input=text,
            text=True,
            check=True,
        )

        time.sleep(0.5)

        subprocess.run(
            [
                "pw-play",
                "--target",
                SPEAKER_TARGET,
                audio_file,
            ],
            check=True,
        )

    finally:
        subprocess.run(
            ["rm", "-f", audio_file],
            check=False,
        )
