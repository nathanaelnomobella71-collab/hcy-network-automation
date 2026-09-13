"""NetworkEngine — orchestrateur autonome (Figure 2.4, Extrait 3.4).

Cœur décisionnel du système (RF-01 à RF-04) : s'appuie sur un Collector,
un Analyzer, une RemediationFactory (pattern Strategy) et notifie une liste
d'IIncidentObserver abonnés (pattern Observer) — sans jamais connaître leurs
implémentations concrètes.
"""
from __future__ import annotations

import logging

from core.analyzer import Analyzer
from core.collector import Collector
from core.models import Equipment, Incident
from observers.base import IIncidentObserver
from strategies.factory import RemediationFactory

logger = logging.getLogger(__name__)


class NetworkEngine:
    def __init__(self, collector: Collector, analyzer: Analyzer, factory: RemediationFactory):
        self._collector = collector
        self._analyzer = analyzer
        self._factory = factory
        self._observers: list[IIncidentObserver] = []
        self.running: bool = False

    def register_observer(self, observer: IIncidentObserver) -> None:
        """Abonne un observateur (DatabaseLogger, PrometheusExporter, AlertNotifier...)."""
        self._observers.append(observer)

    def _notify(self, incident: Incident) -> None:
        for observer in self._observers:
            observer.update(incident)

    def handle(self, incident: Incident, device: Equipment) -> None:
        """Sélectionne la stratégie adaptée (Factory), l'exécute, puis notifie
        les observateurs (Observer) — boucle de rétroaction décrite en 1.4.6."""
        strategy = self._factory.create(incident.incident_type)
        result = strategy.execute(device)
        logger.info(
            "Remédiation %s sur %s : succès=%s",
            incident.incident_type,
            device.hostname,
            result.success,
        )
        self._notify(incident)

    def start_polling(self) -> None:
        self.running = True
        logger.info(
            "NetworkEngine démarré (intervalle de polling : %ss)",
            self._collector.polling_interval,
        )

    def stop_engine(self) -> None:
        self.running = False
        logger.info("NetworkEngine arrêté")
