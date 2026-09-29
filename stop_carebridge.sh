#!/bin/bash
set -u

PROJECT_DIR="/home/dvm/CareBridge"
PID_DIR="$PROJECT_DIR/.pids"

echo "======================================"
echo "        CAREBRIDGE SHUTDOWN"
echo "======================================"

for NAME in recognition_monitor routine_scheduler pi_oled dashboard qwen; do
    PIDFILE="$PID_DIR/$NAME.pid"

    if [ -f "$PIDFILE" ]; then
        PID=$(cat "$PIDFILE")

        if kill -0 "$PID" 2>/dev/null; then
            echo "Stopping $NAME (PID $PID)..."
            kill "$PID"
            sleep 1

            if kill -0 "$PID" 2>/dev/null; then
                echo "Force stopping $NAME..."
                kill -9 "$PID" 2>/dev/null || true
            fi

            echo "✓ $NAME stopped"
        else
            echo "○ $NAME already stopped"
        fi

        rm -f "$PIDFILE"
    else
        echo "○ $NAME not managed by CareBridge"
    fi
done

echo
echo "CareBridge shutdown complete."
