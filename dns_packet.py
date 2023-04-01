from typing import List

class DNSPacket:
    def __init__(self):
        self.header: DNSHeader = None
        self.questions: List[Question] = None
        self.answers: List[Record] = None
        self.nameserver_records: List[Record] = None
        self.additional_records: List[Record] = None
