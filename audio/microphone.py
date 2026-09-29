import subprocess


MIC_TARGET = "bluez_input.41:42:DF:2A:50:F5"
SAMPLE_RATE = "16000"
CHANNELS = "1"
AUDIO_FORMAT = "s16"


def record_audio(output_file, seconds=5):
    command = [
        "pw-record",
        "--target",
        MIC_TARGET,
        "--rate",
        SAMPLE_RATE,
        "--channels",
        CHANNELS,
        "--format",
        AUDIO_FORMAT,
        output_file,
    ]

    process = subprocess.Popen(command)

    try:
        process.wait(timeout=seconds)
    except subprocess.TimeoutExpired:
        process.terminate()
        process.wait()


if __name__ == "__main__":
    record_audio("/tmp/carebridge_python_test.wav", seconds=5)
