from datetime import datetime
from pathlib import Path
import json

STATE_FILE = Path(__file__).resolve().parent.parent / "data" / "alert_state.json"


def _default_state():
    return {
        "active": False,
        "reason": None,
        "location": None,
        "patient": None,
        "source": None,
        "timestamp": None,
    }


def get_alert():
    try:
        if not STATE_FILE.exists():
            return _default_state()

        with open(STATE_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)

        if not isinstance(state, dict):
            return _default_state()

        result = _default_state()
        result.update(state)
        return result

    except Exception:
        return _default_state()


def activate_alert(reason, location, patient="Arjun", source="VOICE"):
    state = {
        "active": True,
        "reason": reason.upper(),
        "location": location,
        "patient": patient,
        "source": source.upper(),
        "timestamp": datetime.now().isoformat(),
    }

    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

    return state


def clear_alert():
    state = _default_state()

    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

    return state
