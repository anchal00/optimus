import binascii
import ipaddress
import unittest

from optimus.dns.models.records import RecordClass, RecordType
from optimus.dns.parser.parse import DNSParser


class TestDnsParser(unittest.TestCase):

    @classmethod
    def setUpClass(cls): ...

    def test_deserialize_query_packet(self):
        query_packet_hex = (
            "22a90120000100000000000106676f6f676c6503636f6d000"
            + "001000100002904d000000000000c000a00084c3af5f43d7c585b"
        )
        query_packet_bytes = binascii.unhexlify(query_packet_hex)
        parser = DNSParser(bytearray(query_packet_bytes))
        query_packet = parser.get_dns_packet()
        self.assertIsNotNone(query_packet)
        self.assertIsNotNone(query_packet.header.ID)
        self.assertTrue(query_packet.header.is_query)
        self.assertEqual(query_packet.header.question_count, 1)
        self.assertEqual(query_packet.header.answer_count, 0)
        self.assertIsNotNone(query_packet.questions[0])
        self.assertEqual(query_packet.questions[0].name, "google.com")
        self.assertEqual(query_packet.questions[0].rtype, RecordType.A)
        self.assertEqual(query_packet.questions[0].qclass, RecordClass.IN)

    def test_deserialize_corrupt_query_packet(self):
        query_packet_hex = ""
        query_packet_bytes = binascii.unhexlify(query_packet_hex)
        self.assertRaises(Exception, lambda: DNSParser(bytearray(query_packet_bytes)))

    def test_deserialize_answer_packet(self):
        answer_packet_hex = (
            "d38d8180000100010000000106676f6f676c6503636f6d0000010001c00c"
            + "000100010000008000048efab74e00002904d0000000000000"
        )
        answer_packet_bin = binascii.unhexlify(answer_packet_hex)
        parser = DNSParser(bytearray(answer_packet_bin))
        answer_packet = parser.get_dns_packet()
        self.assertIsNotNone(answer_packet)
        self.assertIsNotNone(answer_packet.header.ID)
        self.assertFalse(answer_packet.header.is_query)
        self.assertTrue(answer_packet.header.answer_count == 1)
        self.assertTrue(answer_packet.header.question_count == 1)
        answer = answer_packet.answers[0]
        self.assertEqual(answer_packet.questions[0].name, answer.name)
        self.assertEqual(answer.name, "google.com")
        self.assertEqual(answer.rtype, RecordType.A)
        self.assertEqual(answer.rec_class, RecordClass.IN)
        self.assertIsNotNone(answer.address)
        self.assertEqual(answer.address, ipaddress.ip_address("142.250.183.78"))
