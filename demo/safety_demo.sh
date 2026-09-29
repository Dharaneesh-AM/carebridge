#!/bin/bash

PROJECT_DIR="/home/dvm/CareBridge"
PYTHON="$PROJECT_DIR/.venv/bin/python"

echo "=============================================="
echo "          CAREBRIDGE SAFETY DEMO"
echo "=============================================="
echo
echo "Simulating patient safety request: HELP"
echo

"$PYTHON" - <<'PY'
from safety.safety_engine import check_safety
from safety.alert_state import activate_alert, get_alert, clear_alert

test_text = "Help, I have fallen."

print("PATIENT:", test_text)

result = check_safety(test_text)

print("SAFETY CHECK:", result)

if result["alert"]:
    state = activate_alert(
        result["reason"],
        "living room",
        patient="Arjun",
        source="DEMO",
    )

    print()
    print("ALERT ACTIVATED")
    print("REASON:", state["reason"])
    print("LOCATION:", state["location"])
    print("PATIENT:", state["patient"])
    print("SOURCE:", state["source"])
    print("TIMESTAMP:", state["timestamp"])

    print()
    print("Shared alert state:")
    print(get_alert())

    input("\nPress ENTER after verifying the dashboard/OLED alert...")

    clear_alert()

    print()
    print("ALERT CLEARED")
    print("Shared alert state:")
    print(get_alert())
else:
    print("ERROR: Safety engine did not trigger an alert.")
    raise SystemExit(1)
PY

echo
echo "----------------------------------------------"
echo "Safety demo complete."
echo "----------------------------------------------"
