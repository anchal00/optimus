from typing import List

from dns_records import Record, RecordClass, RecordType


class Question:
    name: str
    rtype: RecordType
    qclass: RecordClass

    def __init__(self, name: str, rtype: RecordType, qclass: RecordClass) -> None:
        self.name = name
        self.rtype = rtype
        self.qclass = qclass

    def __repr__(self) -> str:
        rep_dict = {
            "name": self.name,
            "type": self.rtype.name,
            "class": self.qclass.name
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
    response_code: int  # 4 bits
    question_count: int  # 2 bytes
    answer_count: int  # 2 bytes
    nameserver_records_count: int  # 2 bytes
    additional_records_count: int  # 2 bytes

    def __init__(
        self, id: int,
        is_query: bool,
        opcode: int,
        is_authoritative_answer: bool,
        is_truncated_message: bool,
        is_recursion_desired: bool,
        is_recursion_available: bool,
        z_flag: int,
        response_code: int,
        question_count: int,
        answer_count: int,
        nameserver_records_count: int,
        additional_records_count: int
    ) -> None:
        self.ID = id
        self.is_query = is_query
        self.opcode = opcode
        self.is_authoritative_answer = is_authoritative_answer
        self.is_truncated_message = is_truncated_message
        self.is_recursion_desired = is_recursion_desired
        self.is_recursion_available = is_recursion_available
        self.z_flag = z_flag
        self.response_code = response_code
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
            # TODO: create Response Enum
            "rcode": self.response_code,
            "question_count": self.question_count,
            "answer_count": self.answer_count,
            "nameserver_records_count": self.nameserver_records_count,
            "additional_records_count": self.additional_records_count,
        }
        return str(rep_dict)


class DNSPacket:
    def __init__(
        self, dns_header: DNSHeader,
        questions: List[Question],
        answers: List[Record],
        nameserver_records: List[Record],
        additional_records: List[Record]
    ) -> None:
        self.header = dns_header
        self.questions = questions
        self.answers = answers
        self.nameserver_records = nameserver_records
        self.additional_records = additional_records

    def __repr__(self) -> str:
        rep_dict = {
            "header": self.header,
            "questions": self.questions,
            "answers": self.answers,
            "authoritative_records": self.nameserver_records,
            "additional_records": self.additional_records
        }
        return str(rep_dict)
