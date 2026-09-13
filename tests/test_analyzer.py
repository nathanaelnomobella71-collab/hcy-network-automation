"""Tests unitaires de l'Analyzer (3.9.1, RF-02/RF-03, Tableau 3.3)."""
from core.analyzer import Analyzer
from core.models import Severity


def test_evaluate_metrics_detects_link_down():
    analyzer = Analyzer()

    incident = analyzer.evaluate_metrics({"equipment_id": 1, "reachable": False})

    assert incident is not None
    assert incident.incident_type == "LINK_DOWN"
    assert incident.severity == Severity.CRITICAL.value


def test_evaluate_metrics_detects_mac_intrusion():
    analyzer = Analyzer()

    incident = analyzer.evaluate_metrics(
        {"equipment_id": 2, "reachable": True, "unauthorized_mac": True}
    )

    assert incident is not None
    assert incident.incident_type == "MAC_INTRUSION"
    assert incident.severity == Severity.HIGH.value


def test_evaluate_metrics_returns_none_when_healthy():
    analyzer = Analyzer()

    incident = analyzer.evaluate_metrics({"equipment_id": 3, "reachable": True})

    assert incident is None


def test_is_critical_flags_high_and_critical_severity():
    analyzer = Analyzer()
    critical_incident = analyzer.evaluate_metrics({"equipment_id": 1, "reachable": False})

    assert analyzer.is_critical(critical_incident) is True


def test_is_critical_returns_false_for_none_without_raising():
    """is_critical(None) doit renvoyer False plutôt que lever AttributeError,
    pour rester chaînable directement avec evaluate_metrics() dans NetworkEngine."""
    analyzer = Analyzer()
    healthy = analyzer.evaluate_metrics({"equipment_id": 3, "reachable": True})

    assert healthy is None
    assert analyzer.is_critical(healthy) is False
