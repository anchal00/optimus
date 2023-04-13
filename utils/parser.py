from ipaddress import IPv4Address
from typing import List

from dns_packet import DNSHeader, DNSPacket, Question
from dns_records import A, Record, RecordClass, RecordType


class Parser:
    def __init__(self, bin_data: bytearray) -> None:
        self.__bin_data_block = bin_data
        self.__ptr = 0

    def __increment_ptr(self, steps: int) -> None:
        self.__ptr += steps

    def __seek_ptr_pos(self, pos: int) -> None:
        self.__ptr = pos

    def __parse_bytes_and_move_ahead(self, bytes_to_parse: int) -> int:
        to_be_read_data_block = self.__bin_data_block[self.__ptr:]
        data = 0
        for x in to_be_read_data_block[:bytes_to_parse]:
            data = data << 8 | x
            self.__increment_ptr(1)
        return data

    def __parse_record_name(self) -> str:
        msb_data: int = self.__parse_bytes_and_move_ahead(1)
        if msb_data ^ 0xC0 == 0:
            # If the First Byte (MSB) has two leftmost(MS) bits set then
            # the name is represented in Compressed format.
            # So in this case, the next byte should be treated as OFFSET
            # which specifies the position from where the name has to be
            # read
            offset: int = self.__parse_bytes_and_move_ahead(1)
            cur_ptr_pos: int = self.__ptr
            self.__seek_ptr_pos(offset)
            name: str = self.__parse_sequence_of_labels()
            # Restore pointer to where it was
            self.__seek_ptr_pos(cur_ptr_pos)
            return name
        return self.__parse_sequence_of_labels()

    def __parse_sequence_of_labels(self) -> str:
        full_name: List = []
        name_str: str = ''
        # 2 MSB bits of the this label_length field are always 0
        # So the label_length can have values between 0 and 63, meaning
        # that the name can take only between 0-63 octets
        label_length: int = self.__parse_bytes_and_move_ahead(1)
        # Parse sequence of labels to decode the Name
        while label_length != 0:
            for _ in range(0, label_length):
                label: int = self.__parse_bytes_and_move_ahead(1)
                name_str = name_str + chr(label)
            full_name.append(name_str)
            name_str = ''
            label_length: int = self.__parse_bytes_and_move_ahead(1)
        return '.'.join(full_name)

    def __get_dns_header(self) -> DNSHeader:
        # Parse ID
        id = self.__parse_bytes_and_move_ahead(2)
        bytes_data = self.__parse_bytes_and_move_ahead(2)
        msb_byte = (bytes_data & 0xFF00) >> 8
        lsb_byte = bytes_data & 0xFF
        # Parse QR
        is_query = msb_byte & (1 << 7) == 0
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

    def __get_ques_section(self, total_questions) -> List[Question]:
        questions: List[Question] = []
        for _ in range(0, total_questions):
            # Parse name
            name: str = self.__parse_sequence_of_labels()
            # Parse type
            rtype: RecordType = RecordType.from_value(self.__parse_bytes_and_move_ahead(2))
            # Parse class
            qclass: RecordClass = RecordClass.from_value(self.__parse_bytes_and_move_ahead(2))
            questions.append(Question(name, rtype, qclass))
        return questions

    def __read_ans(self) -> Record:
        name: str = self.__parse_record_name()
        rtype: RecordType = RecordType.from_value(self.__parse_bytes_and_move_ahead(2))
        rclass: RecordClass = RecordClass.from_value(self.__parse_bytes_and_move_ahead(2))
        ttl: int = self.__parse_bytes_and_move_ahead(4)
        length: int = self.__parse_bytes_and_move_ahead(2)
        record: Record = None
        # Parse record acc to RecordType
        if rtype == RecordType.A:
            ipv4_addr_int: int = self.__parse_bytes_and_move_ahead(4)
            record: Record = A(name, rtype, rclass, ttl, length, IPv4Address(ipv4_addr_int))
        return record

    def __get_ans_section(self, total_answers: int) -> List[Record]:
        answers: List[Record] = []
        for _ in range(0, total_answers):
            answers.append(self.__read_ans())
        return answers

    def __get_additional_section(self) -> List[Record]:
        ...

    def __get_authoritative_section(self) -> List[Record]:
        ...

    def get_dns_packet(self):
        if self.__bin_data_block is None:
            raise Exception("Data not found")
        dns_header: DNSHeader = self.__get_dns_header()
        questions: List[Question] = self.__get_ques_section(dns_header.question_count)
        answers: List[Record] = None
        nameserver_records: List[Record] = []
        additional_records: List[Record] = []
        if not dns_header.is_query:
            if dns_header.answer_count > 0:
                answers = self.__get_ans_section(dns_header.answer_count)
            if dns_header.nameserver_records_count > 0:
                nameserver_records = self.__get_authoritative_section(dns_header.nameserver_records_count)
            if dns_header.additional_records_count > 0:
                additional_records = self.__get_additional_section()
        return DNSPacket(dns_header, questions, answers, nameserver_records, additional_records)
