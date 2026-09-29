#!/bin/bash

PROJECT_DIR="/home/dvm/CareBridge"
PYTHON="$PROJECT_DIR/.venv/bin/python"

echo "=============================================="
echo "       CAREBRIDGE UNKNOWN INFO DEMO"
echo "=============================================="
echo
echo "Ask CareBridge something that is NOT in its"
echo "known patient context."
echo
echo "Example:"
echo '  "What is my neighbour'\''s phone number?"'
echo
echo "Starting..."
echo

"$PYTHON" -m brain.voice_assistant

STATUS=$?

echo
echo "----------------------------------------------"

if [ "$STATUS" -eq 0 ]; then
    echo "Unknown-information demo complete."
else
    echo "Unknown-information demo exited with an error."
fi

echo "----------------------------------------------"

exit "$STATUS"
