from enum import Enum
from ipaddress import IPv4Address, IPv6Address


class RecordType(Enum):  # 2 bytes
    A = 1  # Alias : IPv4 address of a host
    NS = 2  # Name Server : The DNS server address for a domain
    CNAME = 5  # Canonical Name : Maps names to names
    MX = 15  # Mail exchange : The host of the mail server for a domain
    AAAA = 28  # IPv6 alias : IPv6 address of a host
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

    def to_bin(self) -> bytearray:
        dns_record_bin: bytearray = bytearray(0)
        labels = self.name.split('.')
        for label in labels:
            # Write label's length
            dns_record_bin.append(len(label))  # TODO: Add check to ensure that label length is <=63
            for ch in label:
                data = ord(ch) if ch != '.' else 0
                dns_record_bin.append(data)
        dns_record_bin.append(0)
        # Set Type (In 2 byte format)
        dns_record_bin.append((self.rtype.value & 0xFF00) >> 8)
        dns_record_bin.append(self.rtype.value & 0xFF)
        # Set Class (In 2 byte format)
        dns_record_bin.append((self.rec_class.value & 0xFF00) >> 8)
        dns_record_bin.append(self.rec_class.value & 0xFF)
        # Set TTL
        dns_record_bin.append((self.ttl & 0xFF000000) >> 24)
        dns_record_bin.append((self.ttl & 0xFF0000) >> 16)
        dns_record_bin.append((self.ttl & 0xFF00) >> 8)
        dns_record_bin.append(self.ttl & 0xFF)
        # Set Length
        dns_record_bin.append((self.length & 0xFF00) >> 8)
        dns_record_bin.append(self.length & 0xFF)
        return dns_record_bin

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

    def to_bin(self) -> bytearray:
        dns_record_bin: bytearray = super().to_bin()
        data = int(self.address)
        dns_record_bin.append((data & 0xFF000000) >> 24)
        dns_record_bin.append((data & 0xFF0000) >> 16)
        dns_record_bin.append((data & 0xFF00) >> 8)
        dns_record_bin.append((data & 0xFF))
        return dns_record_bin

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


# Record Type AAAA, representing IPv6 address of a host
class AAAA(Record):
    address: IPv6Address

    def __init__(
        self, name: str,
        rtype: RecordType,
        rclass: RecordClass,
        ttl: int,
        length: int,
        address: IPv6Address
    ) -> None:
        super().__init__(name, rtype, rclass, ttl, length)
        self.address = address

    def to_bin(self) -> bytearray:
        dns_record_bin: bytearray = super().to_bin()
        data = int(self.address)
        first_2_bytes = (data & 0xFFFF0000000000000000000000000000) >> 112
        dns_record_bin.append((first_2_bytes & 0xFF00) >> 8)
        dns_record_bin.append((first_2_bytes & 0xFF))
        second_2_bytes = (data & 0xFFFF000000000000000000000000) >> 96
        dns_record_bin.append((second_2_bytes & 0xFF00) >> 8)
        dns_record_bin.append((second_2_bytes & 0xFF))
        third_2_bytes = (data & 0xFFFF00000000000000000000) >> 80
        dns_record_bin.append((third_2_bytes & 0xFF00) >> 8)
        dns_record_bin.append((third_2_bytes & 0xFF))
        fourth_2_bytes = (data & 0xFFFF0000000000000000) >> 64
        dns_record_bin.append((fourth_2_bytes & 0xFF00) >> 8)
        dns_record_bin.append((fourth_2_bytes & 0xFF))
        fifth_2_bytes = (data & 0xFFFF000000000000) >> 48
        dns_record_bin.append((fifth_2_bytes & 0xFF00) >> 8)
        dns_record_bin.append((fifth_2_bytes & 0xFF))
        sixth_2_bytes = (data & 0xFFFF00000000) >> 32
        dns_record_bin.append((sixth_2_bytes & 0xFF00) >> 8)
        dns_record_bin.append((sixth_2_bytes & 0xFF))
        seventh_2_bytes = (data & 0xFFFF0000) >> 16
        dns_record_bin.append((seventh_2_bytes & 0xFF00) >> 8)
        dns_record_bin.append((seventh_2_bytes & 0xFF))
        eighth_2_bytes = (data & 0xFFFF)
        dns_record_bin.append((eighth_2_bytes & 0xFF00) >> 8)
        dns_record_bin.append((eighth_2_bytes & 0xFF))
        return dns_record_bin

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

    def to_bin(self) -> bytearray:
        dns_record_bin: bytearray = super().to_bin()
        labels = self.cname.split('.')
        for label in labels:
            # Write label's length
            dns_record_bin.append(len(label))
            for ch in label:
                data = ord(ch) if ch != '.' else 0
                dns_record_bin.append(data)
        dns_record_bin.append(0)
        return dns_record_bin

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


# Record Type MX, representing the host of the mail server for a domain
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

    def to_bin(self) -> bytearray:
        dns_record_bin: bytearray = super().to_bin()
        dns_record_bin.append((self.preference & 0xFF00) >> 8)
        dns_record_bin.append(self.preference & 0xFF)
        labels = self.exchange.split('.')
        for label in labels:
            # Write label's length
            dns_record_bin.append(len(label))
            for ch in label:
                data = ord(ch) if ch != '.' else 0
                dns_record_bin.append(data)
        dns_record_bin.append(0)
        return dns_record_bin

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


# Record Type NS, Representing the DNS server address for a domain
class NS(Record):
    nsdname: str  # Domain name which specifies a host which should be authoritative for specified class and domain

    def __init__(
        self, name: str,
        rtype: RecordType,
        rclass: RecordClass,
        ttl: int,
        length: int,
        nsdname: str
    ) -> None:
        super().__init__(name, rtype, rclass, ttl, length)
        self.nsdname = nsdname

    def to_bin(self) -> bytearray:
        dns_record_bin: bytearray = super().to_bin()
        labels = self.name.split('.')
        for label in labels:
            # Write label's length
            dns_record_bin.append(len(label))
            for ch in label:
                data = ord(ch) if ch != '.' else 0
                dns_record_bin.append(data)
        dns_record_bin.append(0)
        return dns_record_bin

    def __repr__(self) -> str:
        rep_dict = {
            "name": self.name,
            "type": self.rtype.name,
            "class": self.rec_class.name,
            "ttl": self.ttl,
            "length": self.length,
            "nsdname": self.nsdname
        }
        return str(rep_dict)
