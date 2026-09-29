from logs.event_logger import log_event


_previous_person_state = None


def detect_activity(person_detected):
    """
    Convert person-detection state into a state-change activity.

    Events are logged only when the person-presence state changes.
    """
    global _previous_person_state

    current_state = bool(person_detected)

    if _previous_person_state is None:
        _previous_person_state = current_state
        activity = "person_present" if current_state else "no_person"
        log_event("activity", activity)
        return activity

    if current_state == _previous_person_state:
        return "no_change"

    _previous_person_state = current_state

    if current_state:
        activity = "person_present"
    else:
        activity = "person_left"

    log_event("activity", activity)
    return activity


if __name__ == "__main__":
    print("ACTIVITY TEST:", detect_activity(True))
    print("ACTIVITY TEST:", detect_activity(True))
    print("ACTIVITY TEST:", detect_activity(False))
    print("ACTIVITY TEST:", detect_activity(False))
