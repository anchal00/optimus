from enum import Enum
from ipaddress import IPv4Address


class RecordType(Enum):
    A = 1  # 2 bytes : Represents IPv4 address of a host

    def from_value(value: int):
        for rec in RecordType:
            if rec.value == value:
                return rec.name
        raise Exception("Could not find matching RecordType")


class RecordClass(Enum):
    IN = 1  # 2 bytes : Represents Internet Class

    def from_value(value: int):
        for rec in RecordClass:
            if rec.value == value:
                return rec.name
        raise Exception("Could not find matching RecordClass")


class Record:
    name: str
    type: RecordType
    rec_class: RecordClass
    ttl: int  # 4 bytes : Time-to-Live
    length: int  # 2 bytes : Length of content in a concrete record


# Record Type - A
class A(Record):
    address: IPv4Address
    length = 4  # bytes
