import math
import random
import socket
from typing import List

from dns_packet import DNSHeader, DNSPacket, Question, ResponseCode
from dns_parser import Parser
from dns_records import NS, A, Record, RecordClass, RecordType

D_ROOT_SERVERS_NET_IP = "199.7.91.13"


def perform_recursive_lookup(qpacket: DNSPacket) -> DNSPacket:
    # Start with first lookup on root server D.ROOT-SERVERS.NET
    server_addr = D_ROOT_SERVERS_NET_IP
    while True:
        print(f"Performing DNS lookup on {str(server_addr)} for QNAME {qpacket.questions[0].name} "
              f"TYPE {qpacket.questions[0].rtype}")
        response_packet = perform_dns_lookup(qpacket, server_addr)
        response_code: ResponseCode = response_packet.header.response_code
        # If the server responds with NXDOMAIN, return
        if response_code.value == ResponseCode.NXDOMAIN.value:
            return response_packet
        if response_code.value == ResponseCode.NOERROR.value and len(response_packet.answers) > 0:
            return response_packet
        # No NS record is found, we need to return with response packet we already have
        if not response_packet.nameserver_records:
            return response_packet
        # Try to find a NS with a corresponding A record in the additional section
        # If found, switch NS and retry the loop i.e perform the lookup on new NS again
        ns_record: NS = response_packet.nameserver_records[0]
        additional_records: List[Record] = response_packet.additional_records
        if response_packet.additional_records:
            for ad_rec in additional_records:
                if ad_rec.name == ns_record.nsdname and ad_rec.rtype.value == RecordType.A.value:
                    server_addr = str(ad_rec.address)
                    break
        else:
            packet: DNSPacket = perform_recursive_lookup(
                DNSPacket(
                    dns_header=DNSHeader(id=random.randint(0, math.pow(2, 16)-1), is_query=True, question_count=1),
                    questions=[Question(ns_record.nsdname, RecordType.A, RecordClass.IN)]
                )
            )
            # No A record is found, we need to return with response packet we already have
            if not packet.answers:
                return response_packet
            a_record: A = packet.answers[0]
            # A records are present, pick one of them to retry the lookup on new server
            server_addr = str(a_record.address)


def perform_dns_lookup(query_packet: DNSPacket, server_addr: str) -> DNSPacket:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", 3000))
    # Connect to google's DNS server
    sock.connect((server_addr, 53))
    # Send the Query Packet
    sock.send(query_packet.to_bin())
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
        query_packet: DNSPacket = Parser(bytearray(received_bytes)).get_dns_packet()
        print(f"Received query {query_packet.questions[0].name} TYPE {query_packet.questions[0].rtype}")
        if query_packet.header.is_recursion_desired:
            response_packet: DNSPacket = perform_recursive_lookup(query_packet)
        else:
            response_packet: DNSPacket = perform_dns_lookup(query_packet, D_ROOT_SERVERS_NET_IP)
        response_packet.header.is_recursion_available = True
        sock.sendto(response_packet.to_bin(), address)
