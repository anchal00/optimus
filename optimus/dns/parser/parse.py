from ipaddress import IPv4Address, IPv6Address
from typing import List, Optional, Union

from optimus.dns.models.packet import DNSHeader, DNSPacket, Question, ResponseCode
from optimus.dns.models.records import AAAA, CNAME, MX, NS, SOA, A, OptPseudoRR, Record, RecordClass, RecordType
from optimus.dns.parser.iter import BytearrayIterator


class DNSParser:
    def __init__(self, bin_data: bytearray) -> None:
        if not bin_data:
            raise Exception("No binary data given to parse")
        self.__iter = BytearrayIterator(bin_data)

    def __to_int(self, data: bytearray) -> int:
        value = 0
        for x in data:
            value = value << 8 | x
        return value

    def get_dns_packet(self) -> DNSPacket:
        dns_header: DNSHeader = self.__get_dns_header()
        questions = self.__get_ques_section(dns_header.question_count)
        answers = []
        nameserver_records = []
        additional_records: Optional[List[Union[Record, OptPseudoRR]]] = []
        if not dns_header.is_query:
            if dns_header.answer_count > 0:
                answers = self.__get_ans_section(dns_header.answer_count)
            if dns_header.nameserver_records_count > 0:
                nameserver_records = self.__get_authoritative_section(dns_header.nameserver_records_count)
            if dns_header.additional_records_count > 0:
                additional_records = self.__get_additional_section(dns_header.additional_records_count)
        else:
            if dns_header.additional_records_count > 0:
                dns_header.additional_records_count = 0
        return DNSPacket(dns_header, questions, answers, nameserver_records, additional_records)

    def __parse_record_name(self) -> str:
        msb_data: int = self.__to_int(self.__iter.get_n_bytes(1))
        if self.__is_label_compressed(msb_data):
            # In this case, the next byte should be treated as OFFSET
            # which specifies the position from where the name has to be
            # read
            self.__iter.seek_ptr_pos(self.__iter.get_cur_ptr_pos() + 1)
            name = self.__parse_compressed_label()
            return name
        return self.__parse_sequence_of_labels()

    def __is_label_compressed(self, label_length) -> bool:
        # If the First Byte (MSB) of the 'length' byte has two leftmost(MS)
        #  bits set then the label is represented in Compressed format.
        return bool(label_length ^ 0xC0 == 0)

    def __parse_compressed_label(self) -> str:
        offset: int = self.__to_int(self.__iter.get_n_bytes_and_move(1))
        cur_ptr_pos: int = self.__iter.get_cur_ptr_pos()
        self.__iter.seek_ptr_pos(offset)
        name: str = self.__parse_sequence_of_labels()
        # Restore pointer to where it was
        self.__iter.seek_ptr_pos(cur_ptr_pos)
        return name

    def __parse_sequence_of_labels(self) -> str:
        full_name: List = []
        name_str: str = ""
        # 2 MSB bits of the this label_length field are always 0
        # So the label_length can have values between 0 and 63, meaning
        # that the name can take only between 0-63 octets
        label_length: int = self.__to_int(self.__iter.get_n_bytes_and_move(1))
        # Parse sequence of labels to decode the Name
        while label_length != 0:
            if self.__is_label_compressed(label_length):
                name_str = self.__parse_compressed_label()
                full_name.append(name_str)
                return ".".join(full_name)
            for _ in range(0, label_length):
                label: int = self.__to_int(self.__iter.get_n_bytes_and_move(1))
                name_str = name_str + chr(label)
            full_name.append(name_str)
            name_str = ""
            label_length = self.__to_int(self.__iter.get_n_bytes_and_move(1))
        return ".".join(full_name)

    def __get_dns_header(self) -> DNSHeader:
        # Parse ID
        id = self.__to_int(self.__iter.get_n_bytes_and_move(2))
        bytes_data = self.__to_int(self.__iter.get_n_bytes_and_move(2))
        msb_byte = (bytes_data & 0xFF00) >> 8
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

        lsb_byte = bytes_data & 0xFF
        # Parse RA
        is_recursion_available = lsb_byte & (1 << 7) != 0
        # Parse Z
        z_field = (lsb_byte >> 4) & 7  # TODO: Expand Z field to Z, AD (Authenticated Data), CD (Checking Disabled)
        # Parse RC
        response_code = ResponseCode.from_value(lsb_byte & 0x0F)
        # Parse Record counts
        question_count = self.__to_int(self.__iter.get_n_bytes_and_move(2))
        answer_count = self.__to_int(self.__iter.get_n_bytes_and_move(2))
        nameserver_records_count = self.__to_int(self.__iter.get_n_bytes_and_move(2))
        additional_records_count = self.__to_int(self.__iter.get_n_bytes_and_move(2))
        return DNSHeader(
            id,
            is_query,
            opcode,
            is_authoritative_answer,
            is_truncated_message,
            is_recursion_desired,
            is_recursion_available,
            z_field,
            response_code,
            question_count,
            answer_count,
            nameserver_records_count,
            additional_records_count,
        )

    def __get_ques_section(self, total_questions) -> List[Question]:
        questions: List[Question] = []
        for _ in range(total_questions):
            # Parse name
            name: str = self.__parse_record_name()
            # Parse type
            rtype: RecordType = RecordType.from_value(self.__to_int(self.__iter.get_n_bytes_and_move(2)))
            # Parse class
            qclass: RecordClass = RecordClass.from_value(self.__to_int(self.__iter.get_n_bytes_and_move(2)))
            questions.append(Question(name, rtype, qclass))
        return questions

    def __parse_records(self) -> Record:
        name: str = self.__parse_record_name()
        record_type = self.__to_int(self.__iter.get_n_bytes_and_move(2))
        rtype: RecordType = RecordType.from_value(record_type)
        record_class = self.__to_int(self.__iter.get_n_bytes_and_move(2))
        rclass: RecordClass = RecordClass.from_value(record_class)
        ttl: int = self.__to_int(self.__iter.get_n_bytes_and_move(4))
        length: int = self.__to_int(self.__iter.get_n_bytes_and_move(2))
        # Parse record acc to RecordType
        record: Union[Record, OptPseudoRR]
        if rtype.value == RecordType.A.value:
            ipv4_addr_int: int = self.__to_int(self.__iter.get_n_bytes_and_move(4))
            record = A(name, rtype, rclass, ttl, length, IPv4Address(ipv4_addr_int))
        elif rtype.value == RecordType.AAAA.value:
            ipv6_addr_int: int = self.__to_int(self.__iter.get_n_bytes_and_move(16))
            record = AAAA(name, rtype, rclass, ttl, length, IPv6Address(ipv6_addr_int))
        elif rtype.value == RecordType.CNAME.value:
            record = CNAME(name, rtype, rclass, ttl, length, self.__parse_record_name())
        elif rtype.value == RecordType.MX.value:
            record = MX(
                name,
                rtype,
                rclass,
                ttl,
                length,
                self.__to_int(self.__iter.get_n_bytes_and_move(2)),
                self.__parse_record_name(),
            )
        elif rtype.value == RecordType.NS.value:
            record = NS(name, rtype, rclass, ttl, length, self.__parse_record_name())
        elif rtype.value == RecordType.SOA.value:
            record = SOA(
                name,
                rtype,
                rclass,
                ttl,
                length,
                self.__parse_record_name(),
                self.__parse_record_name(),
                self.__to_int(self.__iter.get_n_bytes_and_move(4)),
                self.__to_int(self.__iter.get_n_bytes_and_move(4)),
                self.__to_int(self.__iter.get_n_bytes_and_move(4)),
                self.__to_int(self.__iter.get_n_bytes_and_move(4)),
                self.__to_int(self.__iter.get_n_bytes_and_move(4)),
            )
        elif rtype.value == RecordType.OPT.value:
            record = OptPseudoRR(
                name,
                rtype,
                requestor_udp_payload_size=record_class,
                ext_rcode_flags=ttl,
                length=length,
                data=bytearray(12),
            )
        else:
            record = Record(name, rtype, rclass, ttl, length)
        return record

    def __get_ans_section(self, total_answers: int) -> List[Record]:
        answers = []
        for _ in range(total_answers):
            answers.append(self.__parse_records())
        return answers

    def __get_additional_section(self, additional_records_count: int) -> List[Record]:
        ad_records = []
        for _ in range(additional_records_count):
            ad_records.append(self.__parse_records())
        return ad_records

    def __get_authoritative_section(self, nameserver_records_count: int) -> List[Record]:
        ns_records = []
        for _ in range(nameserver_records_count):
            ns_records.append(self.__parse_records())
        return ns_records
