from enum import Enum
from ipaddress import IPv4Address, IPv6Address


class RecordType(Enum):  # 2 bytes
    A = 1  # Alias : IPv4 address of a host
    NS = 2  # Name Server : The DNS server address for a domain
    CNAME = 5  # Canonical Name : Maps names to names
    SOA = 6  # Marks the start of a zone of authority
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
        cur_len = len(dns_record_bin)
        data = int(self.address)
        first_2_bytes = (data >> 112) & 0xFFFF
        dns_record_bin.append((first_2_bytes & 0xFF00) >> 8)
        dns_record_bin.append((first_2_bytes & 0xFF))
        second_2_bytes = (data >> 96) & 0xFFFF
        dns_record_bin.append((second_2_bytes & 0xFF00) >> 8)
        dns_record_bin.append((second_2_bytes & 0xFF))
        third_2_bytes = (data >> 80) & 0xFFFF
        dns_record_bin.append((third_2_bytes & 0xFF00) >> 8)
        dns_record_bin.append((third_2_bytes & 0xFF))
        fourth_2_bytes = (data >> 64) & 0xFFFF
        dns_record_bin.append((fourth_2_bytes & 0xFF00) >> 8)
        dns_record_bin.append((fourth_2_bytes & 0xFF))
        fifth_2_bytes = (data >> 48) & 0xFFFF
        dns_record_bin.append((fifth_2_bytes & 0xFF00) >> 8)
        dns_record_bin.append((fifth_2_bytes & 0xFF))
        sixth_2_bytes = (data >> 32) & 0xFFFF
        dns_record_bin.append((sixth_2_bytes & 0xFF00) >> 8)
        dns_record_bin.append((sixth_2_bytes & 0xFF))
        seventh_2_bytes = (data >> 16) & 0xFFFF
        dns_record_bin.append((seventh_2_bytes & 0xFF00) >> 8)
        dns_record_bin.append((seventh_2_bytes & 0xFF))
        eighth_2_bytes = (data & 0xFFFF)
        dns_record_bin.append((eighth_2_bytes & 0xFF00) >> 8)
        dns_record_bin.append((eighth_2_bytes & 0xFF))
        # Modify length to reflect the actual bytes present in the record
        dns_record_bin[cur_len - 2] = ((self.length & 0xFF00) >> 8)
        dns_record_bin[cur_len - 1] = (self.length & 0xFF)
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
        cur_len = len(dns_record_bin)
        labels = self.cname.split('.')
        for label in labels:
            # Write label's length
            dns_record_bin.append(len(label))
            for ch in label:
                data = ord(ch) if ch != '.' else 0
                dns_record_bin.append(data)
        dns_record_bin.append(0)
        new_len = len(dns_record_bin)
        self.length = new_len - cur_len
        # Modify length to reflect the actual bytes present in the record
        dns_record_bin[cur_len - 2] = ((self.length & 0xFF00) >> 8)
        dns_record_bin[cur_len - 1] = (self.length & 0xFF)
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
        cur_len = len(dns_record_bin)
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
        new_len = len(dns_record_bin)
        self.length = new_len - cur_len
        # Modify length to reflect the actual bytes present in the record
        dns_record_bin[cur_len - 2] = ((self.length & 0xFF00) >> 8)
        dns_record_bin[cur_len - 1] = (self.length & 0xFF)
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
        cur_len = len(dns_record_bin)
        labels = self.nsdname.split('.')
        for label in labels:
            # Write label's length
            dns_record_bin.append(len(label))
            for ch in label:
                data = ord(ch) if ch != '.' else 0
                dns_record_bin.append(data)
        dns_record_bin.append(0)
        new_len = len(dns_record_bin)
        self.length = new_len - cur_len
        # Modify length to reflect the actual bytes present in the record
        dns_record_bin[cur_len - 2] = ((self.length & 0xFF00) >> 8)
        dns_record_bin[cur_len - 1] = (self.length & 0xFF)
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


class SOA(Record):
    # Domain name of the name server that was the
    # original or primary source of data for this zone.
    mname: str

    # Domain name which specifies the mailbox of the
    # person responsible for this zone
    rname: str

    # The unsigned 32 bit version number of the original copy
    # of the zone.  Zone transfers preserve this value.  This
    # value wraps and should be compared using sequence space
    # arithmetic
    serial: int

    # A 32 bit time interval before the zone should be
    # refreshed
    refresh: int

    # A 32 bit time interval that should elapse before a
    # failed refresh should be retried
    retry: int

    # A 32 bit time value that specifies the upper limit on
    # the time interval that can elapse before the zone is no
    # longer authoritative
    expire: int

    # The unsigned 32 bit minimum TTL field that should be
    # exported with any RR from this zone
    minimum: int

    def __init__(
        self, name: str,
        rtype: RecordType,
        rclass: RecordClass,
        ttl: int,
        length: int,
        mname: str,
        rname: str,
        serial: int,
        refresh: int,
        retry: int,
        expire: int,
        minimum: int
    ) -> None:
        super().__init__(name, rtype, rclass, ttl, length)
        self.mname = mname
        self.rname = rname
        self.serial = serial
        self.refresh = refresh
        self.retry = retry
        self.expire = expire
        self.minimum = minimum

    def to_bin(self) -> bytearray:
        dns_record_bin: bytearray = super().to_bin()
        cur_len = len(dns_record_bin)
        labels = self.mname.split('.')
        for label in labels:
            # Write label's length
            dns_record_bin.append(len(label))
            for ch in label:
                data = ord(ch) if ch != '.' else 0
                dns_record_bin.append(data)
        dns_record_bin.append(0)

        labels = self.rname.split('.')
        for label in labels:
            # Write label's length
            dns_record_bin.append(len(label))
            for ch in label:
                data = ord(ch) if ch != '.' else 0
                dns_record_bin.append(data)
        dns_record_bin.append(0)

        dns_record_bin.append((self.serial & 0xFF000000) >> 24)
        dns_record_bin.append((self.serial & 0xFF0000) >> 16)
        dns_record_bin.append((self.serial & 0xFF00) >> 8)
        dns_record_bin.append(self.serial & 0xFF)

        dns_record_bin.append((self.refresh & 0xFF000000) >> 24)
        dns_record_bin.append((self.refresh & 0xFF0000) >> 16)
        dns_record_bin.append((self.refresh & 0xFF00) >> 8)
        dns_record_bin.append(self.refresh & 0xFF)

        dns_record_bin.append((self.retry & 0xFF000000) >> 24)
        dns_record_bin.append((self.retry & 0xFF0000) >> 16)
        dns_record_bin.append((self.retry & 0xFF00) >> 8)
        dns_record_bin.append(self.retry & 0xFF)

        dns_record_bin.append((self.expire & 0xFF000000) >> 24)
        dns_record_bin.append((self.expire & 0xFF0000) >> 16)
        dns_record_bin.append((self.expire & 0xFF00) >> 8)
        dns_record_bin.append(self.expire & 0xFF)

        dns_record_bin.append((self.minimum & 0xFF000000) >> 24)
        dns_record_bin.append((self.minimum & 0xFF0000) >> 16)
        dns_record_bin.append((self.minimum & 0xFF00) >> 8)
        dns_record_bin.append(self.minimum & 0xFF)

        new_len = len(dns_record_bin)
        self.length = new_len - cur_len
        # Modify length to reflect the actual bytes present in the record
        dns_record_bin[cur_len - 2] = ((self.length & 0xFF00) >> 8)
        dns_record_bin[cur_len - 1] = (self.length & 0xFF)
        return dns_record_bin

    def __repr__(self) -> str:
        rep_dict = {
            "name": self.name,
            "type": self.rtype.name,
            "class": self.rec_class.name,
            "ttl": self.ttl,
            "length": self.length,
            "mname": self.mname,
            "rname": self.rname,
            "serial": self.serial,
            "refresh": self.refresh,
            "retry": self.retry,
            "expire": self.expire,
            "minimum": self.minimum,
        }
        return str(rep_dict)
