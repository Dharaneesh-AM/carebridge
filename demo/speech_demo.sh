#!/bin/bash

PROJECT_DIR="/home/dvm/CareBridge"
PYTHON="$PROJECT_DIR/.venv/bin/python"

echo "=============================================="
echo "        CAREBRIDGE SPEECH DEMO"
echo "=============================================="
echo
echo "Speak your question after the microphone starts."
echo "CareBridge will listen, think, and respond."
echo
echo "Starting..."
echo

"$PYTHON" -m brain.voice_assistant

STATUS=$?

echo
echo "----------------------------------------------"

if [ "$STATUS" -eq 0 ]; then
    echo "Speech demo complete."
else
    echo "Speech demo exited with an error."
fi

echo "----------------------------------------------"

exit "$STATUS"
