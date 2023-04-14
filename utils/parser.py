from ipaddress import IPv4Address, IPv6Address
from typing import List

from dns_packet import DNSHeader, DNSPacket, Question, ResponseCode
from dns_records import AAAA, MX, NS, A, Record, RecordClass, RecordType


class Parser:
    def __init__(self, bin_data: bytearray) -> None:
        self.__bin_data_block = bin_data
        self.__ptr = 0

    def __increment_ptr(self, steps: int) -> None:
        self.__ptr += steps

    def __seek_ptr_pos(self, pos: int) -> None:
        self.__ptr = pos

    def __parse_bytes(self, bytes_to_parse: int) -> int:
        to_be_read_data_block = self.__bin_data_block[self.__ptr:]
        data = 0
        for x in to_be_read_data_block[:bytes_to_parse]:
            data = data << 8 | x
        return data

    def __parse_bytes_and_move_ahead(self, bytes_to_parse: int) -> int:
        to_be_read_data_block = self.__bin_data_block[self.__ptr:]
        data = 0
        for x in to_be_read_data_block[:bytes_to_parse]:
            data = data << 8 | x
            self.__increment_ptr(1)
        return data

    def __parse_record_name(self) -> str:
        msb_data: int = self.__parse_bytes(1)
        if self.__is_label_compressed(msb_data):
            # In this case, the next byte should be treated as OFFSET
            # which specifies the position from where the name has to be
            # read
            self.__increment_ptr(1)
            name = self.__parse_compressed_label()
            return name
        return self.__parse_sequence_of_labels()

    def __is_label_compressed(self, label_length):
        # If the First Byte (MSB) of the 'length' byte has two leftmost(MS)
        #  bits set then the label is represented in Compressed format.
        return label_length ^ 0xC0 == 0

    def __parse_compressed_label(self):
        offset: int = self.__parse_bytes_and_move_ahead(1)
        cur_ptr_pos: int = self.__ptr
        self.__seek_ptr_pos(offset)
        name: str = self.__parse_sequence_of_labels()
        # Restore pointer to where it was
        self.__seek_ptr_pos(cur_ptr_pos)
        return name

    def __parse_sequence_of_labels(self) -> str:
        full_name: List = []
        name_str: str = ''
        # 2 MSB bits of the this label_length field are always 0
        # So the label_length can have values between 0 and 63, meaning
        # that the name can take only between 0-63 octets
        label_length: int = self.__parse_bytes_and_move_ahead(1)
        # Parse sequence of labels to decode the Name
        while label_length != 0:
            if self.__is_label_compressed(label_length):
                name_str = self.__parse_compressed_label()
                full_name.append(name_str)
                return '.'.join(full_name)
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
        response_code = ResponseCode.from_value((lsb_byte >> 3) & 0x0F)
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
            name: str = self.__parse_record_name()
            # Parse type
            rtype: RecordType = RecordType.from_value(self.__parse_bytes_and_move_ahead(2))
            # Parse class
            qclass: RecordClass = RecordClass.from_value(self.__parse_bytes_and_move_ahead(2))
            questions.append(Question(name, rtype, qclass))
        return questions

    def __read_response_records(self) -> Record:
        name: str = self.__parse_record_name()
        rtype: RecordType = RecordType.from_value(self.__parse_bytes_and_move_ahead(2))
        rclass: RecordClass = RecordClass.from_value(self.__parse_bytes_and_move_ahead(2))
        ttl: int = self.__parse_bytes_and_move_ahead(4)
        length: int = self.__parse_bytes_and_move_ahead(2)
        record: Record = None
        # Parse record acc to RecordType
        if rtype == RecordType.A:
            ipv4_addr_int: int = self.__parse_bytes_and_move_ahead(4)
            record: Record = AAAA(name, rtype, rclass, ttl, length, IPv4Address(ipv4_addr_int))
        if rtype == RecordType.AAAA:
            ipv4_addr_int: int = self.__parse_bytes_and_move_ahead(6)
            record: Record = A(name, rtype, rclass, ttl, length, IPv6Address(ipv4_addr_int))
        elif rtype == RecordType.CNAME:
            from dns_records import CNAME
            record: Record = CNAME(name, rtype, rclass, ttl, length, self.__parse_record_name())
        elif rtype == RecordType.MX:
            record: Record = MX(name, rtype, rclass, ttl, length, self.__parse_bytes_and_move_ahead(2),
                                self.__parse_record_name())
        elif rtype == RecordType.NS:
            record: Record = NS(name, rtype, rclass, ttl, length, self.__parse_record_name())
        else:
            record: Record = Record(name, rtype, rclass, ttl, length)
        return record

    def __get_ans_section(self, total_answers: int) -> List[Record]:
        answers: List[Record] = []
        for _ in range(0, total_answers):
            answers.append(self.__read_response_records())
        return answers

    def __get_additional_section(self, additional_records_count: int) -> List[Record]:
        ad_records: List[Record] = []
        for _ in range(0, additional_records_count):
            ad_records.append(self.__read_response_records())
        return ad_records

    def __get_authoritative_section(self, nameserver_records_count: int) -> List[Record]:
        ns_records: List[Record] = []
        for _ in range(0, nameserver_records_count):
            ns_records.append(self.__read_response_records())
        return ns_records

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
                additional_records = self.__get_additional_section(dns_header.additional_records_count)
        return DNSPacket(dns_header, questions, answers, nameserver_records, additional_records)

    # TODO: Fix method to accept only one arg of type DNSPacket rather than passing separate args
    @staticmethod
    def get_bin_query_dns_packet(domain: str, record_type: RecordType, recursion_desired: bool) -> bytearray:
        dns_packet_bin: bytearray = bytearray(50)  # Use arbitrary packet size(50) for now
        # Write 12 bytes DNS header
        id: int = 15196  # TODO: Make it random 2 byte ID
        # Represent Id in 2 byte format
        id_msbyte: int = (id & 0xFF00) >> 8
        id_lsbyte: int = (id & 0xFF)
        dns_packet_bin[0] = id_msbyte
        dns_packet_bin[1] = id_lsbyte
        dns_packet_bin[2] = 1 if recursion_desired else 0
        dns_packet_bin[3] = 0 ^ (1 << 5)
        dns_packet_bin[5] = 1  # Set Question Count to 1
        # Write Question in the DNS packet
        labels = domain.split('.')
        cur_pos = 12
        for label in labels:
            # Write label's length
            dns_packet_bin[cur_pos] = len(label)  # TODO: Add check to ensure that label length is <=63
            cur_pos += 1
            for ch in label:
                data = ord(ch) if ch != '.' else 0
                dns_packet_bin[cur_pos] = data
                cur_pos += 1
        # Set Type (In 2 byte format)
        cur_pos += 1
        dns_packet_bin[cur_pos] = (record_type.value & 0xFF00) >> 8
        cur_pos += 1
        dns_packet_bin[cur_pos] = (record_type.value & 0xFF)
        # Set Class to 1 for now
        cur_pos += 2
        dns_packet_bin[cur_pos] = 1
        return dns_packet_bin
