import socket
from concurrent import futures

from dns.handlers import handle_request
from logging_utils.logger import log


def run_server(port: int, worker_threads: int):
    master_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    master_socket.bind(("0.0.0.0", port))
    log(f"Started Optimus Server on Port {port}")
    with futures.ThreadPoolExecutor(max_workers=worker_threads) as pool:
        while True:
            received_bytes, address = master_socket.recvfrom(600)
            pool.submit(handle_request, master_socket, received_bytes, address)
