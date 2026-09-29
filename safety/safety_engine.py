DANGEROUS_KEYWORDS = [
    "help",
    "fall",
    "fell",
    "hurt",
    "injured",
    "emergency",
    "fire",
    "smoke",
    "danger",
]


def check_safety(text):
    """
    Deterministic safety check.
    Python makes the decision; the LLM does not.
    """
    text = text.lower().strip()

    for keyword in DANGEROUS_KEYWORDS:
        if keyword in text:
            return {
                "safe": False,
                "alert": True,
                "reason": keyword,
            }

    return {
        "safe": True,
        "alert": False,
        "reason": None,
    }
