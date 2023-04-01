from typing import List

from dns_records import Record, RecordClass, RecordType


class DNSHeader:
    ID: int  # 2 bytes
    query_or_response: bool
    opcode: int  # 4 bits
    is_authoritative_answer: bool
    is_truncated_message: bool
    is_recursion_desired: bool
    is_recursion_available: bool
    z_flag: int  # 3 bits
    response_code: int  # 4 bits
    question_count: int  # 2 bytes
    answer_count: int  # 2 bytes
    namserver_records_count: int  # 2 bytes
    additional_records_count: int  # 2 bytes


class Question:
    name: str
    type: RecordType
    ques_class: RecordClass


class DNSPacket:
    def __init__(self):
        self.header: DNSHeader = None
        self.questions: List[Question] = None
        self.answers: List[Record] = None
        self.nameserver_records: List[Record] = None
        self.additional_records: List[Record] = None
