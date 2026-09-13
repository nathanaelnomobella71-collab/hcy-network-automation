"""Test unitaire de PrometheusExporter (3.9.1).

``core.metrics.INCIDENTS_TOTAL`` est mocké : on vérifie que l'observateur
incrémente bien le compteur avec les bonnes étiquettes (``equipment``,
``type``), sans dépendre du comportement réel de la bibliothèque
``prometheus_client``.
"""
from unittest.mock import patch

from core.models import Incident
from observers.prometheus_exporter import PrometheusExporter


@patch("observers.prometheus_exporter.INCIDENTS_TOTAL")
def test_update_increments_counter_with_equipment_and_type_labels(mock_counter):
    exporter = PrometheusExporter()
    incident = Incident(id=None, equipment_id=42, incident_type="MAC_INTRUSION", severity="HIGH")

    exporter.update(incident)

    mock_counter.labels.assert_called_once_with(equipment="42", type="MAC_INTRUSION")
    mock_counter.labels.return_value.inc.assert_called_once()
