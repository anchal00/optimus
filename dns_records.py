from enum import Enum
from ipaddress import IPv4Address


class RecordType(Enum):
    A = 1  # 2 bytes : Represents IPv4 address of a host

    def from_value(value: int):
        for rec in RecordType:
            if rec.value == value:
                return rec
        raise Exception("Could not find matching RecordType")


class RecordClass(Enum):
    IN = 1  # 2 bytes : Represents Internet Class

    def from_value(value: int):
        for rec in RecordClass:
            if rec.value == value:
                return rec
        raise Exception("Could not find matching RecordClass")


class Record:
    name: str
    rtype: RecordType
    rec_class: RecordClass
    ttl: int  # 4 bytes : Time-to-Live in seconds
    length: int  # 2 bytes : Length of content in a concrete record

    def __init__(
        self, name: str,
        rtype: RecordType,
        rclass: RecordClass,
        ttl: int,
        length: int
    ) -> None:
        self.name = name
        self.rtype = rtype
        self.rec_class = rclass
        self.ttl = ttl
        self.length = length


# Record Type A, representing IPv4 address of a host
class A(Record):
    address: IPv4Address

    def __init__(
        self, name: str,
        rtype: RecordType,
        rclass: RecordClass,
        ttl: int,
        length: int,
        address: IPv4Address
    ) -> None:
        super().__init__(name, rtype, rclass, ttl, length)
        self.address = address

    def __repr__(self) -> str:
        rep_dict = {
            "name": self.name,
            "type": self.rtype.name,
            "class": self.rec_class.name,
            "ttl": self.ttl,
            "length": self.length,
            "address": self.address
        }
        return str(rep_dict)
