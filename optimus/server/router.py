import socket

from optimus.dns.models.packet import DNSPacket, ResponseCode
from optimus.dns.parser.parse import DNSParser
from optimus.dns.resolver import resolve
from optimus.logging.logger import log, log_error
from optimus.prometheus import record_metrics


@record_metrics
def handle_request(master_socket: socket.socket, received_bytes: bytes, return_address: tuple[str, int]) -> bool:
    query_packet: DNSPacket = DNSParser(bytearray(received_bytes)).get_dns_packet()
    log(f"Received query for {query_packet.questions[0].name} TYPE {query_packet.questions[0].rtype}")
    response_packet: DNSPacket = resolve(query_packet)
    response_packet.header.is_recursion_available = True
    master_socket.sendto(response_packet.to_bin(), return_address)
    if response_packet.header.response_code != ResponseCode.NOERROR:
        log_error(f"Query for {query_packet.questions[0].name} TYPE {query_packet.questions[0].rtype} errored out")
        return False
    log(f"Query for {query_packet.questions[0].name} TYPE {query_packet.questions[0].rtype} successfully processed")
    return True
