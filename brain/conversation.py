conversation_history = []

MAX_TURNS = 4


def add_turn(user_text, assistant_text):
    conversation_history.append(
        {
            "user": user_text,
            "assistant": assistant_text,
        }
    )

    if len(conversation_history) > MAX_TURNS:
        conversation_history.pop(0)


def get_history():
    return list(conversation_history)


def clear_history():
    conversation_history.clear()
