from prometheus_client import Counter, Gauge


# Workflow counters
intent_validation_total = Counter(
    "intent_validation_total",
    "Total number of intent validation attempts."
)

configuration_generation_total = Counter(
    "configuration_generation_total",
    "Total number of configuration generation attempts."
)

netconf_connection_total = Counter(
    "netconf_connection_total",
    "Total number of NETCONF connection attempts."
)

configuration_deployment_total = Counter(
    "configuration_deployment_total",
    "Total number of configuration deployment attempts."
)

configuration_verification_total = Counter(
    "configuration_verification_total",
    "Total number of configuration verification attempts."
)

drift_detection_total = Counter(
    "drift_detection_total",
    "Total number of drift detection checks."
)


# Current status gauges
netconf_connection_status = Gauge(
    "netconf_connection_status",
    "Current NETCONF connection status: 1 for connected, 0 for disconnected."
)

deployment_success = Gauge(
    "deployment_success",
    "Current configuration deployment status: 1 for success, 0 for failure."
)

verification_success = Gauge(
    "verification_success",
    "Current configuration verification status: 1 for success, 0 for failure."
)

configuration_drift_status = Gauge(
    "configuration_drift_status",
    "Current configuration drift status: 0 means no drift, 1 means drift detected."
)


def record_validation(success):
    """Record an intent validation attempt."""
    intent_validation_total.inc()
    return success


def record_configuration_generation():
    """Record a configuration generation attempt."""
    configuration_generation_total.inc()


def record_netconf_connection(success):
    """Record a NETCONF connection attempt and current connection status."""
    netconf_connection_total.inc()
    netconf_connection_status.set(1 if success else 0)


def record_deployment(success):
    """Record a configuration deployment attempt."""
    configuration_deployment_total.inc()
    deployment_success.set(1 if success else 0)


def record_verification(success):
    """Record a configuration verification attempt."""
    configuration_verification_total.inc()
    verification_success.set(1 if success else 0)


def record_drift_check(drift_free):
    """Record a drift detection check."""
    drift_detection_total.inc()
    configuration_drift_status.set(0 if drift_free else 1)
