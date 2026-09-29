import re

from memory.database import get_connection


RELATIONSHIP_ALIASES = {
    "daughter": "daughter",
    "son": "son",
    "wife": "wife",
    "husband": "husband",
    "mother": "mother",
    "father": "father",
}


def find_person_by_relationship(patient_id, relationship):
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT name, relationship
            FROM people
            WHERE patient_id = ? AND lower(relationship) = ?
            LIMIT 1
            """,
            (patient_id, relationship.lower()),
        ).fetchone()

    return dict(row) if row else None


def resolve_person_reference(text, patient_id, previous_person=None):
    text_lower = text.lower().strip()

    for word, relationship in RELATIONSHIP_ALIASES.items():
        if re.search(rf"\b(my|the)\s+{word}\b", text_lower):
            person = find_person_by_relationship(patient_id, relationship)
            if person:
                return person

    if previous_person and re.search(
        r"\b(she|he|her|him|that person|that woman|that man)\b",
        text_lower,
    ):
        return previous_person

    return None
