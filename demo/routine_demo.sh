#!/bin/bash

PROJECT_DIR="/home/dvm/CareBridge"
PYTHON="$PROJECT_DIR/.venv/bin/python"

echo "=============================================="
echo "        CAREBRIDGE ROUTINE DEMO"
echo "=============================================="
echo
echo "Simulating today's scheduled routines."
echo

"$PYTHON" - <<'PY'
from datetime import datetime
from brain.routine_scheduler import check_routines, _triggered_today

tests = [
    ("10:00", "Morning Medicine"),
    ("17:00", "Evening Exercise"),
    ("20:00", "Daughter Visit"),
]

for clock, name in tests:
    print("----------------------------------------------")
    print(f"SIMULATED TIME: {clock}")
    print(f"ROUTINE: {name}")
    print("----------------------------------------------")

    check_routines(
        datetime.strptime(
            f"2026-09-25 {clock}",
            "%Y-%m-%d %H:%M",
        )
    )

    print()

_triggered_today.clear()

print("----------------------------------------------")
print("Routine rehearsal complete.")
print("----------------------------------------------")
PY
