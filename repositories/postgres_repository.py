"""PostgresIncidentRepository — implémentation PostgreSQL (Tableau 2.7).

Nécessite le paquet tiers ``psycopg2`` (cf. requirements.txt). Le DSN de
connexion est toujours injecté depuis une variable d'environnement (jamais
en dur dans le code source — cf. Chapitre 3, 3.7, correction du mot de passe
en clair repéré dans la version initiale du portail Streamlit).
"""
from __future__ import annotations

import psycopg2
from psycopg2.extras import RealDictCursor

from core.models import Incident
from repositories.base import IIncidentRepository


class PostgresIncidentRepository(IIncidentRepository):
    def __init__(self, dsn: str):
        self._dsn = dsn

    def save(self, incident: Incident) -> None:
        with psycopg2.connect(self._dsn) as conn, conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO incidents
                    (equipment_id, incident_type, severity, detected_at, resolved)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    incident.equipment_id,
                    incident.incident_type,
                    incident.severity,
                    incident.detected_at,
                    incident.resolved,
                ),
            )

    def find_all(self) -> list[Incident]:
        with psycopg2.connect(self._dsn) as conn, conn.cursor(
            cursor_factory=RealDictCursor
        ) as cur:
            cur.execute("SELECT * FROM incidents ORDER BY detected_at DESC")
            rows = cur.fetchall()
        return [Incident(**row) for row in rows]
