from multiprocessing import Process
import socket
import select
from typing import Tuple, List
from ipaddress import IPv4Address
from optimus.dns.handlers import handle_request
from optimus.logging_config.logger import log


def run_server(port: int, worker_threads: int):
    master_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    master_socket.bind(("0.0.0.0", port))
    master_socket.setblocking(False)
    log(f"Started Optimus Server on Port {port}")
    # TODO: Switch to ProcessPoolExecutor, as ThreadPool does not benefit in this case
    # with futures.ProcessPoolExecutor(max_workers=worker_threads) as pool:
    # while True:
    # received_bytes, address = master_socket.recvfrom(600)
    # pool.submit(handle_request, master_socket, received_bytes, address)
    _run_forever(master_socket)


def _run_forever(master_socket: socket.socket):
    epoll: select.epoll = select.epoll()
    epoll.register(
        fd=master_socket.fileno(), eventmask=(select.POLLIN | select.EPOLLET)
    )
    try:
        while True:
            events: List[Tuple[int, int]] = epoll.poll(1)
            for file_number, event in events:
                input_data_bytes: bytes = b""
                client_address: IPv4Address
                while True:
                    try:
                        data, client_address = master_socket.recvfrom(512)
                        if data:
                            input_data_bytes += data
                    except BlockingIOError:
                        log("enough data read")
                        break
                Process(
                    target=handle_request,
                    name=f"optimus_worker_{client_address}",
                    args=(master_socket, input_data_bytes, client_address),
                ).start()

    except KeyboardInterrupt:
        log("Shutting Down the server")
    finally:
        epoll.unregister(master_socket.fileno())
        epoll.close()
        master_socket.close()
