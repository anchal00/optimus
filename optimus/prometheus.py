from prometheus_client import Counter, Histogram, start_http_server

from optimus.logging.logger import log

inbound_rqc = Counter("inbound_dns_requests", "Total Requests Received")
served_rqc = Counter("served_dns_requests", "Total Requests Processed")
erred_rqc = Counter("erred_dns_requests", "Total Requests Failed")

req_duration_hist = Histogram("duration_dns_request", "Total time taken to process the request")

PORT = 8000


def record_metrics(func):
    """
    Requires a running Prometheus Metrics server
    TODO: Check whether Prometheus server is up and running on `PORT`
    """

    @req_duration_hist.time()
    def wrapper(*args, **kwargs):
        inbound_rqc.inc(1)
        was_success: bool = func(*args, **kwargs)
        served_rqc.inc(1)
        if not was_success:
            erred_rqc.inc(1)

    return wrapper


def with_prometheus_metrics_server(func):
    def wrapper(*args, **kwargs):
        start_http_server(PORT)
        log(f"Started Prometheus Server on Port {PORT}")
        func(*args, **kwargs)

    return wrapper
