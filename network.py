import socket

from dns_packet import DNSPacket
from dns_parser import Parser


def perform_dns_lookup(query_packet: DNSPacket) -> DNSPacket:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", 3000))
    # Connect to google's DNS server
    sock.connect(("8.8.8.8", 53))
    # Create a Query Packet
    packet = Parser.get_bin_query_dns_packet(domain=query_packet.questions[0].name,
                                             record_type=query_packet.questions[0].rtype,
                                             recursion_desired=True)
    # Send the Query Packet
    sock.send(packet)
    # Receive response
    packet_bytes = sock.recv(600)  # Read 600 bytes only for now
    sock.close()
    return Parser(packet_bytes).get_dns_packet()


if __name__ == "__main__":
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", 5000))
    print("Listening on PORT 5000")
    while True:
        received_bytes, address = sock.recvfrom(600)
        received_dns_packet: DNSPacket = Parser(bytearray(received_bytes)).get_dns_packet()

        # Prepare response DNS packet
        response_dns_packet: DNSPacket = DNSPacket()
        response_dns_packet.header.ID = received_dns_packet.header.ID
        response_dns_packet.header.is_recursion_desired = True

        packet = perform_dns_lookup(received_dns_packet)

        response_dns_packet.header.question_count = packet.header.question_count
        response_dns_packet.header.is_recursion_available = packet.header.is_recursion_available
        response_dns_packet.header.answer_count = packet.header.answer_count
        response_dns_packet.header.nameserver_records_count = packet.header.nameserver_records_count
        response_dns_packet.header.additional_records_count = packet.header.additional_records_count

        # TODO: Fix bug in Record -> bytearray conversion code which causes wrong Record lengths to be
        # recorded in binary format
        response_dns_packet.questions.extend(packet.questions)
        response_dns_packet.answers.extend(packet.answers)
        response_dns_packet.nameserver_records.extend(packet.nameserver_records)
        response_dns_packet.additional_records.extend(packet.additional_records)
        sock.sendto(response_dns_packet.to_bin(), address)
