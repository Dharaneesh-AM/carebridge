#!/bin/bash

PROJECT_DIR="/home/dvm/CareBridge"
PYTHON="$PROJECT_DIR/.venv/bin/python"
ESP32="http://172.23.241.62:82"

INITIAL_WAIT=120
RETRY_WAIT=10
MAX_ROUNDS=3

echo "=============================================="
echo "       CAREBRIDGE BUILT-IN SELF-TEST"
echo "=============================================="
echo
echo "Waiting ${INITIAL_WAIT} seconds for hardware startup..."
sleep "$INITIAL_WAIT"
echo "✓ Startup stabilization complete"
echo

PASS=0
FAIL=0

check() {
    LABEL="$1"
    shift

    if "$@"; then
        echo "✓ $LABEL"
        PASS=$((PASS + 1))
        return 0
    else
        echo "✗ $LABEL"
        FAIL=$((FAIL + 1))
        return 1
    fi
}

check_qwen() {
    curl -s --max-time 2 http://127.0.0.1:8080/v1/models >/dev/null 2>&1
}

check_dashboard() {
    pgrep -f "python.*-m dashboard.app" >/dev/null 2>&1
}

check_oled() {
    pgrep -f "python.*-m hardware.pi_oled" >/dev/null 2>&1
}

check_camera() {
    test -e /dev/video0
}

check_opencv() {
    "$PYTHON" -c "import cv2" >/dev/null 2>&1
}

check_whisper() {
    test -x "$HOME/whisper.cpp/build/bin/whisper-cli" &&
    test -f "$HOME/whisper.cpp/models/ggml-tiny.en.bin"
}

check_piper() {
    test -x "$PROJECT_DIR/.venv/bin/piper" &&
    test -f "$PROJECT_DIR/models/piper/en_US-lessac-medium.onnx"
}

check_sqlite() {
    "$PYTHON" -c "import sqlite3; sqlite3.connect('$PROJECT_DIR/data/carebridge.db').execute('SELECT 1')" >/dev/null 2>&1
}

check_esp32() {
    curl -s --max-time 2 "$ESP32/status" >/dev/null 2>&1
}

run_round() {
    ROUND="$1"

    echo "----------------------------------------------"
    echo "BIST ROUND $ROUND / $MAX_ROUNDS"
    echo "----------------------------------------------"

    PASS=0
    FAIL=0

    check "Qwen API" check_qwen
    check "Dashboard" check_dashboard
    check "Pi OLED" check_oled
    check "Camera" check_camera
    check "OpenCV" check_opencv
    check "Whisper + model" check_whisper
    check "Piper + model" check_piper
    check "SQLite database" check_sqlite
    check "ESP32" check_esp32

    echo
    echo "PASS: $PASS"
    echo "FAIL: $FAIL"
    echo

    [ "$FAIL" -eq 0 ]
}

for ROUND in 1 2 3; do
    if run_round "$ROUND"; then
        echo "=============================================="
        echo "RESULT: SYSTEM READY ✓"
        echo "=============================================="
        exit 0
    fi

    if [ "$ROUND" -lt "$MAX_ROUNDS" ]; then
        echo "ROUND $ROUND FAILED"
        echo "Retrying in ${RETRY_WAIT} seconds..."
        echo
        sleep "$RETRY_WAIT"
    fi
done

echo "=============================================="
echo "RESULT: SYSTEM NOT READY ✗"
echo "=============================================="
exit 1
