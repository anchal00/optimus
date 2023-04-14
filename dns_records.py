from enum import Enum
from ipaddress import IPv4Address


class RecordType(Enum):  # 2 bytes
    A = 1  # Alias : IPv4 address of a host
    NS = 2  # Name Server : The DNS server address for a domain
    CNAME = 5  # Canonical Name - Maps names to names
    MX = 15  # Mail exchange - The host of the mail server for a domain
    AAAA = 28  # IPv6 alias
    UNKNOWN = -1

    def from_value(value: int):
        for rec in RecordType:
            if rec.value == value:
                return rec
        return RecordType.UNKNOWN


class RecordClass(Enum):  # 2 bytes
    IN = 1  # Internet : Represents Internet Class
    UNKNOWN = -1

    def from_value(value: int):
        for rec in RecordClass:
            if rec.value == value:
                return rec
        return RecordClass.UNKNOWN


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

    def __repr__(self) -> str:
        rep_dict = {
            "name": self.name,
            "type": self.rtype.name,
            "class": self.rec_class.name,
            "ttl": self.ttl,
            "length": self.length
        }
        return str(rep_dict)


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


# Record Type CNAME, representing Canonical name of a host
class CNAME(Record):
    cname: str

    def __init__(
        self, name: str,
        rtype: RecordType,
        rclass: RecordClass,
        ttl: int,
        length: int,
        cname: str
    ) -> None:
        super().__init__(name, rtype, rclass, ttl, length)
        self.cname = cname

    def __repr__(self) -> str:
        rep_dict = {
            "name": self.name,
            "type": self.rtype.name,
            "class": self.rec_class.name,
            "ttl": self.ttl,
            "length": self.length,
            "cname": self.cname
        }
        return str(rep_dict)


class MX(Record):
    # Lower pref value => High Priority
    preference: int  # 2 bytes : Specifies the preference given to this record among others
    exchange: str  # Domain name which specifies a host willing to act as a mail exchange

    def __init__(
        self, name: str,
        rtype: RecordType,
        rclass: RecordClass,
        ttl: int,
        length: int,
        preference: int,
        exchange: str
    ) -> None:
        super().__init__(name, rtype, rclass, ttl, length)
        self.preference = preference
        self.exchange = exchange

    def __repr__(self) -> str:
        rep_dict = {
            "name": self.name,
            "type": self.rtype.name,
            "class": self.rec_class.name,
            "ttl": self.ttl,
            "length": self.length,
            "preference": self.preference,
            "exchange": self.exchange
        }
        return str(rep_dict)
