import time
from datetime import datetime
import urllib.parse
import urllib.request

from memory.database import get_connection
from logs.event_logger import log_event
from audio.text_to_speech import speak

ESP32_API = "http://172.23.241.62:82"
PATIENT_ID = 1
CHECK_INTERVAL = 5

_triggered_today = set()


def send_to_esp32(message):
    encoded = urllib.parse.quote(message)
    urllib.request.urlopen(
        f"{ESP32_API}/message?text={encoded}",
        timeout=2,
    ).read()


def check_routines(now=None):
    now = now or datetime.now()
    current_time = now.strftime("%H:%M")
    today = now.date().isoformat()

    with get_connection() as connection:
        routines = connection.execute(
            """
            SELECT id, name, time, description
            FROM routines
            WHERE patient_id = ?
            ORDER BY time
            """,
            (PATIENT_ID,),
        ).fetchall()

    for routine in routines:
        key = f"{today}:{routine['id']}"

        if routine["time"] != current_time:
            continue

        if key in _triggered_today:
            continue

        message = routine["description"]

        try:
            send_to_esp32(message)
            speak(message)

            # Give the ESP32 a moment after playback, then restore its normal display.
            time.sleep(0.5)
            for attempt in range(3):
                try:
                    send_to_esp32("CareBridge Ready")
                    print("ESP32: normal display restored")
                    break
                except Exception as restore_error:
                    print(f"ESP32 restore attempt {attempt + 1}/3 failed: {restore_error}")
                    if attempt < 2:
                        time.sleep(1)

            log_event(
                "routine_reminder",
                f"{routine['name']}: {message}",
            )
            _triggered_today.add(key)

            print("ROUTINE:", routine["name"])
            print("REMINDER:", message)
            print("ESP32: OK")

        except Exception as error:
            print("ROUTINE ERROR:", error)


if __name__ == "__main__":
    print("CareBridge routine scheduler started.")
    print("Checking routines every", CHECK_INTERVAL, "seconds.")

    while True:
        try:
            check_routines()
        except Exception as error:
            print("SCHEDULER ERROR:", error)

        time.sleep(CHECK_INTERVAL)
