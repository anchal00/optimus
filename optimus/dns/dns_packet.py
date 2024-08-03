from enum import Enum
from typing import List, Optional

from optimus.dns.dns_records import Record, RecordClass, RecordType, NS, A, AAAA, NS


class ResponseCode(Enum):  # 4 bits
    NOERROR = 0

    FORMERR = 1  # The name server was unable to interpret the query

    SERVFAIL = 2  # The name server was unable to process this query due to a problem with the name server.

    # Meaningful only for responses from an authoritative N server.
    # This code signifies that the domain name referenced in the query does not exist.
    NXDOMAIN = 3

    NOTIMP = 4  # The name server does not support the requested kind of query.

    # The name server refuses to perform the specified operation for
    # policy reasons.  For example, a name server may not wish to provide the
    # information to the particular requester, or a name server may not wish to perform
    # a particular operation (e.g., zone transfer) for particular data.
    REFUSED = 5

    UNKNOWN = -1

    def from_value(value: int):
        for rec in ResponseCode:
            if rec.value == value:
                return rec
        return ResponseCode.UNKNOWN


class Question:
    name: str
    rtype: RecordType
    qclass: RecordClass

    def __init__(self, name: str, rtype: RecordType, qclass: RecordClass) -> None:
        self.name = name
        self.rtype = rtype
        self.qclass = qclass

    def to_bin(self) -> bytearray:
        dns_question_bin: bytearray = bytearray(0)
        labels = self.name.split(".")
        for label in labels:
            # Write label's length
            dns_question_bin.append(
                len(label)
            )  # TODO: Add check to ensure that label length is <=63
            for ch in label:
                data = ord(ch) if ch != "." else 0
                dns_question_bin.append(data)
        dns_question_bin.append(0)
        # Set Type (In 2 byte format)
        dns_question_bin.append((self.rtype.value & 0xFF00) >> 8)
        dns_question_bin.append(self.rtype.value & 0xFF)
        # Set Class (In 2 byte format)
        dns_question_bin.append((self.qclass.value & 0xFF00) >> 8)
        dns_question_bin.append(self.qclass.value & 0xFF)
        return dns_question_bin

    def __repr__(self) -> str:
        rep_dict = {
            "name": self.name,
            "type": self.rtype.name,
            "class": self.qclass.name,
        }
        return str(rep_dict)


class DNSHeader:
    ID: int  # 2 bytes
    is_query: bool
    opcode: int  # 4 bits
    is_authoritative_answer: bool
    is_truncated_message: bool
    is_recursion_desired: bool
    is_recursion_available: bool
    z_flag: int  # 3 bits
    response_code: ResponseCode  # 4 bits
    question_count: int  # 2 bytes
    answer_count: int  # 2 bytes
    nameserver_records_count: int  # 2 bytes
    additional_records_count: int  # 2 bytes

    def to_bin(self) -> bytearray:
        dns_header_bin: bytearray = bytearray(12)
        # Represent Id in 2 byte format
        id_msbyte: int = (self.ID & 0xFF00) >> 8
        id_lsbyte: int = self.ID & 0xFF
        dns_header_bin[0] = id_msbyte
        dns_header_bin[1] = id_lsbyte
        # Set QR, RD
        data = (0 if self.is_query else 1) << 7
        data = data | (1 if self.is_recursion_desired else 0)
        dns_header_bin[2] = data
        data = (1 if self.is_recursion_available else 0) << 7
        data = data | (self.z_flag << 4)
        data = data | self.response_code.value
        dns_header_bin[3] = data
        # Set Question Count
        dns_header_bin[4] = (self.question_count & 0xFF00) >> 8
        dns_header_bin[5] = self.question_count & 0xFF
        # Set Answer Count
        dns_header_bin[6] = (self.answer_count & 0xFF00) >> 8
        dns_header_bin[7] = self.answer_count & 0xFF
        # Set NS Records Count
        dns_header_bin[8] = (self.nameserver_records_count & 0xFF00) >> 8
        dns_header_bin[9] = self.nameserver_records_count & 0xFF
        # Set Additional Records Count
        dns_header_bin[10] = (self.additional_records_count & 0xFF00) >> 8
        dns_header_bin[11] = self.additional_records_count & 0xFF
        return dns_header_bin

    def __init__(
        self,
        id: int = None,
        is_query: bool = False,
        opcode: int = 0,
        is_authoritative_answer: bool = False,
        is_truncated_message: bool = False,
        is_recursion_desired: bool = False,
        is_recursion_available: bool = False,
        z_flag: int = 0,
        response_code: Optional[ResponseCode] = None,
        question_count: int = 0,
        answer_count: int = 0,
        nameserver_records_count: int = 0,
        additional_records_count: int = 0,
    ) -> None:
        self.ID = id
        self.is_query = is_query
        self.opcode = opcode
        self.is_authoritative_answer = is_authoritative_answer
        self.is_truncated_message = is_truncated_message
        self.is_recursion_desired = is_recursion_desired
        self.is_recursion_available = is_recursion_available
        self.z_flag = z_flag
        self.response_code = response_code or ResponseCode.from_value(0)
        self.question_count = question_count
        self.answer_count = answer_count
        self.nameserver_records_count = nameserver_records_count
        self.additional_records_count = additional_records_count

    def __repr__(self) -> str:
        rep_dict = {
            "ID": self.ID,
            "is_query": self.is_query,
            "opcode": self.opcode,
            "is_authoritative_answer": self.is_authoritative_answer,
            "is_truncated_message": self.is_truncated_message,
            "is_recursion_desired": self.is_recursion_desired,
            "is_recursion_available": self.is_recursion_available,
            "z_flag": self.z_flag,
            "rcode": self.response_code.name,
            "question_count": self.question_count,
            "answer_count": self.answer_count,
            "nameserver_records_count": self.nameserver_records_count,
            "additional_records_count": self.additional_records_count,
        }
        return str(rep_dict)


class DNSPacket:
    def __init__(
        self,
        dns_header: DNSHeader = None,
        questions: List[Question] = None,
        answers: List[Record] = None,
        nameserver_records: List[NS] = None,
        additional_records: List[A | AAAA | NS ] = None,
    ) -> None:
        self.header = dns_header
        self.questions = questions if questions else []
        self.answers = answers if answers else []
        self.nameserver_records = nameserver_records if nameserver_records else []
        self.additional_records = additional_records if additional_records else []

    def to_bin(self) -> bytearray:
        dns_packet_bin: bytearray = bytearray(0)
        if self.header:
            dns_packet_bin.extend(self.header.to_bin())
        if self.questions:
            for question in self.questions:
                dns_packet_bin.extend(question.to_bin())
        if self.answers:
            for answer in self.answers:
                dns_packet_bin.extend(answer.to_bin())
        if self.nameserver_records:
            for ns_record in self.nameserver_records:
                dns_packet_bin.extend(ns_record.to_bin())
        if self.additional_records:
            for ad_record in self.additional_records:
                dns_packet_bin.extend(ad_record.to_bin())
        return dns_packet_bin

    def __repr__(self) -> str:
        rep_dict = {
            "header": self.header,
            "questions": self.questions,
            "answers": self.answers,
            "authoritative_records": self.nameserver_records,
            "additional_records": self.additional_records,
        }
        return str(rep_dict)
