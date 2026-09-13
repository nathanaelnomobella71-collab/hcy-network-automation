"""Tests du Repository d'équipements (extension du Chapitre 3, 3.9.1),
mêmes principes d'isolation que test_repository.py (psycopg2 mocké).
"""
from unittest.mock import MagicMock, patch

from core.models import Equipment
from repositories.postgres_equipment_repository import PostgresEquipmentRepository


@patch("repositories.postgres_equipment_repository.psycopg2.connect")
def test_find_all_maps_rows_to_equipment_objects(mock_connect):
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [
        {
            "id": 4, "hostname": "sw-caisse", "ip_address": "192.168.10.5",
            "equipment_type": "switch_acces", "location": "Caisse centrale",
            "status": "UP", "interface": "FastEthernet0/1", "backup_gateway": "",
        }
    ]
    mock_connect.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value = mock_cursor
    repo = PostgresEquipmentRepository(dsn="postgresql://fake")

    equipment = repo.find_all()

    assert len(equipment) == 1
    assert isinstance(equipment[0], Equipment)
    assert equipment[0].hostname == "sw-caisse"
    assert equipment[0].interface == "FastEthernet0/1"


@patch("repositories.postgres_equipment_repository.psycopg2.connect")
def test_update_status_executes_update_with_correct_params(mock_connect):
    mock_cursor = MagicMock()
    mock_connect.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value = mock_cursor
    repo = PostgresEquipmentRepository(dsn="postgresql://fake")

    repo.update_status(equipment_id=4, status="DOWN")

    sql, params = mock_cursor.execute.call_args[0]
    assert "UPDATE equipments" in sql
    assert params == ("DOWN", 4)


@patch("repositories.postgres_equipment_repository.psycopg2.connect")
def test_find_all_returns_empty_list_when_table_empty(mock_connect):
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = []
    mock_connect.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value = mock_cursor
    repo = PostgresEquipmentRepository(dsn="postgresql://fake")

    assert repo.find_all() == []
