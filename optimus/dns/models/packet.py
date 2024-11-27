from enum import Enum
from typing import List, Optional

from optimus.dns.models.records import Record, RecordClass, RecordType
from optimus.utils import to_n_bytes


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

    @classmethod
    def from_value(cls, value: int):
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
            dns_question_bin.append(len(label))  # TODO: Add check to ensure that label length is <=63
            for ch in label:
                data = ord(ch) if ch != "." else 0
                dns_question_bin.append(data)
        dns_question_bin.append(0)
        # Set Type (In 2 byte format)
        dns_question_bin.extend(to_n_bytes(self.rtype.value, 2))
        # Set Class (In 2 byte format)
        dns_question_bin.extend(to_n_bytes(self.qclass.value, 2))
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
        dns_header_bin: bytearray = bytearray()
        # Represent Id in 2 byte format
        dns_header_bin.extend(to_n_bytes(self.ID, 2))
        # Set QR, RD
        qr_rd_flags = int(not self.is_query) << 7
        qr_rd_flags |= int(self.is_recursion_desired)
        dns_header_bin.append(qr_rd_flags)
        data = int(self.is_recursion_available) << 7
        data = data | (self.z_flag << 4)
        data = data | self.response_code.value
        dns_header_bin.append(data)
        # Set Question Count
        dns_header_bin.extend(to_n_bytes(self.question_count, 2))
        # Set Answer Count
        dns_header_bin.extend(to_n_bytes(self.answer_count, 2))
        # Set NS Records Count
        dns_header_bin.extend(to_n_bytes(self.nameserver_records_count, 2))
        # Set Additional Records Count
        dns_header_bin.extend(to_n_bytes(self.additional_records_count, 2))
        return dns_header_bin

    def __init__(
        self,
        id: int,
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
        dns_header: DNSHeader,
        questions: List[Question],
        answers: Optional[List[Record]] = None,
        nameserver_records: Optional[List[Record]] = None,
        additional_records: Optional[List[Record]] = None,
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
