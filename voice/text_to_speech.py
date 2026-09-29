import subprocess
import tempfile
from pathlib import Path


class TextToSpeech:

    def __init__(self, output_target=84):
        self.output_target = output_target

    def speak(self, text):
        text = text.strip()

        if not text:
            return

        with tempfile.NamedTemporaryFile(
            suffix=".wav",
            delete=False
        ) as temp_file:

            wav_path = Path(temp_file.name)

        try:
            subprocess.run(
                [
                    "espeak-ng",
                    "-v",
                    "en",
                    "-w",
                    str(wav_path),
                    text
                ],
                check=True
            )

            subprocess.run(
                [
                    "pw-play",
                    "--target",
                    str(self.output_target),
                    str(wav_path)
                ],
                check=True
            )

        finally:
            wav_path.unlink(missing_ok=True)
