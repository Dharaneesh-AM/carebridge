import sqlite3
from datetime import datetime

from memory.database import get_connection
from logs.event_logger import log_event
from audio.text_to_speech import speak


PATIENT_ID = 1


def add_event(description):
    timestamp = datetime.now().isoformat()

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO events
                (patient_id, event_type, description, timestamp)
            VALUES (?, ?, ?, ?)
            """,
            (
                PATIENT_ID,
                "morning_companion",
                description,
                timestamp,
            ),
        )
        connection.commit()

    log_event("morning_companion", description)


def get_morning_reminders():
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT name, time, description
            FROM routines
            WHERE patient_id = ?
            ORDER BY time
            """,
            (PATIENT_ID,),
        ).fetchall()

    return [dict(row) for row in rows]


def run_morning_companion():
    print()
    print("==============================================")
    print("       CAREBRIDGE MORNING COMPANION")
    print("==============================================")
    print("SIMULATED TIME: 06:00 AM")
    print()

    greeting = (
        "Good morning. I'm CareBridge, your care companion. "
        "Your caregiver is busy right now, but I'm here with you "
        "and I'll help you through your morning. "
        "You don't need to worry."
    )

    print("CAREBRIDGE:", greeting)
    speak(greeting)

    question = "Would you like me to turn on the lights?"
    print("CAREBRIDGE:", question)
    speak(question)

    print()
    print("DEMO RESPONSE: YES")
    print()

    add_event("Patient requested morning lights to be turned on.")

    print("ACTION: Morning lights ON")
    speak("Okay. I've turned on the lights.")

    reminders = get_morning_reminders()

    print()
    print("TODAY'S REMINDERS")
    print("----------------------------------------------")

    if not reminders:
        print("No reminders found.")
    else:
        for reminder in reminders:
            print(
                f"{reminder['time']} - "
                f"{reminder['name']}: "
                f"{reminder['description']}"
            )

    reminder_text = (
        "You have three reminders today. "
        "Your medicine is at 10 AM. "
        "Your exercise is at 5 PM. "
        "Your daughter is scheduled to visit at 8 PM."
    )

    print()
    print("CAREBRIDGE:", reminder_text)
    speak(reminder_text)

    question = "Would you like me to add anything else to your reminders?"
    print()
    print("CAREBRIDGE:", question)
    speak(question)

    print()
    print("DEMO RESPONSE:")
    print('\"Remind me to call my son at 7 PM.\"')
    print()

    new_reminder = "Call my son at 7 PM"

    add_event(
        "New reminder requested: "
        f"{new_reminder}"
    )

    print("REMINDER SAVED:", new_reminder)
    speak(
        "Okay. I've added a reminder to call your son at 7 PM."
    )

    print()
    print("EVENT LOG UPDATED")
    print("----------------------------------------------")
    print("New event: Call my son at 7 PM")
    print()
    print("Morning Companion demo complete.")
    print("==============================================")


if __name__ == "__main__":
    run_morning_companion()
