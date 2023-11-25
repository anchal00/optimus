import math
import random
import socket
from typing import List

from dns.dns_packet import DNSHeader, DNSPacket, Question, ResponseCode
from dns.dns_parser import DNSParser
from dns.dns_records import NS, A, Record, RecordClass, RecordType

ROOT_SERVERS = [
    "198.41.0.4",  # a.root-servers.net_ip
    "199.9.14.201",  # b.root-servers.net_ip
    "192.33.4.12",  # c.root-servers.net_ip
    "199.7.91.13",  # d.root-servers.net_ip
    "192.203.230.10",  # e.root-servers.net_ip
    "192.5.5.241",  # f.root-servers.net_ip
    "192.112.36.4",  # g.root-servers.net_ip
    "198.97.190.53",  # h.root-servers.net_ip
    "192.36.148.17",  # i.root-servers.net_ip
    "192.58.128.30",  # j.root-servers.net_ip
    "193.0.14.129",  # k.root-servers.net_ip
    "199.7.83.42",  # l.root-servers.net_ip
    "202.12.27.33",  # m.root-servers.net_ip
]


def __perform_recursive_lookup(qpacket: DNSPacket) -> DNSPacket:
    # Start with first lookup on a random root server
    server_addr = random.choice(ROOT_SERVERS)
    while True:
        response_packet = __perform_dns_lookup(qpacket, server_addr)
        response_code: ResponseCode = response_packet.header.response_code
        # If the server responds with NXDOMAIN or if we get the Answer, return the packet as it is
        if response_code.value == ResponseCode.NXDOMAIN.value:
            return response_packet
        if response_code.value == ResponseCode.NOERROR.value and len(response_packet.answers) > 0:
            return response_packet
        # No NS record is found, we need to return with response packet we already have
        if not response_packet.nameserver_records:
            return response_packet
        # Try to find a 'NS' type record with a corresponding 'A' type record in the additional section
        # If found, switch Nameserver and retry the loop i.e perform the lookup on new NameServer again
        ns_record_set: set = {ns_rec.nsdname for ns_rec in response_packet.nameserver_records}
        additional_records: List[Record] = response_packet.additional_records
        if response_packet.additional_records:
            for ad_rec in additional_records:
                if ad_rec.name in ns_record_set and ad_rec.rtype.value == RecordType.A.value:
                    server_addr = str(ad_rec.address)
                    break
        else:
            # Pick a random NS record and perform lookup for that
            ns_record: NS = random.choice(response_packet.nameserver_records)
            packet: DNSPacket = __perform_recursive_lookup(
                DNSPacket(
                    dns_header=DNSHeader(id=random.randint(0, math.pow(2, 16)-1), is_query=True, question_count=1),
                    questions=[Question(ns_record.nsdname, RecordType.A, RecordClass.IN)]
                )
            )
            # No 'A' Type record is found, we need to return with response packet we already have
            if not packet.answers:
                return response_packet
            a_type_record: A = random.choice(packet.answers)
            # 'A' Type records are present, pick one of them to retry the lookup on new server
            server_addr = str(a_type_record.address)


def __perform_dns_lookup(query_packet: DNSPacket, server_addr: str) -> DNSPacket:
    try:
        dns_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        dns_socket.settimeout(3)
        dns_socket.connect((server_addr, 53))
        dns_socket.send(query_packet.to_bin())
        packet_bytes = dns_socket.recv(600)  # Read 600 bytes only for now
    except TimeoutError:
        print(f"Error: Time out, couldn't complete lookup on {server_addr}")
    finally:
        dns_socket.shutdown(socket.SHUT_RDWR)
        dns_socket.close()
    return DNSParser(packet_bytes).get_dns_packet()


def handle_request(master_socket: socket.socket, received_bytes: bytes, return_address: tuple[str, int]) -> None:
    query_packet: DNSPacket = DNSParser(bytearray(received_bytes)).get_dns_packet()
    print(f"Received query {query_packet.questions[0].name} TYPE {query_packet.questions[0].rtype}")
    if query_packet.header.is_recursion_desired:
        response_packet: DNSPacket = __perform_recursive_lookup(query_packet)
    else:
        response_packet: DNSPacket = __perform_dns_lookup(query_packet, random.choice(ROOT_SERVERS))
    response_packet.header.is_recursion_available = True
    master_socket.sendto(response_packet.to_bin(), return_address)
    print(f"Query for {query_packet.questions[0].name} TYPE {query_packet.questions[0].rtype} successfully processed")
