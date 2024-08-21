import socket
from optimus.dns.models.packet import DNSPacket
from optimus.dns.parser.parse import DNSParser
from optimus.logging.logger import log
from optimus.dns.resolver import resolve


def handle_request(master_socket: socket.socket, received_bytes: bytes, return_address: tuple[str, int]) -> None:
    query_packet: DNSPacket = DNSParser(bytearray(received_bytes)).get_dns_packet()
    # TODO: Send query for each question in query_packet
    log(f"Received query for {query_packet.questions[0].name} TYPE {query_packet.questions[0].rtype}")
    response_packet: DNSPacket = resolve(query_packet)
    response_packet.header.is_recursion_available = True
    master_socket.sendto(response_packet.to_bin(), return_address)
    log(f"Query for {query_packet.questions[0].name} TYPE {query_packet.questions[0].rtype} successfully processed")
