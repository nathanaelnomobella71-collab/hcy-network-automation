"""Tests unitaires des observateurs DatabaseLogger et AlertNotifier (3.9.1).

Ajoutés pour combler un angle mort de couverture : test_engine.py teste que
NetworkEngine notifie ses observateurs, mais aucun test ne vérifiait jusqu'ici
le comportement propre de chaque observateur concret.
"""
from unittest.mock import MagicMock, patch

from core.models import Incident, Severity
from observers.alert_notifier import AlertNotifier
from observers.db_logger import DatabaseLogger


def test_database_logger_delegates_to_repository_save():
    repository = MagicMock()
    logger_observer = DatabaseLogger(repository)
    incident = Incident(id=None, equipment_id=1, incident_type="MAC_INTRUSION", severity="HIGH")

    logger_observer.update(incident)

    repository.save.assert_called_once_with(incident)


@patch("observers.alert_notifier.logger")
def test_alert_notifier_logs_warning_for_critical_severity(mock_logger):
    notifier = AlertNotifier()
    incident = Incident(
        id=None, equipment_id=1, incident_type="LINK_DOWN", severity=Severity.CRITICAL.value
    )

    notifier.update(incident)

    mock_logger.warning.assert_called_once()


@patch("observers.alert_notifier.logger")
def test_alert_notifier_stays_silent_for_low_severity(mock_logger):
    notifier = AlertNotifier()
    incident = Incident(
        id=None, equipment_id=1, incident_type="LINK_DOWN", severity=Severity.LOW.value
    )

    notifier.update(incident)

    mock_logger.warning.assert_not_called()
