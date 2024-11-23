import binascii
import unittest
from collections import namedtuple

from optimus.dns.models.packet import DNSPacket
from optimus.dns.models.records import RecordClass, RecordType
from optimus.dns.parser.parse import DNSParser


class TestDnsParser(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        DnsPacketData = namedtuple("DnsPacketData", ["domain", "data"])
        cls.DNS_QUERY_PACKET_FIXTURES: dict[RecordType, DnsPacketData] = {
            RecordType.A: DnsPacketData(
                domain="google.com",
                data="22a90120000100000000000106676f6f676c6503636f6d0000"
                "01000100002904d000000000000c000a00084c3af5f43d7c585b",
            ),
            RecordType.AAAA: DnsPacketData(
                domain="google.com",
                data="93a30120000100000000000106676f6f676c6503636f6d00001c00010000"
                "2904d000000000000c000a0008920d5c0ad5b507cd",
            ),
            RecordType.MX: DnsPacketData(
                domain="google.com",
                data="56680120000100000000000106676f6f676c6503636f6d00000f00010000"
                "2904d000000000000c000a0008e3b66cb8d81a2619",
            ),
            RecordType.SOA: DnsPacketData(
                domain="google.com",
                data="01180120000100000000000106676f6f676c6503636f6d00000600010000"
                "2904d000000000000c000a000882bbbe610424dcac",
            ),
            RecordType.NS: DnsPacketData(
                domain="google.com",
                data="575a0120000100000000000106676f6f676c6503636f6d00000200010000"
                "2904d000000000000c000a0008be8c8f6e44b73029",
            ),
            RecordType.CNAME: DnsPacketData(
                domain="pages.github.com",
                data="b3fa012000010000000000010570616765730667697468756203636f6d00"
                "0005000100002904d000000000000c000a000841279ffbd9123f4a",
            ),
        }
        cls.DNS_RESPONSE_PACKET_FIXTURES: dict[RecordType, DnsPacketData] = {
            RecordType.A: DnsPacketData(
                domain="google.com",
                data="d38d8180000100010000000106676f6f676c6503636f6d0000"
                "010001c00c000100010000008000048efab74e00002904d0000000000000",
            ),
            RecordType.AAAA: DnsPacketData(
                domain="google.com",
                data="a3d38180000100010000000106676f6f676c6503636f6d00001c0001c00c"
                "001c00010000011500102404680040090828000000000000200e00002904"
                "d0000000000000",
            ),
            RecordType.SOA: DnsPacketData(
                domain="google.com",
                data="a61b8180000100010000000106676f6f676c6503636f6d0000060001c00c"
                "000600010000003c0026036e7331c00c09646e732d61646d696ec00c29a5"
                "bf3d0000038400000384000007080000003c00002904d0000000000000",
            ),
            RecordType.MX: DnsPacketData(
                domain="google.com",
                data="b9398180000100010000000106676f6f676c6503636f6d00000f0001c00c"
                "000f00010000012c0009000a04736d7470c00c00002904d0000000000000",
            ),
            RecordType.NS: DnsPacketData(
                domain="google.com",
                data="d9d08180000100040000000106676f6f676c6503636f6d0000020001c00c"
                "0002000100051eb40006036e7333c00cc00c0002000100051eb40006036e"
                "7334c00cc00c0002000100051eb40006036e7331c00cc00c000200010005"
                "1eb40006036e7332c00c00002904d0000000000000",
            ),
            RecordType.CNAME: DnsPacketData(
                domain="pages.github.com",
                data="b3fa818000010001000000010570616765730667697468756203636f6d00"
                "00050001c00c0005000100000e1000120667697468756206676974687562"
                "02696f0000002904d0000000000000",
            ),
        }

    def __get_packet(self, hex_data: str) -> DNSPacket:
        packet_bytes = binascii.unhexlify(hex_data)
        parser = DNSParser(bytearray(packet_bytes))
        return parser.get_dns_packet()

    def test_deserialize_corrupt_query_packet(self):
        query_packet_hex = ""
        query_packet_bytes = binascii.unhexlify(query_packet_hex)
        self.assertRaises(Exception, lambda: DNSParser(bytearray(query_packet_bytes)))

    def test_deserialize_query_packet(self):
        for record_type, dns_packet_data in self.DNS_QUERY_PACKET_FIXTURES.items():
            query_packet_hex = dns_packet_data.data
            query_packet = self.__get_packet(query_packet_hex)
            self.assertIsNotNone(query_packet)
            self.assertIsNotNone(query_packet.header.ID)
            self.assertTrue(query_packet.header.is_query)
            self.assertEqual(query_packet.header.question_count, 1)
            self.assertEqual(query_packet.header.answer_count, 0)
            self.assertIsNotNone(query_packet.questions[0])
            self.assertEqual(query_packet.questions[0].name, dns_packet_data.domain)
            self.assertEqual(query_packet.questions[0].rtype, record_type)
            self.assertEqual(query_packet.questions[0].qclass, RecordClass.IN)

    def test_deserialize_response_packet(self):
        for record_type, dns_packet_data in self.DNS_RESPONSE_PACKET_FIXTURES.items():
            response_packet_hex = dns_packet_data.data
            response_packet = self.__get_packet(response_packet_hex)
            self.assertIsNotNone(response_packet)
            self.assertIsNotNone(response_packet.header.ID)
            self.assertFalse(response_packet.header.is_query)
            self.assertTrue(response_packet.header.answer_count >= 1)
            self.assertTrue(response_packet.header.question_count >= 1)
            answer = response_packet.answers[0]
            self.assertEqual(response_packet.questions[0].name, answer.name)
            self.assertEqual(answer.name, dns_packet_data.domain)
            self.assertEqual(answer.rtype, record_type)
            self.assertTrue(answer.ttl > 0)
            self.assertEqual(answer.rec_class, RecordClass.IN)
            if record_type in (RecordType.A, RecordType.AAAA):
                self.assertIsNotNone(answer.address)
            if record_type == RecordType.CNAME:
                self.assertIsNotNone(answer.cname)
            if record_type == RecordType.MX:
                self.assertIsNotNone(answer.preference)
                self.assertIsNotNone(answer.exchange)
            if record_type == RecordType.NS:
                self.assertIsNotNone(answer.nsdname)
            if record_type == RecordType.SOA:
                self.assertIsNotNone(answer.mname)
                self.assertIsNotNone(answer.rname)
                self.assertIsNotNone(answer.serial)
                self.assertIsNotNone(answer.refresh)
                self.assertIsNotNone(answer.retry)
                self.assertIsNotNone(answer.expire)
                self.assertIsNotNone(answer.minimum)
