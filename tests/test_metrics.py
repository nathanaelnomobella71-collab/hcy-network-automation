"""Test unitaire de core.metrics (3.9.1, 2.7.2).

``prometheus_client.start_http_server`` est mocké : la logique propre à ce
module (démarrage du serveur d'exportation sur le port demandé) reste
vérifiable sans dépendre du comportement réel du serveur HTTP sous-jacent.
"""
from unittest.mock import patch

from core.metrics import start_metrics_server


@patch("core.metrics.start_http_server")
def test_start_metrics_server_uses_the_requested_port(mock_start_http_server):
    start_metrics_server(port=8000)

    mock_start_http_server.assert_called_once_with(8000)
