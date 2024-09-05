from prometheus_client import Counter, start_http_server

from optimus.logging.logger import log


inbound_rqc = Counter("inbound_requests", "Total Requests Received")
served_rqc = Counter("served_requests", "Total Requests Processed")
erred_rqc = Counter("erred_requests", "Total Requests Failed")
PORT = 8000


def record_metrics(func):
    def wrapper(*args, **kwargs):
        inbound_rqc.inc(1)
        was_success: bool = func(*args, **kwargs)
        served_rqc.inc(1)
        if not was_success:
            erred_rqc.inc(1)

    return wrapper


def with_prometheus_monitoring(func):
    def wrapper(*args, **kwargs):
        start_http_server(PORT)
        log(f"Started Prometheus Server on Port {PORT}")
        func(*args, **kwargs)

    return wrapper
