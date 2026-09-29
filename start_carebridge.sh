#!/bin/bash
set -u

PROJECT_DIR="/home/dvm/CareBridge"
PYTHON="$PROJECT_DIR/.venv/bin/python"
LLAMA="/home/dvm/llama.cpp/build/bin/llama-server"
PID_DIR="$PROJECT_DIR/.pids"

mkdir -p "$PID_DIR"

echo "======================================"
echo "       CAREBRIDGE STARTUP"
echo "======================================"

start_process() {
    NAME="$1"
    PIDFILE="$PID_DIR/$NAME.pid"
    shift

    if [ -f "$PIDFILE" ]; then
        OLD_PID=$(cat "$PIDFILE")
        if kill -0 "$OLD_PID" 2>/dev/null; then
            echo "✓ $NAME already running (PID $OLD_PID)"
            return
        fi
        rm -f "$PIDFILE"
    fi

    echo "Starting $NAME..."
    "$@" > "$PROJECT_DIR/logs/${NAME}.log" 2>&1 &
    PID=$!
    echo "$PID" > "$PIDFILE"
    echo "✓ $NAME started (PID $PID)"
}

start_process qwen     "$LLAMA"     -hf ggml-org/Qwen3.5-0.8B-GGUF:Q4_0     --host 127.0.0.1     --port 8080     -c 4096     --reasoning off

echo "Waiting for Qwen..."
for i in {1..30}; do
    if curl -s http://127.0.0.1:8080/v1/models >/dev/null 2>&1; then
        echo "✓ Qwen API ready"
        break
    fi
    sleep 1
done

start_process dashboard     "$PYTHON" -m dashboard.app

start_process pi_oled     "$PYTHON" -m hardware.pi_oled



echo
echo "======================================"
echo "       CAREBRIDGE STARTED"
echo "======================================"
echo
echo "Qwen                 ✓"
echo "Dashboard            ✓"
echo "Pi OLED              ✓"
echo
echo "PID files: $PID_DIR"
echo "Logs:      $PROJECT_DIR/logs/"
