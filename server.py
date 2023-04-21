import socket

from dns_packet import DNSPacket
from dns_parser import Parser


def perform_dns_lookup(query_packet: DNSPacket) -> DNSPacket:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", 3000))
    # Connect to google's DNS server
    sock.connect(("8.8.8.8", 53))
    # Send the Query Packet
    sock.send(query_packet)
    # Receive response
    packet_bytes = sock.recv(600)  # Read 600 bytes only for now
    sock.close()
    return Parser(packet_bytes).get_dns_packet()


if __name__ == "__main__":
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", 5000))
    print("Listening on PORT 5000")
    while True:
        received_bytes, address = sock.recvfrom(600)
        packet: DNSPacket = perform_dns_lookup(bytearray(received_bytes))
        print(packet)
        sock.sendto(packet.to_bin(), address)
