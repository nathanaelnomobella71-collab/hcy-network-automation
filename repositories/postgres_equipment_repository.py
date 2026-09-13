"""PostgresEquipmentRepository — implémentation PostgreSQL de l'inventaire
des équipements (extension du Tableau 2.7, colonnes ``interface`` et
``backup_gateway`` ajoutées pour que les stratégies de remédiation sachent
quelle interface ou quelle passerelle utiliser pour chaque équipement réel).
"""
from __future__ import annotations

import psycopg2
from psycopg2.extras import RealDictCursor

from core.models import Equipment
from repositories.equipment_base import IEquipmentRepository


class PostgresEquipmentRepository(IEquipmentRepository):
    def __init__(self, dsn: str):
        self._dsn = dsn

    def find_all(self) -> list[Equipment]:
        with psycopg2.connect(self._dsn) as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT id, hostname, ip_address, equipment_type, location, status,
                       COALESCE(interface, '') AS interface,
                       COALESCE(backup_gateway, '') AS backup_gateway,
                       COALESCE(lan_subnet, '') AS lan_subnet
                FROM equipments
                ORDER BY id
                """
            )
            rows = cur.fetchall()
        return [Equipment(**row) for row in rows]

    def update_status(self, equipment_id: int, status: str) -> None:
        with psycopg2.connect(self._dsn) as conn, conn.cursor() as cur:
            cur.execute(
                "UPDATE equipments SET status = %s WHERE id = %s",
                (status, equipment_id),
            )
