import math
import random
from typing import List, Union

from optimus.dns.models.packet import DNSHeader, DNSPacket, Question, ResponseCode
from optimus.dns.parser.parse import DNSParser
from optimus.dns.models.records import AAAA, NS, A, Record, RecordClass, RecordType
from optimus.networking.udp import query_server_over_udp
from optimus.optimus_server.context import get_root_servers


# TODO: Improve logging
def resolve(qpacket: DNSPacket) -> DNSPacket:
    # Start with first lookup on a random root server
    server_addr: str = random.choice(get_root_servers())
    while True:
        _bytes: bytes = query_server_over_udp(qpacket.to_bin(), server_addr)
        if not _bytes:
            return DNSPacket(
                DNSHeader(
                    id=qpacket.header.ID,
                    question_count=qpacket.header.question_count,
                    response_code=ResponseCode.SERVFAIL,
                ),
                questions=qpacket.questions,
            )
        response_packet: DNSPacket = DNSParser(bytearray(_bytes)).get_dns_packet()
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
        ns_records: List[NS] = list(filter(lambda rec: rec.rtype == RecordType.NS, response_packet.nameserver_records))
        ns_record_set: set[str] = {ns_rec.nsdname for ns_rec in ns_records}
        additional_records: List[Union[A, AAAA, NS]] = response_packet.additional_records
        if additional_records:
            for ad_rec in additional_records:
                if ad_rec.rtype.value == RecordType.A.value and ad_rec.name in ns_record_set:
                    server_addr = str(ad_rec.address)
                    break
        else:
            if not ns_records:
                return response_packet
            # Pick a random NS record and perform lookup for that
            ns_record: NS = random.choice(ns_records)
            packet: DNSPacket = resolve(
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
