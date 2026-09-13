"""Tests unitaires du Collector (3.9.1, RF-01).

``subprocess.run`` est mocké : ces tests ne dépendent d'aucune connectivité
réseau réelle, conformément à l'isolation pratiquée pour le reste de la
suite (cf. test_strategies.py).
"""
from unittest.mock import MagicMock, patch

from core.collector import Collector


@patch("core.collector.subprocess.run")
def test_ping_device_returns_true_when_host_responds(mock_run):
    mock_run.return_value = MagicMock(returncode=0)
    collector = Collector()

    assert collector.ping_device("192.168.10.1") is True


@patch("core.collector.subprocess.run")
def test_ping_device_returns_false_when_host_unreachable(mock_run):
    mock_run.return_value = MagicMock(returncode=1)
    collector = Collector()

    assert collector.ping_device("192.168.10.99") is False


@patch("core.collector.subprocess.run", side_effect=OSError("réseau indisponible"))
def test_ping_device_returns_false_on_os_error_instead_of_raising(mock_run):
    """Une erreur système (ex. commande ping absente) ne doit jamais faire
    remonter d'exception jusqu'à l'appelant — cf. RNF-02 (tolérance aux pannes)."""
    collector = Collector()

    assert collector.ping_device("192.168.10.1") is False


def test_check_snmp_status_returns_expected_shape():
    collector = Collector()

    status = collector.check_snmp_status("192.168.10.1")

    assert status["ip"] == "192.168.10.1"
    assert "cpu_usage" in status
    assert "bandwidth_usage" in status


def test_scrape_metrics_reports_configured_polling_interval():
    collector = Collector(polling_interval=10)

    assert collector.scrape_metrics() == {"polling_interval": 10}
