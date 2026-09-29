from datetime import datetime
import json
import urllib.request
import urllib.error

from vision.face_recognition import recognize_from_camera
from audio.microphone import record_audio
from audio.speech_to_text import transcribe
from audio.text_to_speech import speak
from safety.safety_engine import check_safety
from safety.alert_state import activate_alert
from logs.event_logger import log_event
from memory.database import get_connection
from brain.context import get_patient_context
from brain.voice_assistant import ask_from_voice


PATIENT_ID = 1
PATIENT_NAME = "Arjun"
ASSISTANT_NAME = "Mitra"

AUDIO_FILE = "/tmp/carebridge_command.wav"
ESP32_API = "http://172.23.241.62:82"


def say(text):
    print(f"{ASSISTANT_NAME.upper()}: {text}")
    speak(text)


def listen():
    print("\n🎤 Listening for 5 seconds...")
    record_audio(AUDIO_FILE, seconds=5)

    text = transcribe(AUDIO_FILE)

    if text:
        print("USER:", text)
    else:
        print("USER: [no speech detected]")

    return text.strip() if text else ""


def save_conversation_memory(memory, memory_type="conversation"):
    if not memory:
        return

    try:
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO conversation_memory
                (patient_id, memory, memory_type, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (
                    PATIENT_ID,
                    memory,
                    memory_type,
                    datetime.now().isoformat(),
                ),
            )
            connection.commit()
    except Exception as exc:
        print("Memory save warning:", exc)


def get_relevant_memory_text():
    context = get_patient_context(PATIENT_ID)

    parts = []

    patient = context.get("patient")
    if patient:
        parts.append(f"Name: {patient['name']}")

    people = context.get("people", [])
    if people:
        people_text = ", ".join(
            f"{p['name']} ({p.get('relationship') or 'known person'})"
            for p in people
        )
        parts.append(f"People: {people_text}")

    memories = context.get("memories", [])
    if memories:
        parts.append(
            "Personal memories: "
            + "; ".join(m["memory"] for m in memories[:8])
        )

    yesterday_events = context.get("yesterday_events", [])
    if yesterday_events:
        parts.append(
            "Yesterday's events: "
            + "; ".join(e["description"] for e in yesterday_events[:8])
        )

    yesterday_memories = context.get("yesterday_memories", [])
    if yesterday_memories:
        parts.append(
            "Yesterday's conversation memories: "
            + "; ".join(m["memory"] for m in yesterday_memories[:8])
        )

    routines = context.get("routines", [])
    if routines:
        parts.append(
            "Routines: "
            + "; ".join(
                f"{r['name']} at {r['time'] or 'unspecified time'}"
                for r in routines[:8]
            )
        )

    recent_events = context.get("recent_events", [])
    if recent_events:
        parts.append(
            "Recent events: "
            + "; ".join(e["description"] for e in recent_events[:8])
        )

    return "\n".join(parts)


def relay(state):
    try:
        url = f"{ESP32_API}/relay/{state}"
        request = urllib.request.Request(url, method="POST")

        with urllib.request.urlopen(request, timeout=3) as response:
            response.read()

        return True

    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        print("Relay error:", exc)
        return False


def get_routines():
    with get_connection() as connection:
        return connection.execute(
            """
            SELECT name, time, description
            FROM routines
            WHERE patient_id = ?
            ORDER BY time
            """,
            (PATIENT_ID,),
        ).fetchall()


def speak_today_routines():
    rows = get_routines()

    if not rows:
        say("You don't have any routines stored for today.")
        return

    say("Of course. Here are the routines I have for you today.")

    for row in rows:
        if row["time"]:
            say(f"{row['name']} is scheduled for {row['time']}.")
        else:
            say(row["name"])


def introduce():
    now = datetime.now()
    current = now.strftime("%I:%M %p").lstrip("0")

    if 5 <= now.hour < 12:
        greeting = "Good morning"
    elif 12 <= now.hour < 17:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"

    say(
        f"Hello {PATIENT_NAME}. I'm {ASSISTANT_NAME}, "
        "your friendly companion. It's nice to see you."
    )

    say(f"{greeting}, {PATIENT_NAME}. It's {current}.")

    context = get_patient_context(PATIENT_ID)
    yesterday = context.get("yesterday_events", [])

    if yesterday:
        say(
            "I remember a few things from yesterday. "
            "Would you like to talk about what happened yesterday?"
        )
    else:
        say("How are you feeling today?")


def safety_response(text):
    safety = check_safety(text)

    if not safety["alert"]:
        return False

    activate_alert(
        safety["reason"],
        "living room",
        patient=PATIENT_NAME,
        source="VOICE",
    )

    log_event(
        "safety_alert",
        f"Mitra detected a safety request: {text}",
    )

    say(
        "I'm here with you. I have requested help for you. "
        "Please stay where you are and take your time."
    )

    return True


def handle_light(text):
    lower = text.lower()

    if "light" not in lower:
        return False

    if any(
        phrase in lower
        for phrase in [
            "turn on",
            "switch on",
            "light on",
            "lights on",
        ]
    ):
        if relay("on"):
            log_event(
                "relay_on",
                f"{PATIENT_NAME} asked Mitra to turn the light on.",
            )
            say("Of course. I've turned the light on for you.")
        else:
            say(
                "I tried to turn the light on, "
                "but I can't reach the light control right now."
            )

        return True

    if any(
        phrase in lower
        for phrase in [
            "turn off",
            "switch off",
            "light off",
            "lights off",
        ]
    ):
        if relay("off"):
            log_event(
                "relay_off",
                f"{PATIENT_NAME} asked Mitra to turn the light off.",
            )
            say("Of course. I've turned the light off for you.")
        else:
            say(
                "I tried to turn the light off, "
                "but I can't reach the light control right now."
            )

        return True

    return False


def handle_time(text):
    lower = text.lower()

    if not (
        "what time" in lower
        or "current time" in lower
        or "time is it" in lower
        or "what's the time" in lower
    ):
        return False

    current = datetime.now().strftime("%I:%M %p").lstrip("0")
    say(f"It's currently {current}, {PATIENT_NAME}.")
    return True


def handle_routines(text):
    lower = text.lower()

    if not any(
        phrase in lower
        for phrase in [
            "routine",
            "routines",
            "schedule",
            "what do i have today",
            "what am i doing today",
        ]
    ):
        return False

    speak_today_routines()
    return True


def handle_yesterday(text):
    lower = text.lower()

    if not any(
        phrase in lower
        for phrase in [
            "yesterday",
            "what happened yesterday",
            "what did i do yesterday",
            "what was yesterday like",
        ]
    ):
        return False

    context = get_patient_context(PATIENT_ID)
    events = context.get("yesterday_events", [])
    memories = context.get("yesterday_memories", [])

    if not events and not memories:
        say(
            "I don't have many details from yesterday yet. "
            "That's okay. We can start making some memories today."
        )
        return True

    say("Let me remind you.")

    spoken = set()

    for event in events[:4]:
        description = event["description"].strip()

        if description and description not in spoken:
            say(description)
            spoken.add(description)

    for memory in memories[:4]:
        value = memory["memory"].strip()

        if value and value not in spoken:
            say(value)
            spoken.add(value)

    return True


def handle_stop(text):
    lower = text.lower()

    stop_phrases = [
        "stop mitra",
        "stop",
        "exit mitra",
        "goodbye mitra",
        "go to sleep",
    ]

    if any(phrase in lower for phrase in stop_phrases):
        say("Of course. I'll be here whenever you need me. Goodbye for now.")
        return True

    return False


def friendly_response(text):
    """
    Lightweight local response policy for common conversational situations.
    We intentionally do not invent memories or claim facts that are not stored.
    """

    lower = text.lower()

    if any(word in lower for word in ["thank you", "thanks"]):
        say("You're very welcome, Arjun. I'm happy to be here with you.")
        return True

    if any(
        phrase in lower
        for phrase in [
            "i don't know",
            "i dont know",
            "i can't remember",
            "i cant remember",
            "i forgot",
            "not sure",
        ]
    ):
        say(
            "That's completely okay, Arjun. "
            "Sometimes things are hard to remember. "
            "We can take our time."
        )
        return True

    if any(
        phrase in lower
        for phrase in [
            "how are you",
            "are you okay",
        ]
    ):
        say(
            "I'm doing well, thank you. "
            "I'm happy to spend some time with you."
        )
        return True

    return False


def save_useful_user_memory(text):
    """
    Store a small amount of useful conversational information.
    This deliberately avoids storing every sentence.
    """

    lower = text.lower()

    memory_triggers = [
        "my daughter",
        "my son",
        "my wife",
        "my husband",
        "i like",
        "i love",
        "i enjoy",
        "i used to",
        "today i",
        "yesterday i",
        "yesterday we",
    ]

    if any(trigger in lower for trigger in memory_triggers):
        save_conversation_memory(
            text,
            memory_type="user_statement",
        )


def handle_command(text):
    text_lower = text.lower().strip()

    if text_lower in {
        "stop mitra",
        "stop",
        "exit mitra",
        "goodbye mitra",
        "go to sleep",
    }:
        return handle_stop()

    safety = check_safety(text)
    if safety["alert"]:
        return safety_response(text, safety)

    if handle_light(text):
        return True

    if handle_time(text):
        return True

    if handle_routines(text):
        return True

    if handle_yesterday(text):
        return True

    # All other natural conversation goes through the existing
    # Whisper -> context -> Qwen -> conversation-memory pipeline.
    answer = ask_from_voice(seconds=5, user_text=text)
    if answer:
        speak(answer)

        # Store useful personal statements for future recall.
        save_useful_user_memory(text)

    return True

def main():
    print("=" * 60)
    print("                 MITRA")
    print("       CareBridge Friendly Companion")
    print("=" * 60)
    print()
    print("Camera is checking for Arjun...")
    print()

    state, score = recognize_from_camera()

    print("RECOGNITION:", state)
    print("SCORE:", score)

    if state != "patient":
        print()
        print("Arjun was not recognized.")
        print("Mitra will not start personalized conversation.")
        return

    print()
    print("✓ Arjun recognized")
    print()

    introduce()

    while True:
        command = listen()

        if not command:
            say(
                "I didn't hear you clearly. "
                "That's okay. Take your time and try again."
            )
            continue

        if not handle_command(command):
            break

        print()
        print("-----------------------------------------------")
        print("Mitra is here and ready to listen.")
        print("-----------------------------------------------")


if __name__ == "__main__":
    main()
