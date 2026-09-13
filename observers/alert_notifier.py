"""AlertNotifier — canal d'alerte hors-bande (cf. 1.4.7).

Implémentation de référence : journalise l'alerte à un niveau WARNING pour
les incidents HIGH/CRITICAL. À substituer en production par un connecteur
SMS ou WhatsApp réel (perspective retenue en Conclusion générale), sans
modifier NetworkEngine ni les autres observateurs — c'est tout l'intérêt du
pattern Observer (Chapitre 1, 1.2.1).
"""
from __future__ import annotations

import logging

from core.models import Incident, Severity
from observers.base import IIncidentObserver

logger = logging.getLogger(__name__)


class AlertNotifier(IIncidentObserver):
    def update(self, incident: Incident) -> None:
        if incident.severity in (Severity.HIGH.value, Severity.CRITICAL.value):
            logger.warning(
                "ALERTE HORS-BANDE [%s] équipement=%s type=%s",
                incident.severity,
                incident.equipment_id,
                incident.incident_type,
            )
