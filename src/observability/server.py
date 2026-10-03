from prometheus_client import start_http_server


def start_metrics_server(port=8000):
    """Start the Prometheus metrics HTTP endpoint."""
    start_http_server(port)
    print(f"Prometheus metrics server started on port {port}.")
