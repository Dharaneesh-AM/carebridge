import time
import urllib.parse
import urllib.request

from vision.face_recognition import recognize_from_camera
from logs.event_logger import log_event

CHECK_INTERVAL = 5
ESP32_API = "http://172.23.241.62:82"

_previous_state = None


def check_recognition():
    global _previous_state

    state, score = recognize_from_camera()

    if state == _previous_state:
        return state, score

    _previous_state = state

    if state == "patient":
        description = "Patient detected by USB C270 camera"
    elif state == "other_person":
        description = "Other person detected by USB C270 camera"
    elif state == "multiple_faces":
        description = "Multiple people detected by USB C270 camera"
    else:
        description = "No face detected by USB C270 camera"

    log_event("recognition", description)

    # Send a short status message to the bedroom OLED.
    if state == "patient":
        message = "Welcome back"
    elif state == "other_person":
        message = "Visitor detected"
    elif state == "multiple_faces":
        message = "Multiple people"
    else:
        message = "No face detected"

    try:
        encoded = urllib.parse.quote(message)
        urllib.request.urlopen(
            f"{ESP32_API}/message?text={encoded}",
            timeout=2,
        ).read()
        print("OLED:", message)
    except Exception as error:
        print("OLED ERROR:", error)

    print("RECOGNITION:", state)
    print("SCORE:", score)

    return state, score


if __name__ == "__main__":
    print("CareBridge recognition monitor started.")

    while True:
        try:
            check_recognition()
        except Exception as error:
            print("RECOGNITION ERROR:", error)

        time.sleep(CHECK_INTERVAL)
