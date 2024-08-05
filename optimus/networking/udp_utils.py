import socket

from optimus.logging_config.logger import log_error


def query_server_over_udp(bin_data: bytearray, server_addr: str) -> bytes:
    """
    Connects to given `server_addr` over UDP on port 53, sends given `bin_data`
    and returns back the response
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(3)
        sock.connect((server_addr, 53))
        sock.send(bin_data)
        packet_bytes = sock.recv(600)  # Read 600 bytes only for now
        return packet_bytes
    except socket.timeout as texc:
        log_error(f"Error: Time out, couldn't complete lookup on {server_addr}")
        raise Exception("Socket Timeout Error") from texc
    except socket.error as err:
        log_error(f"Error: Socket error while connecting to {server_addr}")
        raise Exception("Socket Error") from err
    finally:
        sock.shutdown(socket.SHUT_RDWR)
        sock.close()
