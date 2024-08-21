import math
import random
from typing import List, Union

from optimus.dns.models.packet import DNSHeader, DNSPacket, Question, ResponseCode
from optimus.dns.parser.parse import DNSParser
from optimus.dns.models.records import AAAA, NS, A, Record, RecordClass, RecordType
from optimus.networking.udp import query_server_over_udp

# TODO: Move to a config file and read from file instead of hardcoding
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


# TODO: Improve logging
def resolve(qpacket: DNSPacket) -> DNSPacket:
    # Start with first lookup on a random root server
    server_addr: str = random.choice(ROOT_SERVERS)
    while True:
        response_packet: DNSPacket = DNSParser(
            bytearray(query_server_over_udp(qpacket.to_bin(), server_addr))
        ).get_dns_packet()
        response_code: ResponseCode = response_packet.header.response_code
        # If the server responds with error or if we get the Answer, return the packet as it is
        if response_code.value in [
            ResponseCode.NXDOMAIN.value,
            ResponseCode.FORMERR.value,
            ResponseCode.SERVFAIL.value,
            ResponseCode.NOTIMP.value,
            ResponseCode.REFUSED.value,
            ResponseCode.UNKNOWN.value,
        ]:
            return response_packet
        if response_code.value == ResponseCode.NOERROR.value and len(response_packet.answers) > 0:
            return response_packet
        # No NS record is found, we need to return with response packet we already have
        if not response_packet.nameserver_records:
            return response_packet
        if not qpacket.header.is_recursion_desired:
            return response_packet
        # Try to find a 'NS' type record with a corresponding 'A' type record in the additional section
        # If found, switch Nameserver and retry the loop i.e perform the lookup on new NameServer again
        ns_record_set: set[str] = {ns_rec.nsdname for ns_rec in response_packet.nameserver_records}
        additional_records: List[Union[A, AAAA, NS]] = response_packet.additional_records
        if additional_records:
            for ad_rec in additional_records:
                if ad_rec.rtype.value == RecordType.A.value and ad_rec.name in ns_record_set:
                    server_addr = str(ad_rec.address)
                    break
        else:
            # Pick a random NS record and perform lookup for that
            ns_record: NS = random.choice(response_packet.nameserver_records)
            packet: DNSPacket = __resolve(
                DNSPacket(
                    dns_header=DNSHeader(
                        id=random.randint(0, int(math.pow(2, 16)) - 1),
                        is_query=True,
                        question_count=1,
                        is_recursion_desired=True,
                    ),
                    questions=[Question(ns_record.nsdname, RecordType.A, RecordClass.IN)],
                )
            )
            # No 'A' Type record is found, we need to return with response packet we already have
            if not packet.answers:
                return response_packet
            a_type_record: Record = random.choice(packet.answers)
            # 'A' Type records are present, pick one of them to retry the lookup on new server
            server_addr = str(a_type_record.address)
