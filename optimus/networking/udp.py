from typing import Optional
from optimus.networking.cache import socket_cache
import socket

from optimus.logging.logger import log_error


def query_server_over_udp(bin_data: bytearray, server_addr: str) -> bytes:
    try:
        sock: Optional[socket.socket] = socket_cache.get(server_addr)
        if not sock:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(5)
            sock.connect((server_addr, 53))
            socket_cache.put(server_addr, sock)
        sock.send(bin_data)
        packet_bytes = sock.recv(600)
        return packet_bytes
    except socket.timeout:
        log_error(f"Error: Time out, couldn't complete lookup on {server_addr}")
        return bytes()
    except socket.error:
        log_error(f"Error: Socket error while connecting to {server_addr}")
        return bytes()
