from enum import Enum
from ipaddress import IPv4Address, IPv6Address

from optimus.utils import to_n_bytes


class RecordType(Enum):  # 2 bytes
    A = 1  # Alias : IPv4 address of a host
    NS = 2  # Name Server : The DNS server address for a domain
    CNAME = 5  # Canonical Name : Maps names to names
    SOA = 6  # Marks the start of a zone of authority
    PTR = 12  # Pointer record for reverse DNS lookups
    MX = 15  # Mail exchange : The host of the mail server for a domain
    TXT = 16  # Text record, for storing arbitrary text
    AAAA = 28  # IPv6 alias : IPv6 address of a host
    OPT = 41  # OPT-pseudo RR or meta RR
    HTTPS = 65
    URI = 265
    TEST1 = 65535
    TEST2 = 0
    UNKNOWN = -1

    @classmethod
    def from_value(cls, value: int):
        for rec in RecordType:
            if rec.value == value:
                return rec
        return RecordType.UNKNOWN


class RecordClass(Enum):  # 2 bytes
    IN = 1  # Internet : Represents Internet Class
    UNKNOWN = -1

    @classmethod
    def from_value(cls, value: int):
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

    # ---------------------------------------
    # Nasty workaround for mypy errors
    # Attributes of other record types(subclasses)
    ipv4_address: IPv4Address
    ipv6_address: IPv6Address
    cname: str
    preference: int
    exchange: str
    nsdname: str
    mname: str
    rname: str
    serial: int
    refresh: int
    retry: int
    expire: int
    minimum: int

    # ----------------------------------------
    def __init__(self, name: str, rtype: RecordType, rclass: RecordClass, ttl: int, length: int) -> None:
        self.name = name
        self.rtype = rtype
        self.rec_class = rclass
        self.ttl = ttl
        self.length = length

    def to_bin(self) -> bytearray:
        dns_record_bin: bytearray = bytearray(0)
        labels = self.name.split(".")
        for label in labels:
            # Write label's length
            dns_record_bin.append(len(label))  # TODO: Add check to ensure that label length is <=63
            for ch in label:
                data = ord(ch) if ch != "." else 0
                dns_record_bin.append(data)
        dns_record_bin.append(0)
        # Set Type (In 2 byte format)
        dns_record_bin.extend(to_n_bytes(self.rtype.value, 2))
        # Set Class (In 2 byte format)
        dns_record_bin.extend(to_n_bytes(self.rec_class.value, 2))
        # Set TTL
        dns_record_bin.extend(to_n_bytes(self.ttl, 4))
        # Set Length
        dns_record_bin.extend(to_n_bytes(self.length, 2))
        return dns_record_bin

    def __repr__(self) -> str:
        rep_dict = {
            "name": self.name,
            "type": self.rtype.name,
            "class": self.rec_class.name,
            "ttl": self.ttl,
            "length": self.length,
        }
        return str(rep_dict)


# Record Type A, representing IPv4 address of a host
class A(Record):
    ipv4_address: IPv4Address

    def __init__(
        self,
        name: str,
        rtype: RecordType,
        rclass: RecordClass,
        ttl: int,
        length: int,
        address: IPv4Address,
    ) -> None:
        super().__init__(name, rtype, rclass, ttl, length)
        self.ipv4_address = address

    def to_bin(self) -> bytearray:
        dns_record_bin: bytearray = super().to_bin()
        data = int(self.ipv4_address)
        dns_record_bin.extend(to_n_bytes(data, 4))
        return dns_record_bin

    def __repr__(self) -> str:
        rep_dict = {
            "name": self.name,
            "type": self.rtype.name,
            "class": self.rec_class.name,
            "ttl": self.ttl,
            "length": self.length,
            "address": self.ipv4_address,
        }
        return str(rep_dict)


# Record Type AAAA, representing IPv6 address of a host
class AAAA(Record):
    ipv6_address: IPv6Address

    def __init__(
        self,
        name: str,
        rtype: RecordType,
        rclass: RecordClass,
        ttl: int,
        length: int,
        address: IPv6Address,
    ) -> None:
        super().__init__(name, rtype, rclass, ttl, length)
        self.ipv6_address = address

    def to_bin(self) -> bytearray:
        dns_record_bin: bytearray = super().to_bin()
        cur_len = len(dns_record_bin)
        data = int(self.ipv6_address)
        dns_record_bin.extend(to_n_bytes(data, 16))
        # Modify length to reflect the actual bytes present in the record
        dns_record_bin[cur_len - 2] = (self.length & 0xFF00) >> 8
        dns_record_bin[cur_len - 1] = self.length & 0xFF
        return dns_record_bin

    def __repr__(self) -> str:
        rep_dict = {
            "name": self.name,
            "type": self.rtype.name,
            "class": self.rec_class.name,
            "ttl": self.ttl,
            "length": self.length,
            "address": self.ipv6_address,
        }
        return str(rep_dict)


# Record Type CNAME, representing Canonical name of a host
class CNAME(Record):
    cname: str

    def __init__(
        self,
        name: str,
        rtype: RecordType,
        rclass: RecordClass,
        ttl: int,
        length: int,
        cname: str,
    ) -> None:
        super().__init__(name, rtype, rclass, ttl, length)
        self.cname = cname

    def to_bin(self) -> bytearray:
        dns_record_bin: bytearray = super().to_bin()
        cur_len = len(dns_record_bin)
        labels = self.cname.split(".")
        for label in labels:
            # Write label's length
            dns_record_bin.append(len(label))
            for ch in label:
                data = ord(ch) if ch != "." else 0
                dns_record_bin.append(data)
        dns_record_bin.append(0)
        new_len = len(dns_record_bin)
        self.length = new_len - cur_len
        # Modify length to reflect the actual bytes present in the record
        dns_record_bin[cur_len - 2] = (self.length & 0xFF00) >> 8
        dns_record_bin[cur_len - 1] = self.length & 0xFF
        return dns_record_bin

    def __repr__(self) -> str:
        rep_dict = {
            "name": self.name,
            "type": self.rtype.name,
            "class": self.rec_class.name,
            "ttl": self.ttl,
            "length": self.length,
            "cname": self.cname,
        }
        return str(rep_dict)


# Record Type MX, representing the host of the mail server for a domain
class MX(Record):
    # Lower pref value => High Priority
    preference: int  # 2 bytes : Specifies the preference given to this record among others
    exchange: str  # Domain name which specifies a host willing to act as a mail exchange

    def __init__(
        self,
        name: str,
        rtype: RecordType,
        rclass: RecordClass,
        ttl: int,
        length: int,
        preference: int,
        exchange: str,
    ) -> None:
        super().__init__(name, rtype, rclass, ttl, length)
        self.preference = preference
        self.exchange = exchange

    def to_bin(self) -> bytearray:
        dns_record_bin: bytearray = super().to_bin()
        cur_len = len(dns_record_bin)
        dns_record_bin.append((self.preference & 0xFF00) >> 8)
        dns_record_bin.append(self.preference & 0xFF)
        labels = self.exchange.split(".")
        for label in labels:
            # Write label's length
            dns_record_bin.append(len(label))
            for ch in label:
                data = ord(ch) if ch != "." else 0
                dns_record_bin.append(data)
        dns_record_bin.append(0)
        new_len = len(dns_record_bin)
        self.length = new_len - cur_len
        # Modify length to reflect the actual bytes present in the record
        dns_record_bin[cur_len - 2] = (self.length & 0xFF00) >> 8
        dns_record_bin[cur_len - 1] = self.length & 0xFF
        return dns_record_bin

    def __repr__(self) -> str:
        rep_dict = {
            "name": self.name,
            "type": self.rtype.name,
            "class": self.rec_class.name,
            "ttl": self.ttl,
            "length": self.length,
            "preference": self.preference,
            "exchange": self.exchange,
        }
        return str(rep_dict)


# Record Type NS, Representing the DNS server address for a domain
class NS(Record):
    nsdname: str  # Domain name which specifies a host which should be authoritative for specified class and domain

    def __init__(
        self,
        name: str,
        rtype: RecordType,
        rclass: RecordClass,
        ttl: int,
        length: int,
        nsdname: str,
    ) -> None:
        super().__init__(name, rtype, rclass, ttl, length)
        self.nsdname = nsdname

    def to_bin(self) -> bytearray:
        dns_record_bin: bytearray = super().to_bin()
        cur_len = len(dns_record_bin)
        labels = self.nsdname.split(".")
        for label in labels:
            # Write label's length
            dns_record_bin.append(len(label))
            for ch in label:
                data = ord(ch) if ch != "." else 0
                dns_record_bin.append(data)
        dns_record_bin.append(0)
        new_len = len(dns_record_bin)
        self.length = new_len - cur_len
        # Modify length to reflect the actual bytes present in the record
        dns_record_bin[cur_len - 2] = (self.length & 0xFF00) >> 8
        dns_record_bin[cur_len - 1] = self.length & 0xFF
        return dns_record_bin

    def __repr__(self) -> str:
        rep_dict = {
            "name": self.name,
            "type": self.rtype.name,
            "class": self.rec_class.name,
            "ttl": self.ttl,
            "length": self.length,
            "nsdname": self.nsdname,
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
        self,
        name: str,
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
        minimum: int,
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
        labels = self.mname.split(".")
        for label in labels:
            # Write label's length
            dns_record_bin.append(len(label))
            for ch in label:
                data = ord(ch) if ch != "." else 0
                dns_record_bin.append(data)
        dns_record_bin.append(0)

        labels = self.rname.split(".")
        for label in labels:
            # Write label's length
            dns_record_bin.append(len(label))
            for ch in label:
                data = ord(ch) if ch != "." else 0
                dns_record_bin.append(data)
        dns_record_bin.append(0)
        dns_record_bin.extend(to_n_bytes(self.serial, 4))
        dns_record_bin.extend(to_n_bytes(self.refresh, 4))
        dns_record_bin.extend(to_n_bytes(self.retry, 4))
        dns_record_bin.extend(to_n_bytes(self.expire, 4))
        dns_record_bin.extend(to_n_bytes(self.minimum, 4))
        new_len = len(dns_record_bin)
        self.length = new_len - cur_len
        # Modify length to reflect the actual bytes present in the record
        dns_record_bin[cur_len - 2] = (self.length & 0xFF00) >> 8
        dns_record_bin[cur_len - 1] = self.length & 0xFF
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


# An OPT pseudo-RR (sometimes called a meta-RR) MAY be added to the
# additional data section of a request. An OPT record does not carry any DNS data
class OptPseudoRR(Record):
    """
    name: str  # domain name MUST be '0' (root domain)
    rtype: int  # 2 bytes, OPT (41)
    rec_class: int  # 2 bytes, requestor's UDP payload size
    ttl: int  # 4 bytes, extended RCODE and flags
    length: int  # 2 bytes, length of all Record data
    """

    data: bytearray  # octet stream  {attribute,value}

    def __init__(
        self,
        name: str,
        rtype: RecordType,
        requestor_udp_payload_size: int,
        ext_rcode_flags: int,
        length: int,
        data: bytearray,
    ) -> None:
        super().__init__(name, rtype, RecordClass.from_value(requestor_udp_payload_size), ext_rcode_flags, length)
        self.requestor_udp_payload_size = requestor_udp_payload_size
        self.ext_rcode_flags = ext_rcode_flags
        self.data = data

    def to_bin(self) -> bytearray:
        return self.data

    def __repr__(self) -> str:
        rep_dict = {
            # "name": self.name,
            # "type": self.rtype.name,
            # "class": self.rec_class,
            # "ttl": self.ttl,
            # "length": self.length,
            # "rdata": self.rec_data,
            "data": self.data
        }
        return str(rep_dict)
