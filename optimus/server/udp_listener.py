import socket
from concurrent import futures

from optimus.logging.logger import log
from optimus.networking.cache import socket_cache
from optimus.prometheus import with_prometheus_metrics_server
from optimus.server.context import warmup_cache
from optimus.server.router import handle_request


@with_prometheus_metrics_server
@warmup_cache(socket_cache)
def run_forever(port: int, worker_threads: int):
    master_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    master_socket.bind(("0.0.0.0", port))
    log(f"Started Optimus Server on Port {port}")
    # TODO: Test with ProcessPoolExecutor and EPOLL
    try:
        with futures.ThreadPoolExecutor(max_workers=worker_threads) as pool:
            while True:
                received_bytes, address = master_socket.recvfrom(600)
                pool.submit(handle_request, master_socket, received_bytes, address)
    except KeyboardInterrupt:
        log("Goodbye ! Shutting Down the server...")
    finally:
        master_socket.close()
