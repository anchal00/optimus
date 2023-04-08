from typing import List

from dns_records import Record, RecordClass, RecordType
from utils.parsing_utils import Parser


class DNSHeader:
    ID: int  # 2 bytes
    is_query: bool
    opcode: int  # 4 bits
    is_authoritative_answer: bool
    is_truncated_message: bool
    is_recursion_desired: bool
    is_recursion_available: bool
    z_flag: int  # 3 bits
    response_code: int  # 4 bits
    question_count: int  # 2 bytes
    answer_count: int  # 2 bytes
    nameserver_records_count: int  # 2 bytes
    additional_records_count: int  # 2 bytes

    def __init__(self, parser: Parser):
        # Parse ID
        self.ID = parser.parse_bytes_and_move_ahead(2)
        bytes_data = parser.parse_bytes_and_move_ahead(2)
        left_byte = bytes_data & 0xFF00
        right_byte = bytes_data & 0xFF
        # Parse QR
        self.is_query = (left_byte & 1 << 7) != 0
        # Parse OPCODE
        self.opcode = (left_byte >> 3) & 0x0F
        # Parse AA
        self.is_authoritative_answer = left_byte & (1 << 2) != 0
        # Parse TC
        self.is_truncated_message = left_byte & (1 << 1) != 0
        # Parse RD
        self.is_recursion_desired = left_byte & 1 != 0
        # Parse RA
        self.is_recursion_available = right_byte & (1 << 7) != 0
        # Parse Z
        self.z_flag = (right_byte >> 4) & 7
        # Parse RC
        self.response_code = (right_byte >> 3) & 0x0F
        # Parse Record counts
        ques_count_data = parser.parse_bytes_and_move_ahead(2)
        self.question_count = ques_count_data
        ans_count_data = parser.parse_bytes_and_move_ahead(2)
        self.answer_count = ans_count_data
        ns_count_data = parser.parse_bytes_and_move_ahead(2)
        self.nameserver_records_count = ns_count_data
        ad_count_data = parser.parse_bytes_and_move_ahead(2)
        self.additional_records_count = ad_count_data

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
            "rcode": self.response_code,
            "question_count": self.question_count,
            "answer_count": self.answer_count,
            "nameserver_records_count": self.nameserver_records_count,
            "additional_records_count": self.additional_records_count,
        }
        return str(rep_dict)


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

    def create(self, parser: Parser):
        self.header = DNSHeader(parser)
