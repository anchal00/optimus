import socket
from concurrent import futures

from optimus_server.handlers import handle_request


def run_server(port: int, worker_threads: int):
    master_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    master_socket.bind(("0.0.0.0", port))
    print(f"Listening on PORT {port}")
    with futures.ThreadPoolExecutor(max_workers=worker_threads) as pool:
        while True:
            received_bytes, address = master_socket.recvfrom(600)
            pool.submit(handle_request, master_socket, received_bytes, address)
