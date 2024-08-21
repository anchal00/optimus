import socket
from concurrent import futures

from optimus.optimus_server.router import handle_request
from optimus.logging.logger import log


def run_udp_listener(port: int, worker_threads: int):
    master_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    master_socket.bind(("0.0.0.0", port))
    log(f"Started Optimus Server on Port {port}")
    # TODO: Test with Process PoolExecutor and EPOLL
    try:
        with futures.ThreadPoolExecutor(max_workers=worker_threads) as pool:
            while True:
                received_bytes, address = master_socket.recvfrom(600)
                pool.submit(handle_request, master_socket, received_bytes, address)
    except KeyboardInterrupt:
        log("Goodbye ! Shutting Down the server...")
    finally:
        master_socket.close()
