from enum import Enum
from ipaddress import IPv4Address


class RecordType(Enum):
    A = 1  # 2 bytes : Represents IPv4 address of a host


class RecordClass(Enum):
    IN = 1  # 2 bytes : Represents Internet Class


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
