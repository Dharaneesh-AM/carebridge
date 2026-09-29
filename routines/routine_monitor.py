from datetime import datetime

from routines.routine_engine import get_due_routines, build_routine_message
from brain.llm import LocalLLM
from audio.text_to_speech import speak
from logs.event_logger import log_event

PATIENT_ID = 1


def check_routines(current_time=None):
    if current_time is None:
        current_time = datetime.now().strftime("%H:%M")

    due_routines = get_due_routines(PATIENT_ID, current_time)

    for routine in due_routines:
        prompt = build_routine_message(routine)
        answer = LocalLLM().ask(prompt)

        print("ROUTINE:", routine["name"])
        print("CAREBRIDGE:", answer)

        log_event(
            "routine_reminder",
            f"{routine['name']}: {answer}",
        )

        speak(answer)


if __name__ == "__main__":
    check_routines()
