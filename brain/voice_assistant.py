import json

from audio.microphone import record_audio
from audio.speech_to_text import transcribe
from audio.text_to_speech import speak
from brain.context import get_patient_context
from brain.conversation import add_turn, get_history
from brain.reference import resolve_person_reference
from brain.llm import LocalLLM
from brain.intent import detect_intent
from logs.event_logger import log_event
from safety.safety_engine import check_safety
from safety.alert_state import activate_alert

AUDIO_FILE = "/tmp/carebridge_voice.wav"
PATIENT_ID = 1


def ask_from_voice(seconds=5, user_text=None):
    if user_text is None:
        record_audio(AUDIO_FILE, seconds)
        user_text = transcribe(AUDIO_FILE)

    if not user_text:
        return ""

    print("USER:", user_text)

    intent = detect_intent(user_text)
    print("INTENT:", intent)
    log_event("voice_query", user_text)

    safety = check_safety(user_text)
    print("SAFETY:", safety)

    if safety["alert"]:
        activate_alert(safety["reason"], "living room", patient="Arjun", source="VOICE")
        alert_message = (
            "I heard that you may need help. "
            "Please stay where you are. A caregiver should check on you."
        )
        log_event("safety_alert", f"Safety alert: {safety['reason']}")
        add_turn(user_text, alert_message)
        return alert_message

    context = get_patient_context(PATIENT_ID)
    history = get_history()

    previous_person = None
    if history:
        for turn in reversed(history):
            resolved = resolve_person_reference(
                turn["user"],
                PATIENT_ID,
                None,
            )
            if resolved:
                previous_person = resolved
                break

    resolved_person = resolve_person_reference(
        user_text,
        PATIENT_ID,
        previous_person,
    )

    prompt = (
        "You are Mitra, a warm, friendly offline personal companion. "
        "Speak naturally like a kind and patient friend. "
        "Never describe the user as a patient and never mention a diagnosis "
        "unless the user explicitly asks about it. "
        "Never scold, correct harshly, test, embarrass, or make the user feel "
        "bad about forgetting something. "
        "If the user remembers something differently from stored information, "
        "respond positively and gently offer the stored information without "
        "insisting that the user is wrong. "
        "Use remembered events and personal information to help the user "
        "recall their day and previous days. "
        "Treat memory as support for conversation, not as a test. "
        "If something is not recorded, say so honestly and do not invent it. "
        "Keep responses natural, reassuring, and reasonably short.\n\n"
        "Patient context:\n"
        f"{json.dumps(context)}\n\n"
        "Recent conversation:\n"
        f"{json.dumps(history)}\n\n"
        f"Current user question: {user_text}\n\n"
        f"Resolved person reference: {json.dumps(resolved_person)}\n\n"
        "Use the patient context as the source of factual information. "
        "Python may provide a resolved person reference. "
        "When a resolved person is provided, use that person to obtain "
        "the factual information needed to answer the question. "
        "Preserve the user's natural relationship wording when replying. "
        "For example, if the user says 'my daughter', say 'your daughter' "
        "rather than 'the patient's daughter' or '<patient name>\'s daughter'. "
        "Do not replace 'my', 'your', or other natural relationship wording "
        "with the patient's name unless the user explicitly asks for the name. "
        "Use recent conversation only as supporting context. "
        "If that person's location is provided, use that location "
        "in the answer. "
        "Do not invent facts. "
        "If the requested information is not known, say that you do not know. "
        "Keep the answer short and calm."
    )

    answer = LocalLLM().ask(prompt)

    add_turn(user_text, answer)

    return answer


if __name__ == "__main__":
    answer = ask_from_voice(seconds=5)

    if answer:
        print("CAREBRIDGE:", answer)
        speak(answer)
