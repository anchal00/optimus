from typing import List

from dns_packet import DNSHeader, DNSPacket, Question
from dns_records import Record


class Parser:
    def __init__(self, bin_data: bytearray) -> None:
        self.__bin_data_block = bin_data
        self.__ptr = 0

    def __increment_ptr(self, steps: int) -> None:
        self.__ptr = self.__ptr + steps

    def __parse_bytes_and_move_ahead(self, bytes_to_parse: int) -> int:
        to_be_read_data_block = self.__bin_data_block[self.__ptr:]
        data = 0
        for x in to_be_read_data_block[:bytes_to_parse]:
            data = data << 8 | x
            self.__increment_ptr(1)
        return data

    def __get_dns_header(self) -> DNSHeader:
        # Parse ID
        id = self.__parse_bytes_and_move_ahead(2)
        bytes_data = self.__parse_bytes_and_move_ahead(2)
        msb_byte = bytes_data & 0xFF00
        lsb_byte = bytes_data & 0xFF
        # Parse QR
        is_query = (msb_byte >> 8) & (1 << 7) == 0
        # Parse OPCODE
        opcode = (msb_byte >> 3) & 0x0F
        # Parse AA
        is_authoritative_answer = msb_byte & (1 << 2) != 0
        # Parse TC
        is_truncated_message = msb_byte & (1 << 1) != 0
        # Parse RD
        is_recursion_desired = msb_byte & 1 != 0
        # Parse RA
        is_recursion_available = lsb_byte & (1 << 7) != 0
        # Parse Z
        z_flag = (lsb_byte >> 4) & 7
        # Parse RC
        response_code = (lsb_byte >> 3) & 0x0F
        # Parse Record counts
        question_count = self.__parse_bytes_and_move_ahead(2)
        answer_count = self.__parse_bytes_and_move_ahead(2)
        nameserver_records_count = self.__parse_bytes_and_move_ahead(2)
        additional_records_count = self.__parse_bytes_and_move_ahead(2)
        return DNSHeader(
            id,
            is_query,
            opcode,
            is_authoritative_answer,
            is_truncated_message,
            is_recursion_desired,
            is_recursion_available,
            z_flag,
            response_code,
            question_count,
            answer_count,
            nameserver_records_count,
            additional_records_count
        )

    def __get_ques_section(self) -> List[Question]:
        ...

    def __get_ans_section(self) -> List[Record]:
        ...

    def __get_additional_section(self) -> List[Record]:
        ...

    def __get_authoritative_section(self) -> List[Record]:
        ...

    def get_dns_packet(self):
        if self.__bin_data_block is None:
            raise Exception("Data not found")
        dns_header: DNSHeader = self.__get_dns_header()
        questions: List[Question] = self.__get_ques_section()
        answers: List[Record] = self.__get_ans_section()
        nameserver_records: List[Record] = self.__get_authoritative_section()
        additional_records: List[Record] = self.__get_additional_section()
        return DNSPacket(dns_header, questions, answers, nameserver_records, additional_records)
