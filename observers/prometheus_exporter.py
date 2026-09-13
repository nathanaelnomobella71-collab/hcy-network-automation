"""PrometheusExporter — incrémente les métriques métier (2.7.2, Extrait 3.2).

Dépend de ``core.metrics``, qui nécessite le paquet tiers
``prometheus_client`` (cf. requirements.txt) pour être importé. Testé via
mock du compteur ``INCIDENTS_TOTAL`` (cf. tests/test_prometheus_exporter.py)
plutôt que contre une vraie instance ``prometheus_client``.
"""
from __future__ import annotations

from core.metrics import INCIDENTS_TOTAL
from core.models import Incident
from observers.base import IIncidentObserver


class PrometheusExporter(IIncidentObserver):
    def update(self, incident: Incident) -> None:
        INCIDENTS_TOTAL.labels(
            equipment=str(incident.equipment_id), type=incident.incident_type
        ).inc()
