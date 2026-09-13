"""Tests unitaires du NetworkEngine — orchestration Factory + notification Observer.

Ajoutés au-delà du plan de tests initial (Tableau 3.3) : ce module reste le
seul point où les patterns Factory et Observer sont exercés ensemble, ce qui
en fait une lacune de couverture à combler explicitement plutôt qu'un
angle mort silencieux.
"""
from unittest.mock import MagicMock

from core.engine import NetworkEngine
from core.models import Equipment, Incident, Result


def test_handle_executes_selected_strategy_and_notifies_observers():
    factory = MagicMock()
    strategy = MagicMock()
    strategy.execute.return_value = Result(success=True, message="ok")
    factory.create.return_value = strategy

    engine = NetworkEngine(collector=MagicMock(), analyzer=MagicMock(), factory=factory)
    observer = MagicMock()
    engine.register_observer(observer)

    device = Equipment(id=1, hostname="sw1", ip_address="10.0.0.1", equipment_type="switch")
    incident = Incident(id=None, equipment_id=1, incident_type="MAC_INTRUSION", severity="HIGH")

    engine.handle(incident, device)

    factory.create.assert_called_once_with("MAC_INTRUSION")
    strategy.execute.assert_called_once_with(device)
    observer.update.assert_called_once_with(incident)


def test_handle_notifies_every_registered_observer_exactly_once():
    """Vérifie le découplage Observer : plusieurs abonnés, tous notifiés, sans ordre imposé.
    """
    factory = MagicMock()
    factory.create.return_value.execute.return_value = Result(success=True, message="ok")
    engine = NetworkEngine(collector=MagicMock(), analyzer=MagicMock(), factory=factory)

    db_logger, prometheus_exporter, alert_notifier = MagicMock(), MagicMock(), MagicMock()
    for observer in (db_logger, prometheus_exporter, alert_notifier):
        engine.register_observer(observer)

    device = Equipment(id=2, hostname="sw2", ip_address="10.0.0.2", equipment_type="switch")
    incident = Incident(id=None, equipment_id=2, incident_type="LINK_DOWN", severity="CRITICAL")

    engine.handle(incident, device)

    db_logger.update.assert_called_once_with(incident)
    prometheus_exporter.update.assert_called_once_with(incident)
    alert_notifier.update.assert_called_once_with(incident)


def test_start_and_stop_polling_toggle_running_flag():
    engine = NetworkEngine(
        collector=MagicMock(polling_interval=5), analyzer=MagicMock(), factory=MagicMock()
    )
    assert engine.running is False

    engine.start_polling()
    assert engine.running is True

    engine.stop_engine()
    assert engine.running is False
