"""Tests du Repository (3.9.1, Tableau 3.3).

``psycopg2.connect`` est mocké : ces tests valident la construction des
requêtes SQL et le mapping objet-relationnel, sans dépendre d'une instance
PostgreSQL réelle (cohérent avec l'isolation des dépendances externes
pratiquée pour les stratégies, cf. test_strategies.py).
"""
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from core.models import Incident
from repositories.postgres_repository import PostgresIncidentRepository


@patch("repositories.postgres_repository.psycopg2.connect")
def test_save_executes_insert_with_incident_fields(mock_connect):
    mock_cursor = MagicMock()
    cursor_ctx = mock_connect.return_value.__enter__.return_value.cursor
    cursor_ctx.return_value.__enter__.return_value = mock_cursor
    repo = PostgresIncidentRepository(dsn="postgresql://fake")
    incident = Incident(
        id=None,
        equipment_id=1,
        incident_type="MAC_INTRUSION",
        severity="HIGH",
        detected_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )

    repo.save(incident)

    assert mock_cursor.execute.called
    sql, params = mock_cursor.execute.call_args[0]
    assert "INSERT INTO incidents" in sql
    assert params[0] == 1
    assert params[1] == "MAC_INTRUSION"
    assert params[2] == "HIGH"


@patch("repositories.postgres_repository.psycopg2.connect")
def test_find_all_maps_rows_to_incident_objects(mock_connect):
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [
        {
            "id": 1,
            "equipment_id": 1,
            "incident_type": "MAC_INTRUSION",
            "severity": "HIGH",
            "detected_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
            "resolved": False,
        }
    ]
    cursor_ctx = mock_connect.return_value.__enter__.return_value.cursor
    cursor_ctx.return_value.__enter__.return_value = mock_cursor
    repo = PostgresIncidentRepository(dsn="postgresql://fake")

    incidents = repo.find_all()

    assert len(incidents) == 1
    assert isinstance(incidents[0], Incident)
    assert incidents[0].incident_type == "MAC_INTRUSION"


@patch("repositories.postgres_repository.psycopg2.connect")
def test_find_all_returns_empty_list_when_no_incident(mock_connect):
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = []
    cursor_ctx = mock_connect.return_value.__enter__.return_value.cursor
    cursor_ctx.return_value.__enter__.return_value = mock_cursor
    repo = PostgresIncidentRepository(dsn="postgresql://fake")

    assert repo.find_all() == []
