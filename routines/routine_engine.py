from datetime import datetime
from memory.database import get_connection


def get_due_routines(patient_id, current_time=None):
    if current_time is None:
        current_time = datetime.now().strftime("%H:%M")

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, name, time, description
            FROM routines
            WHERE patient_id = ?
            """,
            (patient_id,),
        ).fetchall()

    due = []

    for row in rows:
        if row["time"] == current_time:
            due.append(dict(row))

    return due


def build_routine_message(routine):
    return (
        f"The patient has a scheduled routine: "
        f"{routine['name']}. "
        f"Description: {routine['description']}. "
        "Give a short, calm reminder."
    )
