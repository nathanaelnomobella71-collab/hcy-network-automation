"""Analyzer — analyse et qualification des incidents (RF-02, RF-03, Figure 2.4)."""
from __future__ import annotations

from core.models import Incident, IncidentType, Severity


class Analyzer:
    """Évalue les métriques collectées et qualifie les incidents détectés."""

    def __init__(self, cpu_threshold: float = 95.0):
        self.thresholds = {"cpu_usage": cpu_threshold}

    def evaluate_metrics(self, data: dict) -> Incident | None:
        """Qualifie un incident à partir des métriques collectées (RF-02/RF-03).

        ``data`` est le dictionnaire produit par le Collector, enrichi des
        indicateurs bruts (joignabilité, adresses MAC observées, charge). La
        méthode renvoie ``None`` lorsqu'aucune anomalie n'est détectée — RF-02
        couvre trois catégories (ruptures de liens, saturation, équipements
        non autorisés) ; seules les deux premières sont câblées ci-dessous, la
        détection de saturation restant à raccorder à un seuil de bande
        passante (cf. Chapitre 4, 4.1.2, écart identifié sur ce point).
        """
        if data.get("reachable") is False:
            return Incident(
                id=None,
                equipment_id=data["equipment_id"],
                incident_type=IncidentType.LINK_DOWN.value,
                severity=Severity.CRITICAL.value,
            )
        if data.get("unauthorized_mac"):
            return Incident(
                id=None,
                equipment_id=data["equipment_id"],
                incident_type=IncidentType.MAC_INTRUSION.value,
                severity=Severity.HIGH.value,
            )
        return None

    def is_critical(self, issue: Incident | None) -> bool:
        """Qualification de criticité (cf. Figure 3.2, étape 5 : « Qualification HAUTE »).

        Renvoie ``False`` si ``issue`` est ``None`` (aucune anomalie détectée)
        plutôt que de lever une exception : NetworkEngine peut ainsi enchaîner
        ``is_critical(analyzer.evaluate_metrics(...))`` sans garde-fou séparé.
        """
        if issue is None:
            return False
        return issue.severity in (Severity.HIGH.value, Severity.CRITICAL.value)
