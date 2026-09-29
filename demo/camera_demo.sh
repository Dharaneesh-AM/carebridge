#!/bin/bash

PROJECT_DIR="/home/dvm/CareBridge"
PYTHON="$PROJECT_DIR/.venv/bin/python"

echo "=============================================="
echo "        CAREBRIDGE CAMERA DEMO"
echo "=============================================="
echo
echo "Camera recognition is starting."
echo
echo "Show the patient to the camera."
echo "Press Ctrl+C to end the demo."
echo

trap 'echo; echo "Camera demo stopped."; exit 0' INT TERM

"$PYTHON" -m vision.recognition_monitor
