def detect_intent(text):
    text = text.lower().strip()

    if any(word in text for word in ["where", "location"]):
        return "location"

    if any(word in text for word in ["who is", "who's", "daughter", "son", "wife", "husband", "family"]):
        return "person"

    if any(word in text for word in ["medicine", "medication", "tablet", "pill"]):
        return "routine"

    return "general"
