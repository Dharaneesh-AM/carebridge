from datetime import datetime, timedelta
from memory.database import get_connection


def get_patient_context(patient_id):
    with get_connection() as connection:
        patient = connection.execute(
            "SELECT id, name FROM patients WHERE id = ?",
            (patient_id,),
        ).fetchone()

        people = connection.execute(
            """
            SELECT name, relationship
            FROM people
            WHERE patient_id = ?
            """,
            (patient_id,),
        ).fetchall()

        memories = connection.execute(
            """
            SELECT memory
            FROM memories
            WHERE patient_id = ?
            """,
            (patient_id,),
        ).fetchall()

        routines = connection.execute(
            """
            SELECT name, time, description
            FROM routines
            WHERE patient_id = ?
            ORDER BY time
            """,
            (patient_id,),
        ).fetchall()

        locations = connection.execute(
            """
            SELECT person_name, location, timestamp
            FROM locations
            WHERE patient_id = ?
            ORDER BY id DESC
            """,
            (patient_id,),
        ).fetchall()

        events = connection.execute(
            """
            SELECT event_type, description, timestamp
            FROM events
            WHERE patient_id = ?
            ORDER BY id DESC
            LIMIT 10
            """,
            (patient_id,),
        ).fetchall()

        conversation_memories = connection.execute(
            """
            SELECT memory, memory_type, created_at
            FROM conversation_memory
            WHERE patient_id = ?
            ORDER BY id DESC
            LIMIT 10
            """,
            (patient_id,),
        ).fetchall()

        yesterday_start = (datetime.now() - timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        yesterday_end = yesterday_start + timedelta(days=1)

        yesterday_events = connection.execute(
            """
            SELECT event_type, description, timestamp
            FROM events
            WHERE patient_id = ?
              AND timestamp >= ?
              AND timestamp < ?
            ORDER BY timestamp
            """,
            (
                patient_id,
                yesterday_start.isoformat(),
                yesterday_end.isoformat(),
            ),
        ).fetchall()

        yesterday_memories = connection.execute(
            """
            SELECT memory, memory_type, created_at
            FROM conversation_memory
            WHERE patient_id = ?
              AND created_at >= ?
              AND created_at < ?
            ORDER BY created_at
            """,
            (
                patient_id,
                yesterday_start.isoformat(),
                yesterday_end.isoformat(),
            ),
        ).fetchall()

    return {
        "patient": dict(patient) if patient else None,
        "people": [dict(row) for row in people],
        "memories": [dict(row) for row in memories],
        "routines": [dict(row) for row in routines],
        "locations": [dict(row) for row in locations],
        "recent_events": [dict(row) for row in events],
        "conversation_memories": [dict(row) for row in conversation_memories],
        "yesterday_events": [dict(row) for row in yesterday_events],
        "yesterday_memories": [dict(row) for row in yesterday_memories],
    }
