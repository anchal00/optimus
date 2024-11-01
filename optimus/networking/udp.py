import socket
from typing import Optional

from optimus.logging.logger import log_error
from optimus.networking.cache import socket_cache


def query_server_over_udp(payload: bytearray, server_addr: str) -> bytes:
    sock: Optional[socket.socket] = socket_cache.get(server_addr)
    is_root_server = True
    try:
        if not sock:
            is_root_server = False
            log_error(f"Upstream DNS server {server_addr} socket cache miss")
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(5)
            sock.connect((server_addr, 53))
        sock.send(payload)
        packet_bytes = sock.recv(600)
        return packet_bytes
    except socket.timeout:
        log_error(f"Time out, couldn't complete lookup on {server_addr}")
        return bytes()
    except socket.error:
        log_error(f"Socket error while connecting to {server_addr}")
        return bytes()
    finally:
        if sock and not is_root_server:
            # Only close sockets for non-root servers since root server sockets have
            # to remain cached and can't be closed
            sock.close()
