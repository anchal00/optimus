
import socket


def query_server(bin_data: bytearray, server_addr: str) -> bytearray:
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
    except TimeoutError:
        print(f"Error: Time out, couldn't complete lookup on {server_addr}")
        return None
    finally:
        sock.shutdown(socket.SHUT_RDWR)
        sock.close()
    return bytearray(packet_bytes)
